"""
ORCA Earth Observation & Raster Processing Schemas
SIH 2026 - Problem Statement 26176
Defines canonical data contracts for satellite raster fields, georeferenced spatial extractions,
regional statistics, geodetic spatial gradients, and GeoJSON map representations.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from backend.data.schemas import DataStatus, QualityFlag


class ProcessingLevel(str, Enum):
    LEVEL_1B = "L1B"       # Top-of-atmosphere radiance
    LEVEL_2 = "L2"         # Geophyiscal variables at sensor swath
    LEVEL_3 = "L3"         # Spatially binned, gridded composite
    LEVEL_4 = "L4"         # Analyzed, gap-filled, multi-sensor blend
    DERIVED = "DERIVED"    # Computed secondary field (e.g. gradient, anomaly)


class ExtractionMethod(str, Enum):
    NEAREST_NEIGHBOR = "nearest_neighbor"
    BILINEAR_INTERPOLATION = "bilinear_interpolation"
    CENTROID = "centroid"


class RasterDatasetMetadata(BaseModel):
    """Canonical metadata description for a satellite raster field."""
    dataset_id: str
    product_name: str
    variable: str                      # e.g., "sea_surface_temperature", "chlorophyll_a"
    source: str                        # e.g., "ISRO NRSC / MOSDAC", "Copernicus EUMETSAT"
    provider: str                      # Operational satellite agency
    satellite_name: str                # e.g., "ISRO Oceansat-3 (EOS-06)", "INSAT-3DR"
    sensor_name: str                   # e.g., "OCM-3", "Imager TIR"
    file_path: Optional[str] = None
    acquisition_time: str              # ISO 8601 UTC timestamp of sensor acquisition
    valid_time: str                    # ISO 8601 UTC timestamp for which field is valid
    processing_level: ProcessingLevel = ProcessingLevel.LEVEL_3
    crs: str = "EPSG:4326"             # Standard WGS84 Geographic 2D CRS
    bounding_box: Tuple[float, float, float, float]  # (min_lon, min_lat, max_lon, max_lat)
    shape: Tuple[int, int]             # (rows, cols)
    resolution: Tuple[float, float]    # (dlat, dlon) in degrees
    units: str                         # e.g. "deg_C", "mg/m^3"
    nodata: float = -9999.0
    data_type: DataStatus = DataStatus.ARCHIVED
    quality_flag: QualityFlag = QualityFlag.VERIFIED_SENSOR
    limitations: List[str] = Field(default_factory=list)


class SpatialPointResult(BaseModel):
    """Extracted point observation from a scientific raster field."""
    latitude: float
    longitude: float
    value: Optional[float]             # None if masked/nodata
    unit: str
    cell_latitude: float
    cell_longitude: float
    distance_to_cell_km: float
    extraction_method: ExtractionMethod
    is_masked: bool = False
    is_land: bool = False
    is_cloud: bool = False
    dataset_id: str
    product_name: str
    satellite_name: str
    sensor_name: str
    source: str
    acquisition_time: str
    valid_time: str
    data_type: DataStatus
    quality_flag: QualityFlag
    limitations: List[str] = Field(default_factory=list)


class RegionalStatistics(BaseModel):
    """Zonal/Area statistics computed strictly over unmasked ocean pixels."""
    variable: str
    unit: str
    bounding_box: Tuple[float, float, float, float]  # (min_lon, min_lat, max_lon, max_lat)
    has_valid_data: bool
    mean: Optional[float] = None
    median: Optional[float] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    standard_deviation: Optional[float] = None
    valid_pixel_count: int
    total_pixel_count: int
    valid_percentage: float
    dataset_id: str
    product_name: str
    source: str
    acquisition_time: str
    valid_time: str
    data_type: DataStatus
    limitations: List[str] = Field(default_factory=list)


class HighGradientPoint(BaseModel):
    """Frontal point where spatial derivative exceeds threshold."""
    latitude: float
    longitude: float
    gradient_magnitude: float          # In unit / km (e.g. °C / km or mg/m³ / km)
    d_dx: float                        # Zonal gradient component
    d_dy: float                        # Meridional gradient component


class SpatialGradientResult(BaseModel):
    """Geodetic spacing-aware spatial gradient field."""
    variable: str
    unit: str
    gradient_unit: str                 # e.g., "deg_C/km"
    bounding_box: Tuple[float, float, float, float]
    mean_gradient_magnitude: Optional[float] = None
    max_gradient_magnitude: Optional[float] = None
    frontal_points_count: int
    sharpest_front_points: List[HighGradientPoint] = Field(default_factory=list)
    dataset_id: str
    source: str
    data_type: DataStatus = DataStatus.DERIVED
    acquisition_time: str
    method: str = "Central geodetic finite differences on WGS84 ellipsoid"
    limitations: List[str] = Field(default_factory=list)


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
    crs: Dict[str, Any] = Field(
        default_factory=lambda: {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        }
    )


class RasterGridResponse(BaseModel):
    """Map-ready downsampled grid matrix for Leaflet heatmaps and contouring."""
    variable: str
    unit: str
    latitudes: List[float]
    longitudes: List[float]
    values: List[List[Optional[float]]]  # 2D grid matrix [lat_idx][lon_idx]
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    source: str
    satellite: str
    sensor: str
    acquisition_time: str
    valid_time: str
    data_type: DataStatus
    provenance: Dict[str, Any] = Field(default_factory=dict)
