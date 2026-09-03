"""
Normalized Marine & Oceanographic Data Schemas for ORCA
ISRO SIH 2026 - Problem Statement 26176
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class DataStatus(str, Enum):
    LIVE = "LIVE"
    NEAR_REAL_TIME = "NEAR_REAL_TIME"
    OBSERVED = "OBSERVED"
    ARCHIVED = "ARCHIVED"
    REAL_ARCHIVED = "REAL_ARCHIVED"
    FORECAST = "FORECAST"
    HISTORICAL = "HISTORICAL"
    DERIVED = "DERIVED"
    STATIC_REFERENCE = "STATIC_REFERENCE"
    DEMO = "DEMO"
    DEMO_SYNTHETIC = "DEMO_SYNTHETIC"
    UNAVAILABLE = "UNAVAILABLE"

class QualityFlag(str, Enum):
    VERIFIED_SENSOR = "VERIFIED_SENSOR"
    GOOD = "GOOD"
    UNCERTAIN = "UNCERTAIN"
    MISSING = "MISSING"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    STALE = "STALE"
    SOURCE_ERROR = "SOURCE_ERROR"
    UNKNOWN = "UNKNOWN"

class MarineDataPoint(BaseModel):
    """
    Standardized atomic environmental observation or forecast measurement.
    Retains full provenance, explicit timestamps, units, and quality metadata.
    """
    variable: str
    value: Optional[float] = None
    unit: str
    latitude: float
    longitude: float
    depth_m: float = 0.0
    
    # Temporal Metadata (Section 13, 15, 29)
    data_type: DataStatus = DataStatus.LIVE
    observed_at: Optional[str] = None
    valid_time: Optional[str] = None
    issued_at: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    freshness_seconds: Optional[float] = None
    
    # Source Provenance & Quality (Section 7, 30, 39)
    source: str
    source_url: Optional[str] = None
    quality: QualityFlag = QualityFlag.GOOD
    is_fallback: bool = False
    fallback_source: Optional[str] = None
    limitations: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

class MarineEnvironmentBundle(BaseModel):
    """
    Aggregated environmental baseline for a specific location and temporal window.
    """
    latitude: float
    longitude: float
    timestamp: str
    is_forecast: bool = False
    target_time_label: str = "current_observation"
    
    # Core Oceanographic Variables
    sea_surface_temperature: Optional[MarineDataPoint] = None
    chlorophyll_a: Optional[MarineDataPoint] = None
    salinity: Optional[MarineDataPoint] = None
    
    # Wave & Swell
    significant_wave_height: Optional[MarineDataPoint] = None
    wave_direction: Optional[MarineDataPoint] = None
    wave_period: Optional[MarineDataPoint] = None
    swell_wave_height: Optional[MarineDataPoint] = None
    swell_wave_direction: Optional[MarineDataPoint] = None
    swell_wave_period: Optional[MarineDataPoint] = None
    
    # Ocean Currents
    current_velocity: Optional[MarineDataPoint] = None
    current_direction: Optional[MarineDataPoint] = None
    
    # Meteorology
    wind_speed: Optional[MarineDataPoint] = None
    wind_direction: Optional[MarineDataPoint] = None
    wind_gusts: Optional[MarineDataPoint] = None
    air_temperature: Optional[MarineDataPoint] = None
    surface_pressure: Optional[MarineDataPoint] = None
    precipitation: Optional[MarineDataPoint] = None
    visibility: Optional[MarineDataPoint] = None
    
    # Hydrodynamics & Hazards
    tide_water_level: Optional[MarineDataPoint] = None
    lightning: Optional[MarineDataPoint] = None
    active_cyclones: List[Dict[str, Any]] = Field(default_factory=list)
    marine_advisories: List[Dict[str, Any]] = Field(default_factory=list)
    
    # System Metadata
    data_sources_used: List[str] = Field(default_factory=list)
    unavailable_variables: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
