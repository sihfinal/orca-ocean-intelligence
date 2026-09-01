"""
Temporal Models & Time Window Representation for ORCA
ISRO SIH 2026 - Problem Statement 26176
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# Indian Standard Time (IST) timezone offset +05:30
IST_OFFSET = timezone(timedelta(hours=5, minutes=30))

class TimeWindow(BaseModel):
    """
    Structured, timezone-aware representation of a temporal request.
    Distinguishes understood semantic time from executable forecast capabilities.
    """
    start_datetime: datetime
    end_datetime: datetime
    timezone: str = "Asia/Kolkata"
    label: str = "current_observation"
    is_relative: bool = False
    is_future: bool = False
    is_past: bool = False
    resolution_source: str = "default_clock"
    
    # Metadata foundation for Phase 4 observation vs forecast ingestion (Section 19)
    data_type: str = "SYNTHETIC"  # OBSERVED, FORECAST, PREDICTED, DERIVED, STATIC, SYNTHETIC
    observed_at: Optional[str] = None
    forecast_for: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    
    # Scientific Honesty Gate (Section 18 & 40)
    forecast_executable: bool = False
    capability_note: str = "Temporal window understood. In-situ forecast models deferred to Phase 4."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_datetime": self.start_datetime.isoformat(),
            "end_datetime": self.end_datetime.isoformat(),
            "timezone": self.timezone,
            "label": self.label,
            "is_relative": self.is_relative,
            "is_future": self.is_future,
            "resolution_source": self.resolution_source,
            "data_type": self.data_type,
            "forecast_executable": self.forecast_executable,
            "capability_note": self.capability_note
        }
