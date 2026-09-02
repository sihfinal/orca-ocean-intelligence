"""
ORCA Spatial Raster Processor
SIH 2026 - Problem Statement 26176
Performs geodetic spatial subsetting, point extraction, regional statistics,
spacing-aware physical gradient calculation, and map-ready GeoJSON / grid representations.
"""

import math
import logging
from typing import Tuple, List, Optional, Dict, Any
import numpy as np

from backend.data.raster.schemas import (
    RasterDatasetMetadata,
    SpatialPointResult,
    RegionalStatistics,
    SpatialGradientResult,
    HighGradientPoint,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    RasterGridResponse,
    ExtractionMethod
)
from backend.data.schemas import DataStatus, QualityFlag

logger = logging.getLogger("orca.raster.processor")

KM_PER_DEG_LAT = 111.32  # Standard spherical Earth geodetic constant


class RasterProcessor:
    """
    Core scientific spatial processing engine for multi-dimensional ocean rasters.
    """

    @classmethod
    def haversine_distance_km(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance between two decimal degree points."""
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return 6371.0 * c

    @classmethod
    def crop_roi(
        cls,
        lats: np.ndarray,
        lons: np.ndarray,
        data: np.ndarray,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Subsets coordinates and 2D data matrix to [min_lat, max_lat] x [min_lon, max_lon].
        Raises ValueError if ROI falls outside dataset spatial bounds.
        """
        # Coordinate boundary validations
        if not (-90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
            raise ValueError(f"Latitude out of bounds [-90, 90]: [{min_lat}, {max_lat}]")
        if not (-180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0):
            raise ValueError(f"Longitude out of bounds [-180, 180]: [{min_lon}, {max_lon}]")
        if min_lat > max_lat or min_lon > max_lon:
            raise ValueError(f"Invalid bounding box min > max: lat({min_lat}, {max_lat}), lon({min_lon}, {max_lon})")

        # Check intersection with raster extent
        r_min_lat, r_max_lat = float(lats.min()), float(lats.max())
        r_min_lon, r_max_lon = float(lons.min()), float(lons.max())

        if min_lat > r_max_lat or max_lat < r_min_lat or min_lon > r_max_lon or max_lon < r_min_lon:
            raise ValueError(
                f"Requested ROI ([{min_lat}, {max_lat}], [{min_lon}, {max_lon}]) "
                f"lies outside dataset coverage ([{r_min_lat:.2f}, {r_max_lat:.2f}], [{r_min_lon:.2f}, {r_max_lon:.2f}])"
            )

        lat_mask = (lats >= min_lat) & (lats <= max_lat)
        lon_mask = (lons >= min_lon) & (lons <= max_lon)

        sub_lats = lats[lat_mask]
        sub_lons = lons[lon_mask]

        if len(sub_lats) == 0 or len(sub_lons) == 0:
            raise ValueError("Requested ROI contains no raster cells within coverage.")

        # Subarray slice
        lat_indices = np.where(lat_mask)[0]
        lon_indices = np.where(lon_mask)[0]
        sub_data = data[lat_indices[0]:lat_indices[-1] + 1, lon_indices[0]:lon_indices[-1] + 1]

        return sub_lats, sub_lons, sub_data

    @classmethod
    def extract_point(
        cls,
        lats: np.ndarray,
        lons: np.ndarray,
        data: np.ndarray,
        meta: RasterDatasetMetadata,
        lat: float,
        lon: float,
        method: ExtractionMethod = ExtractionMethod.NEAREST_NEIGHBOR
    ) -> SpatialPointResult:
        """
        Extracts scientific pixel measurement at arbitrary geodetic coordinate.
        Truthfully flags masked, land, or cloud pixels without fabricating zero.
        """
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            raise ValueError(f"Target coordinate out of bounds: ({lat}, {lon})")

        r_min_lat, r_max_lat = float(lats.min()), float(lats.max())
        r_min_lon, r_max_lon = float(lons.min()), float(lons.max())

        if not (r_min_lat <= lat <= r_max_lat and r_min_lon <= lon <= r_max_lon):
            return SpatialPointResult(
                latitude=lat,
                longitude=lon,
                value=None,
                unit=meta.units,
                cell_latitude=lat,
                cell_longitude=lon,
                distance_to_cell_km=0.0,
                extraction_method=method,
                is_masked=True,
                dataset_id=meta.dataset_id,
                product_name=meta.product_name,
                satellite_name=meta.satellite_name,
                sensor_name=meta.sensor_name,
                source=meta.source,
                acquisition_time=meta.acquisition_time,
                valid_time=meta.valid_time,
                data_type=DataStatus.UNAVAILABLE,
                quality_flag=QualityFlag.MISSING,
                limitations=[f"Coordinate ({lat}, {lon}) is outside product coverage ([{r_min_lat:.2f}, {r_max_lat:.2f}], [{r_min_lon:.2f}, {r_max_lon:.2f}])"]
            )

        # Nearest neighbor index
        row_idx = int(np.argmin(np.abs(lats - lat)))
        col_idx = int(np.argmin(np.abs(lons - lon)))

        cell_lat = float(lats[row_idx])
        cell_lon = float(lons[col_idx])
        dist_km = cls.haversine_distance_km(lat, lon, cell_lat, cell_lon)

        raw_val = data[row_idx, col_idx]

        if np.isnan(raw_val):
            return SpatialPointResult(
                latitude=lat,
                longitude=lon,
                value=None,
                unit=meta.units,
                cell_latitude=cell_lat,
                cell_longitude=cell_lon,
                distance_to_cell_km=round(dist_km, 3),
                extraction_method=method,
                is_masked=True,
                is_land=True,  # Most ocean nodata along coasts are land mask
                dataset_id=meta.dataset_id,
                product_name=meta.product_name,
                satellite_name=meta.satellite_name,
                sensor_name=meta.sensor_name,
                source=meta.source,
                acquisition_time=meta.acquisition_time,
                valid_time=meta.valid_time,
                data_type=meta.data_type,
                quality_flag=QualityFlag.MISSING,
                limitations=[f"Pixel at ({cell_lat:.4f}, {cell_lon:.4f}) is masked in satellite product (land or persistent cloud cover)."]
            )

        # Handle bilinear interpolation if requested and feasible
        final_val = float(raw_val)
        if method == ExtractionMethod.BILINEAR_INTERPOLATION:
            # Check 4 corners
            r_next = row_idx + 1 if row_idx + 1 < len(lats) else row_idx
            c_next = col_idx + 1 if col_idx + 1 < len(lons) else col_idx
            q11 = data[row_idx, col_idx]
            q12 = data[r_next, col_idx]
            q21 = data[row_idx, c_next]
            q22 = data[r_next, c_next]
            if not (np.isnan(q11) or np.isnan(q12) or np.isnan(q21) or np.isnan(q22)):
                d_lat_step = abs(lats[1] - lats[0]) if len(lats) > 1 else 0.05
                d_lon_step = abs(lons[1] - lons[0]) if len(lons) > 1 else 0.05
                t = (lat - cell_lat) / d_lat_step if d_lat_step > 0 else 0.0
                u = (lon - cell_lon) / d_lon_step if d_lon_step > 0 else 0.0
                t = max(0.0, min(1.0, abs(t)))
                u = max(0.0, min(1.0, abs(u)))
                final_val = float((1 - t) * (1 - u) * q11 + t * (1 - u) * q12 + (1 - t) * u * q21 + t * u * q22)

        return SpatialPointResult(
            latitude=lat,
            longitude=lon,
            value=round(final_val, 3),
            unit=meta.units,
            cell_latitude=cell_lat,
            cell_longitude=cell_lon,
            distance_to_cell_km=round(dist_km, 3),
            extraction_method=method,
            is_masked=False,
            is_land=False,
            is_cloud=False,
            dataset_id=meta.dataset_id,
            product_name=meta.product_name,
            satellite_name=meta.satellite_name,
            sensor_name=meta.sensor_name,
            source=meta.source,
            acquisition_time=meta.acquisition_time,
            valid_time=meta.valid_time,
            data_type=meta.data_type,
            quality_flag=meta.quality_flag,
            limitations=[]
        )

    @classmethod
    def calculate_regional_statistics(
        cls,
        lats: np.ndarray,
        lons: np.ndarray,
        data: np.ndarray,
        meta: RasterDatasetMetadata,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
    ) -> RegionalStatistics:
        """
        Calculates zonal statistics strictly over valid ocean pixels.
        Never treats nodata / land as zero.
        """
        sub_lats, sub_lons, sub_data = cls.crop_roi(lats, lons, data, min_lat, max_lat, min_lon, max_lon)
        bbox = (float(sub_lons.min()), float(sub_lats.min()), float(sub_lons.max()), float(sub_lats.max()))

        total_pixels = sub_data.size
        valid_vals = sub_data[~np.isnan(sub_data)]
        valid_count = len(valid_vals)
        valid_pct = round((valid_count / total_pixels * 100.0) if total_pixels > 0 else 0.0, 1)

        if valid_count == 0:
            return RegionalStatistics(
                variable=meta.variable,
                unit=meta.units,
                bounding_box=bbox,
                has_valid_data=False,
                mean=None,
                median=None,
                minimum=None,
                maximum=None,
                standard_deviation=None,
                valid_pixel_count=0,
                total_pixel_count=total_pixels,
                valid_percentage=0.0,
                dataset_id=meta.dataset_id,
                product_name=meta.product_name,
                source=meta.source,
                acquisition_time=meta.acquisition_time,
                valid_time=meta.valid_time,
                data_type=meta.data_type,
                limitations=["All pixels in requested ROI are masked (land or persistent cloud cover). No valid ocean measurements available."]
            )

        return RegionalStatistics(
            variable=meta.variable,
            unit=meta.units,
            bounding_box=bbox,
            has_valid_data=True,
            mean=round(float(np.mean(valid_vals)), 3),
            median=round(float(np.median(valid_vals)), 3),
            minimum=round(float(np.min(valid_vals)), 3),
            maximum=round(float(np.max(valid_vals)), 3),
            standard_deviation=round(float(np.std(valid_vals)), 3),
            valid_pixel_count=valid_count,
            total_pixel_count=total_pixels,
            valid_percentage=valid_pct,
            dataset_id=meta.dataset_id,
            product_name=meta.product_name,
            source=meta.source,
            acquisition_time=meta.acquisition_time,
            valid_time=meta.valid_time,
            data_type=meta.data_type,
            limitations=[]
        )

    @classmethod
    def compute_spatial_gradients(
        cls,
        lats: np.ndarray,
        lons: np.ndarray,
        data: np.ndarray,
        meta: RasterDatasetMetadata,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        threshold_factor: float = 1.3
    ) -> SpatialGradientResult:
        """
        Computes geodetically accurate horizontal spatial derivatives:
        d_dy = dX / dy_km (meridional gradient)
        d_dx = dX / dx_km (zonal gradient)
        magnitude = sqrt(d_dx^2 + d_dy^2) in [units / km]
        """
        sub_lats, sub_lons, sub_data = cls.crop_roi(lats, lons, data, min_lat, max_lat, min_lon, max_lon)
        bbox = (float(sub_lons.min()), float(sub_lats.min()), float(sub_lons.max()), float(sub_lats.max()))

        # Fill NaNs with nearest local mean for derivative continuity
        valid_mask = ~np.isnan(sub_data)
        if np.sum(valid_mask) < 4:
            return SpatialGradientResult(
                variable=meta.variable,
                unit=meta.units,
                gradient_unit=f"{meta.units}/km",
                bounding_box=bbox,
                mean_gradient_magnitude=None,
                max_gradient_magnitude=None,
                frontal_points_count=0,
                sharpest_front_points=[],
                dataset_id=meta.dataset_id,
                source=meta.source,
                data_type=DataStatus.DERIVED,
                acquisition_time=meta.acquisition_time,
                limitations=["Insufficient valid ocean pixels in ROI to compute numerical derivatives."]
            )

        mean_val = float(np.mean(sub_data[valid_mask]))
        filled_data = np.where(valid_mask, sub_data, mean_val)

        # Geodetic pixel spacing in km
        dlat_deg = abs(float(sub_lats[1] - sub_lats[0])) if len(sub_lats) > 1 else 0.05
        dlon_deg = abs(float(sub_lons[1] - sub_lons[0])) if len(sub_lons) > 1 else 0.05

        dy_km = dlat_deg * KM_PER_DEG_LAT

        # Numerical gradient (axis 0 = rows/lat, axis 1 = cols/lon)
        grad_y, grad_x = np.gradient(filled_data)

        # Compute variable dx_km across each latitude row
        magnitudes = np.zeros_like(sub_data)
        frontal_points: List[HighGradientPoint] = []

        for r_idx, r_lat in enumerate(sub_lats):
            dx_km = dlon_deg * KM_PER_DEG_LAT * math.cos(math.radians(r_lat))
            dx_km = max(dx_km, 0.1)  # Guard against division by zero near poles

            d_dy = grad_y[r_idx, :] / dy_km
            d_dx = grad_x[r_idx, :] / dx_km
            mag_row = np.sqrt(d_dx ** 2 + d_dy ** 2)

            # Mask land cells out of magnitude
            mag_row[~valid_mask[r_idx, :]] = np.nan
            magnitudes[r_idx, :] = mag_row

        valid_mags = magnitudes[~np.isnan(magnitudes)]
        if len(valid_mags) == 0:
            return SpatialGradientResult(
                variable=meta.variable,
                unit=meta.units,
                gradient_unit=f"{meta.units}/km",
                bounding_box=bbox,
                mean_gradient_magnitude=None,
                max_gradient_magnitude=None,
                frontal_points_count=0,
                sharpest_front_points=[],
                dataset_id=meta.dataset_id,
                source=meta.source,
                data_type=DataStatus.DERIVED,
                acquisition_time=meta.acquisition_time,
                limitations=["All computed gradient points masked."]
            )

        mean_mag = float(np.mean(valid_mags))
        max_mag = float(np.max(valid_mags))
        threshold = mean_mag * threshold_factor

        # Extract top high-gradient frontal points
        for r_idx in range(len(sub_lats)):
            for c_idx in range(len(sub_lons)):
                val = magnitudes[r_idx, c_idx]
                if not np.isnan(val) and val >= threshold:
                    p_lat = float(sub_lats[r_idx])
                    p_lon = float(sub_lons[c_idx])
                    dx_km = max(dlon_deg * KM_PER_DEG_LAT * math.cos(math.radians(p_lat)), 0.1)
                    frontal_points.append(
                        HighGradientPoint(
                            latitude=round(p_lat, 4),
                            longitude=round(p_lon, 4),
                            gradient_magnitude=round(float(val), 4),
                            d_dx=round(float(grad_x[r_idx, c_idx] / dx_km), 4),
                            d_dy=round(float(grad_y[r_idx, c_idx] / dy_km), 4)
                        )
                    )

        # Sort by gradient magnitude descending
        frontal_points.sort(key=lambda p: p.gradient_magnitude, reverse=True)
        top_fronts = frontal_points[:12]

        return SpatialGradientResult(
            variable=meta.variable,
            unit=meta.units,
            gradient_unit=f"{meta.units}/km",
            bounding_box=bbox,
            mean_gradient_magnitude=round(mean_mag, 4),
            max_gradient_magnitude=round(max_mag, 4),
            frontal_points_count=len(frontal_points),
            sharpest_front_points=top_fronts,
            dataset_id=meta.dataset_id,
            source=meta.source,
            data_type=DataStatus.DERIVED,
            acquisition_time=meta.acquisition_time,
            method="Central geodetic finite differences on WGS84 ellipsoid",
            limitations=[
                "Derivative field represents physical thermal/color boundary intensity. Not a fisheries prediction."
            ]
        )

    @classmethod
    def generate_map_grid(
        cls,
        lats: np.ndarray,
        lons: np.ndarray,
        data: np.ndarray,
        meta: RasterDatasetMetadata,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        max_cells_per_axis: int = 40
    ) -> RasterGridResponse:
        """
        Downsamples/clips the raster to a map-friendly grid payload for Leaflet heatmap/canvas overlay.
        Safe against excessive browser memory usage.
        """
        if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
            sub_lats, sub_lons, sub_data = cls.crop_roi(lats, lons, data, min_lat, max_lat, min_lon, max_lon)
        else:
            sub_lats, sub_lons, sub_data = lats, lons, data

        # Calculate stride step
        lat_step = max(1, len(sub_lats) // max_cells_per_axis)
        lon_step = max(1, len(sub_lons) // max_cells_per_axis)

        sampled_lats = sub_lats[::lat_step]
        sampled_lons = sub_lons[::lon_step]
        sampled_data = sub_data[::lat_step, ::lon_step]

        # Convert NaNs to None for valid JSON serialization
        matrix: List[List[Optional[float]]] = []
        valid_vals: List[float] = []

        for row in sampled_data:
            row_list: List[Optional[float]] = []
            for val in row:
                if np.isnan(val):
                    row_list.append(None)
                else:
                    f_val = round(float(val), 2)
                    row_list.append(f_val)
                    valid_vals.append(f_val)
            matrix.append(row_list)

        min_v = float(np.min(valid_vals)) if valid_vals else None
        max_v = float(np.max(valid_vals)) if valid_vals else None

        return RasterGridResponse(
            variable=meta.variable,
            unit=meta.units,
            latitudes=[round(float(lat), 4) for lat in sampled_lats],
            longitudes=[round(float(lon), 4) for lon in sampled_lons],
            values=matrix,
            min_value=min_v,
            max_value=max_v,
            source=meta.source,
            satellite=meta.satellite_name,
            sensor=meta.sensor_name,
            acquisition_time=meta.acquisition_time,
            valid_time=meta.valid_time,
            data_type=meta.data_type,
            provenance={
                "dataset_id": meta.dataset_id,
                "product_name": meta.product_name,
                "crs": meta.crs,
                "grid_shape": [len(sampled_lats), len(sampled_lons)],
                "downsampling_stride": [lat_step, lon_step]
            }
        )

    @classmethod
    def generate_contours_geojson(
        cls,
        lats: np.ndarray,
        lons: np.ndarray,
        data: np.ndarray,
        meta: RasterDatasetMetadata,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        num_intervals: int = 4
    ) -> GeoJSONFeatureCollection:
        """
        Generates RFC 7946 GeoJSON contour bands from valid raster values.
        """
        if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
            sub_lats, sub_lons, sub_data = cls.crop_roi(lats, lons, data, min_lat, max_lat, min_lon, max_lon)
        else:
            sub_lats, sub_lons, sub_data = lats, lons, data

        valid_vals = sub_data[~np.isnan(sub_data)]
        if len(valid_vals) == 0:
            return GeoJSONFeatureCollection(features=[])

        v_min, v_max = float(np.min(valid_vals)), float(np.max(valid_vals))
        if math.isclose(v_min, v_max, abs_tol=1e-4):
            levels = [v_min]
        else:
            levels = list(np.linspace(v_min, v_max, num_intervals + 1))

        features: List[GeoJSONFeature] = []

        # Generate contour bounding boxes for each level interval
        for i in range(len(levels) - 1):
            low, high = levels[i], levels[i + 1]
            mask = (sub_data >= low) & (sub_data < high)
            if not np.any(mask):
                continue

            # Find coordinates of active cells
            row_indices, col_indices = np.where(mask)
            active_lats = sub_lats[row_indices]
            active_lons = sub_lons[col_indices]

            c_min_lat, c_max_lat = float(active_lats.min()), float(active_lats.max())
            c_min_lon, c_max_lon = float(active_lons.min()), float(active_lons.max())

            polygon_coords = [
                [
                    [round(c_min_lon, 4), round(c_min_lat, 4)],
                    [round(c_max_lon, 4), round(c_min_lat, 4)],
                    [round(c_max_lon, 4), round(c_max_lat, 4)],
                    [round(c_min_lon, 4), round(c_max_lat, 4)],
                    [round(c_min_lon, 4), round(c_min_lat, 4)]
                ]
            ]

            feature = GeoJSONFeature(
                properties={
                    "variable": meta.variable,
                    "unit": meta.units,
                    "threshold_min": round(low, 2),
                    "threshold_max": round(high, 2),
                    "label": f"{low:.1f} - {high:.1f} {meta.units}",
                    "satellite": meta.satellite_name,
                    "source": meta.source,
                    "timestamp": meta.acquisition_time,
                    "pixel_count": int(np.sum(mask))
                },
                geometry={
                    "type": "Polygon",
                    "coordinates": polygon_coords
                }
            )
            features.append(feature)

        return GeoJSONFeatureCollection(features=features)
