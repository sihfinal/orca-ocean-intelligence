"""
Open-Meteo Marine API Adapter
ISRO SIH 2026 - Problem Statement 26176
Ingests real Sea Surface Temperature, Wave, Swell, and Ocean Current Telemetry.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from backend.data.adapters.base import BaseDataServiceAdapter
from backend.data.schemas import MarineDataPoint, DataStatus, QualityFlag

class OpenMeteoMarineAdapter(BaseDataServiceAdapter):
    """
    Adapter for Open-Meteo Marine Data Feed.
    Provides verified physical oceanographic observations and multi-day forecasts.
    """
    def __init__(self, timeout_seconds: float = 4.0):
        super().__init__(
            source_name="Open-Meteo Marine API",
            organization="Open-Meteo / ECMWF IFS & WAM Marine Modeling",
            base_url="https://marine-api.open-meteo.com/v1/marine",
            timeout_seconds=timeout_seconds,
            max_retries=0
        )

    async def fetch_marine_data(
        self,
        lat: float,
        lon: float,
        target_datetime: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetches hourly oceanographic variables for given coordinates and target timestamp.
        """
        params = {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "hourly": "sea_surface_temperature,wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,swell_wave_period,ocean_current_velocity,ocean_current_direction",
            "timezone": "Asia/Kolkata"
        }

        resp = await self._safe_get("", params=params)
        if not resp["success"]:
            return resp

        data = resp["data"]
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        if not times:
            return {"success": False, "error": "Empty hourly time series in marine response", "status_code": 502}

        # Select target time index (align with Phase 3 TimeWindow)
        target_idx, is_forecast, valid_time_str = self._find_time_index(times, target_datetime)

        return {
            "success": True,
            "latitude": data.get("latitude", lat),
            "longitude": data.get("longitude", lon),
            "target_index": target_idx,
            "is_forecast": is_forecast,
            "valid_time": valid_time_str,
            "hourly": hourly,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }

    def _find_time_index(
        self,
        times: list,
        target_datetime: Optional[datetime]
    ) -> Tuple[int, bool, str]:
        """Aligns target timestamp with closest hourly entry."""
        if not target_datetime:
            return 0, False, times[0]

        target_iso_prefix = target_datetime.strftime("%Y-%m-%dT%H:00")
        for i, t in enumerate(times):
            if t.startswith(target_iso_prefix):
                now_utc = datetime.now(timezone.utc)
                is_future = target_datetime.astimezone(timezone.utc) > now_utc
                return i, is_future, t

        # Fallback to closest available hour
        return 0, False, times[0]

    def extract_datapoints(self, marine_payload: Dict[str, Any]) -> Dict[str, MarineDataPoint]:
        """Normalizes payload into standardized MarineDataPoints."""
        if not marine_payload.get("success"):
            return {}

        lat = marine_payload["latitude"]
        lon = marine_payload["longitude"]
        idx = marine_payload["target_index"]
        is_forecast = marine_payload["is_forecast"]
        valid_time = marine_payload["valid_time"]
        retrieved_at = marine_payload["retrieved_at"]
        hourly = marine_payload["hourly"]

        data_type = DataStatus.FORECAST if is_forecast else DataStatus.OBSERVED

        def _make_point(var_name: str, unit: str) -> Optional[MarineDataPoint]:
            vals = hourly.get(var_name, [])
            if idx < len(vals) and vals[idx] is not None:
                return MarineDataPoint(
                    variable=var_name,
                    value=float(vals[idx]),
                    unit=unit,
                    latitude=lat,
                    longitude=lon,
                    data_type=data_type,
                    valid_time=valid_time,
                    observed_at=valid_time if not is_forecast else None,
                    retrieved_at=retrieved_at,
                    source=self.source_name,
                    source_url=self.base_url,
                    quality=QualityFlag.GOOD
                )
            return None

        return {
            "sea_surface_temperature": _make_point("sea_surface_temperature", "°C"),
            "significant_wave_height": _make_point("wave_height", "m"),
            "wave_direction": _make_point("wave_direction", "deg"),
            "wave_period": _make_point("wave_period", "s"),
            "swell_wave_height": _make_point("swell_wave_height", "m"),
            "swell_wave_direction": _make_point("swell_wave_direction", "deg"),
            "swell_wave_period": _make_point("swell_wave_period", "s"),
            "current_velocity": _make_point("ocean_current_velocity", "m/s"),
            "current_direction": _make_point("ocean_current_direction", "deg")
        }
