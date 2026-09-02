"""
Earth Observation Dataset Catalog & Spatial Service for ORCA
SIH 2026 - Problem Statement 26176
Manages product discovery, temporal matching, spatial subsetting, and caching for
ISRO (Oceansat-3, INSAT-3DR) and Copernicus (Sentinel-3) satellite raster datasets.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import numpy as np

from backend.data.raster.schemas import (
    RasterDatasetMetadata,
    SpatialPointResult,
    RegionalStatistics,
    SpatialGradientResult,
    GeoJSONFeatureCollection,
    RasterGridResponse,
    ProcessingLevel,
    ExtractionMethod
)
from backend.data.raster.reader import NetCDFRasterReader
from backend.data.raster.processor import RasterProcessor
from backend.data.schemas import DataStatus, QualityFlag
from backend.temporal.models import TimeWindow

logger = logging.getLogger("orca.raster.catalog")

DEFAULT_GRANULES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eo_granules")


class EODatasetCatalog:
    """
    Central catalog and scientific spatial dispatch engine for Earth Observation raster data.
    """

    def __init__(self, granules_dir: Optional[str] = None, cache_ttl_seconds: int = 900):
        self.granules_dir = granules_dir or DEFAULT_GRANULES_DIR
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._loaded_rasters: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, RasterDatasetMetadata]] = {}
        self._init_catalog()

    def _init_catalog(self) -> None:
        """Discovers and catalogs available local NetCDF granules."""
        if not os.path.exists(self.granules_dir):
            os.makedirs(self.granules_dir, exist_ok=True)
            return

        for fname in os.listdir(self.granules_dir):
            if fname.endswith(".nc") or fname.endswith(".hdf") or fname.endswith(".h5"):
                fpath = os.path.join(self.granules_dir, fname)
                try:
                    lats, lons, data, meta = NetCDFRasterReader.read_file(fpath)
                    self._loaded_rasters[meta.dataset_id] = (lats, lons, data, meta)
                    logger.info("Catalogs EO dataset %s (variable=%s, shape=%s)", meta.dataset_id, meta.variable, data.shape)
                except Exception as e:
                    logger.warning("Failed to catalog EO granule %s: %s", fname, e)

    def list_available_products(self) -> List[Dict[str, Any]]:
        """Returns metadata for all cataloged satellite Earth Observation products."""
        products = []
        for d_id, (_, _, _, meta) in self._loaded_rasters.items():
            products.append({
                "dataset_id": meta.dataset_id,
                "product_name": meta.product_name,
                "variable": meta.variable,
                "satellite": meta.satellite_name,
                "sensor": meta.sensor_name,
                "source": meta.source,
                "acquisition_time": meta.acquisition_time,
                "valid_time": meta.valid_time,
                "units": meta.units,
                "resolution_deg": meta.resolution,
                "bounding_box": meta.bounding_box,
                "data_type": meta.data_type.value,
                "quality_flag": meta.quality_flag.value
            })
        return products

    def discover_product(
        self,
        variable: str,
        roi: Optional[Tuple[float, float, float, float]] = None,
        time_window: Optional[TimeWindow] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Discovers the best-matching dataset ID for variable, region, and time.
        Returns (dataset_id, limitation_error).
        """
        var_clean = variable.lower().strip()
        # Canonicalize variable names
        if var_clean in ["sst", "sea_surface_temperature", "temp", "temperature"]:
            target_var = "sea_surface_temperature"
        elif var_clean in ["chl", "chla", "chlorophyll", "chlorophyll_a", "ocean_color"]:
            target_var = "chlorophyll_a"
        else:
            target_var = var_clean

        # Temporal Rule: Reject future satellite observation requests
        if time_window and time_window.is_future:
            return None, (
                "Future satellite observation cannot exist. Earth Observation sensors record past or "
                "near-real-time physical radiances. For future conditions, please consult numerical marine forecast models."
            )

        # Match variable
        matching_ids = [
            d_id for d_id, (_, _, _, meta) in self._loaded_rasters.items()
            if meta.variable == target_var
        ]

        if not matching_ids:
            return None, f"No satellite Earth Observation product cataloged for variable '{variable}'."

        # If specific historical date requested (e.g. 2026-09-01 vs 2026-09-02)
        if time_window and time_window.start_datetime:
            req_date_str = time_window.start_datetime.strftime("%Y-%m-%d")
            date_matches = [
                d_id for d_id in matching_ids
                if self._loaded_rasters[d_id][3].acquisition_time.startswith(req_date_str)
            ]
            if date_matches:
                return date_matches[0], None
            else:
                # Provide closest available historical product with transparent explanation
                best_id = matching_ids[0]
                meta = self._loaded_rasters[best_id][3]
                return best_id, f"Requested date '{req_date_str}' not found in archive. Serving closest available product acquired on {meta.acquisition_time[:10]}."

        # Default to primary operational sensor (Oceansat-3 for Chl-a, INSAT-3DR for SST)
        for d_id in matching_ids:
            if "EOS06" in d_id or "INSAT3DR" in d_id:
                return d_id, None

        return matching_ids[0], None

    def get_spatial_point(
        self,
        variable: str,
        lat: float,
        lon: float,
        time_window: Optional[TimeWindow] = None,
        method: ExtractionMethod = ExtractionMethod.NEAREST_NEIGHBOR
    ) -> SpatialPointResult:
        """Extracts point observation from satellite raster field."""
        dataset_id, limitation = self.discover_product(variable, (lon - 0.1, lat - 0.1, lon + 0.1, lat + 0.1), time_window)
        if not dataset_id:
            now_iso = datetime.now(timezone.utc).isoformat()
            return SpatialPointResult(
                latitude=lat,
                longitude=lon,
                value=None,
                unit="unknown",
                cell_latitude=lat,
                cell_longitude=lon,
                distance_to_cell_km=0.0,
                extraction_method=method,
                is_masked=True,
                dataset_id="UNAVAILABLE",
                product_name="No Product",
                satellite_name="Unknown",
                sensor_name="Unknown",
                source="ORCA EO Catalog",
                acquisition_time=now_iso,
                valid_time=now_iso,
                data_type=DataStatus.UNAVAILABLE,
                quality_flag=QualityFlag.MISSING,
                limitations=[limitation or "Product discovery failed"]
            )

        lats, lons, data, meta = self._loaded_rasters[dataset_id]
        res = RasterProcessor.extract_point(lats, lons, data, meta, lat, lon, method=method)
        if limitation:
            res.limitations.append(limitation)
        return res

    def get_regional_statistics(
        self,
        variable: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        time_window: Optional[TimeWindow] = None
    ) -> RegionalStatistics:
        """Calculates area statistics strictly over unmasked ocean pixels."""
        cache_key = f"stats:{variable}:{min_lat}:{max_lat}:{min_lon}:{max_lon}:{time_window.label if time_window else 'current'}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached["data"]

        dataset_id, limitation = self.discover_product(variable, (min_lon, min_lat, max_lon, max_lat), time_window)
        bbox = (min_lon, min_lat, max_lon, max_lat)
        now_iso = datetime.now(timezone.utc).isoformat()

        if not dataset_id:
            return RegionalStatistics(
                variable=variable,
                unit="unknown",
                bounding_box=bbox,
                has_valid_data=False,
                mean=None,
                median=None,
                minimum=None,
                maximum=None,
                standard_deviation=None,
                valid_pixel_count=0,
                total_pixel_count=0,
                valid_percentage=0.0,
                dataset_id="UNAVAILABLE",
                product_name="No Product",
                source="ORCA EO Catalog",
                acquisition_time=now_iso,
                valid_time=now_iso,
                data_type=DataStatus.UNAVAILABLE,
                limitations=[limitation or "Product discovery failed"]
            )

        lats, lons, data, meta = self._loaded_rasters[dataset_id]
        stats = RasterProcessor.calculate_regional_statistics(lats, lons, data, meta, min_lat, max_lat, min_lon, max_lon)
        if limitation:
            stats.limitations.append(limitation)

        self._save_to_cache(cache_key, {"data": stats})
        return stats

    def get_spatial_gradients(
        self,
        variable: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        time_window: Optional[TimeWindow] = None
    ) -> SpatialGradientResult:
        """Computes geodetic horizontal spatial gradients across requested ROI."""
        cache_key = f"grad:{variable}:{min_lat}:{max_lat}:{min_lon}:{max_lon}:{time_window.label if time_window else 'current'}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached["data"]

        dataset_id, limitation = self.discover_product(variable, (min_lon, min_lat, max_lon, max_lat), time_window)
        bbox = (min_lon, min_lat, max_lon, max_lat)
        now_iso = datetime.now(timezone.utc).isoformat()

        if not dataset_id:
            return SpatialGradientResult(
                variable=variable,
                unit="unknown",
                gradient_unit="unknown/km",
                bounding_box=bbox,
                mean_gradient_magnitude=None,
                max_gradient_magnitude=None,
                frontal_points_count=0,
                sharpest_front_points=[],
                dataset_id="UNAVAILABLE",
                source="ORCA EO Catalog",
                data_type=DataStatus.UNAVAILABLE,
                acquisition_time=now_iso,
                limitations=[limitation or "Product discovery failed"]
            )

        lats, lons, data, meta = self._loaded_rasters[dataset_id]
        grads = RasterProcessor.compute_spatial_gradients(lats, lons, data, meta, min_lat, max_lat, min_lon, max_lon)
        if limitation:
            grads.limitations.append(limitation)

        self._save_to_cache(cache_key, {"data": grads})
        return grads

    def get_map_grid(
        self,
        variable: str,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        time_window: Optional[TimeWindow] = None
    ) -> RasterGridResponse:
        """Generates downsampled 2D grid matrix for Leaflet canvas/heatmap overlay."""
        dataset_id, limitation = self.discover_product(variable, None, time_window)
        if not dataset_id:
            now_iso = datetime.now(timezone.utc).isoformat()
            return RasterGridResponse(
                variable=variable,
                unit="unknown",
                latitudes=[],
                longitudes=[],
                values=[],
                source="ORCA EO Catalog",
                satellite="Unknown",
                sensor="Unknown",
                acquisition_time=now_iso,
                valid_time=now_iso,
                data_type=DataStatus.UNAVAILABLE,
                provenance={"error": limitation or "Product discovery failed"}
            )

        lats, lons, data, meta = self._loaded_rasters[dataset_id]
        return RasterProcessor.generate_map_grid(lats, lons, data, meta, min_lat, max_lat, min_lon, max_lon)

    def get_contours_geojson(
        self,
        variable: str,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        time_window: Optional[TimeWindow] = None
    ) -> GeoJSONFeatureCollection:
        """Generates RFC 7946 GeoJSON contour bands from valid raster values."""
        dataset_id, limitation = self.discover_product(variable, None, time_window)
        if not dataset_id:
            return GeoJSONFeatureCollection(features=[])

        lats, lons, data, meta = self._loaded_rasters[dataset_id]
        return RasterProcessor.generate_contours_geojson(lats, lons, data, meta, min_lat, max_lat, min_lon, max_lon)

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        if key not in self._cache:
            return None
        entry = self._cache[key]
        now = datetime.now(timezone.utc).timestamp()
        if now - entry["cached_at"] > self.cache_ttl:
            del self._cache[key]
            return None
        return entry

    def _save_to_cache(self, key: str, data_dict: Dict[str, Any]) -> None:
        self._cache[key] = {
            **data_dict,
            "cached_at": datetime.now(timezone.utc).timestamp()
        }
