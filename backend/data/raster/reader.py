"""
NetCDF & HDF5 Scientific Raster Reader for ORCA
SIH 2026 - Problem Statement 26176
Provides robust, CF-compliant spatial raster ingestion with coordinate normalization,
orientation checks (descending latitude inversion, 0-360 to -180-180 longitude conversion),
nodata/quality masking, and metadata preservation.
"""

import os
import logging
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime, timezone
import numpy as np
import netCDF4 as nc

from backend.data.raster.schemas import (
    RasterDatasetMetadata,
    ProcessingLevel
)
from backend.data.schemas import DataStatus, QualityFlag

logger = logging.getLogger("orca.raster.reader")


class NetCDFRasterReader:
    """
    Standardized reader for Earth Observation raster datasets in NetCDF-4 / HDF5 format.
    Ensures spatial consistency and coordinate adherence to EPSG:4326.
    """

    LAT_CANDIDATES = ["lat", "latitude", "LAT", "Latitude", "nav_lat", "y"]
    LON_CANDIDATES = ["lon", "longitude", "LON", "Longitude", "nav_lon", "x"]
    TIME_CANDIDATES = ["time", "TIME", "Time"]

    @classmethod
    def read_file(
        cls,
        file_path: str,
        variable_name: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, RasterDatasetMetadata]:
        """
        Reads a NetCDF file and returns (lats, lons, data_2d, metadata).
        Coordinates are normalized to ascending order in EPSG:4326.
        Masked/nodata values are returned as np.nan.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"NetCDF file not found: {file_path}")

        try:
            ds = nc.Dataset(file_path, "r")
        except Exception as e:
            logger.error("Failed to parse NetCDF file %s: %s", file_path, e)
            raise ValueError(f"Corrupt or unreadable NetCDF dataset: {e}")

        try:
            # 1. Identify Latitude coordinate variable
            lat_var_name = cls._find_coord_var(ds, cls.LAT_CANDIDATES)
            if not lat_var_name:
                raise ValueError(f"No latitude coordinate variable found in {list(ds.variables.keys())}")
            raw_lats = np.array(ds.variables[lat_var_name][:], dtype=float)

            # 2. Identify Longitude coordinate variable
            lon_var_name = cls._find_coord_var(ds, cls.LON_CANDIDATES)
            if not lon_var_name:
                raise ValueError(f"No longitude coordinate variable found in {list(ds.variables.keys())}")
            raw_lons = np.array(ds.variables[lon_var_name][:], dtype=float)

            # Flatten to 1D if stored as 2D meshgrid
            if raw_lats.ndim == 2:
                raw_lats = raw_lats[:, 0]
            if raw_lons.ndim == 2:
                raw_lons = raw_lons[0, :]

            # 3. Identify Target Data Variable
            if not variable_name:
                # Pick first variable that isn't a coordinate
                coord_names = {lat_var_name, lon_var_name, "time", "crs", "lat_bnds", "lon_bnds"}
                data_vars = [v for v in ds.variables.keys() if v not in coord_names]
                if not data_vars:
                    raise ValueError(f"No data variables found in {file_path}")
                variable_name = data_vars[0]

            if variable_name not in ds.variables:
                raise ValueError(f"Variable '{variable_name}' not found. Available: {list(ds.variables.keys())}")

            var_obj = ds.variables[variable_name]
            raw_data = var_obj[:]

            # Squeeze dimensions if 3D (time, lat, lon) or 4D
            if raw_data.ndim > 2:
                raw_data = np.squeeze(raw_data)
                if raw_data.ndim > 2:
                    # Take first temporal/depth slice if still > 2D
                    raw_data = raw_data[0]

            # Convert numpy MaskedArray or nodata to np.nan
            if isinstance(raw_data, np.ma.MaskedArray):
                data_2d = raw_data.filled(np.nan).astype(float)
            else:
                data_2d = np.array(raw_data, dtype=float)

            # Check explicit nodata / _FillValue
            fill_val = getattr(var_obj, "_FillValue", None)
            miss_val = getattr(var_obj, "missing_value", None)
            if fill_val is not None:
                data_2d[np.isclose(data_2d, fill_val, atol=1e-3)] = np.nan
            if miss_val is not None:
                data_2d[np.isclose(data_2d, miss_val, atol=1e-3)] = np.nan

            # 4. Latitude Orientation Normalization (Ascending Check)
            lats = raw_lats.copy()
            if len(lats) > 1 and lats[0] > lats[-1]:
                # Invert descending latitude array and rows of data
                lats = lats[::-1]
                data_2d = data_2d[::-1, :]

            # 5. Longitude Convention Normalization (0-360 to -180-180 Check)
            lons = raw_lons.copy()
            if np.any(lons > 180.0):
                lons = np.where(lons > 180.0, lons - 360.0, lons)
                # Sort longitudes and data columns
                sort_idx = np.argsort(lons)
                lons = lons[sort_idx]
                data_2d = data_2d[:, sort_idx]

            # 6. Extract Metadata
            units = getattr(var_obj, "units", "unknown")
            dataset_id = getattr(ds, "id", os.path.basename(file_path))
            product_name = getattr(ds, "title", getattr(ds, "product_name", os.path.basename(file_path)))
            source = getattr(ds, "source", getattr(ds, "institution", "Satellite Ground Station"))
            satellite = getattr(ds, "satellite_name", getattr(ds, "platform", "ISRO Earth Observation Constellation"))
            sensor = getattr(ds, "sensor", getattr(ds, "instrument", "Optical/Thermal Sensor"))
            time_str = getattr(ds, "time_coverage_start", getattr(ds, "date_created", datetime.now(timezone.utc).isoformat()))

            dlat = abs(float(lats[1] - lats[0])) if len(lats) > 1 else 0.05
            dlon = abs(float(lons[1] - lons[0])) if len(lons) > 1 else 0.05

            bbox = (float(lons.min()), float(lats.min()), float(lons.max()), float(lats.max()))

            meta = RasterDatasetMetadata(
                dataset_id=str(dataset_id),
                product_name=str(product_name),
                variable=str(variable_name),
                source=str(source),
                provider="ISRO / NRSC / INCOIS Ground Segment",
                satellite_name=str(satellite),
                sensor_name=str(sensor),
                file_path=file_path,
                acquisition_time=str(time_str),
                valid_time=str(time_str),
                processing_level=ProcessingLevel.LEVEL_3,
                crs="EPSG:4326",
                bounding_box=bbox,
                shape=data_2d.shape,
                resolution=(round(dlat, 4), round(dlon, 4)),
                units=str(units),
                nodata=-9999.0,
                data_type=DataStatus.ARCHIVED,
                quality_flag=QualityFlag.VERIFIED_SENSOR,
                limitations=[]
            )

            return lats, lons, data_2d, meta

        finally:
            ds.close()

    @staticmethod
    def _find_coord_var(ds: nc.Dataset, candidates: List[str]) -> Optional[str]:
        for c in candidates:
            if c in ds.variables:
                return c
        return None
