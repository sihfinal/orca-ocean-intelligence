"""
Open-Meteo Atmospheric Weather API Adapter
ISRO SIH 2026 - Problem Statement 26176
Ingests real Wind Speed, Wind Direction, Gusts, Pressure, Precipitation & Visibility.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from backend.data.adapters.base import BaseDataServiceAdapter
from backend.data.schemas import MarineDataPoint, DataStatus, QualityFlag

class OpenMeteoWeatherAdapter(BaseDataServiceAdapter):
    """
    Adapter for Open-Meteo Meteorological Weather Feed.
    Provides verified atmospheric observations, wind telemetry, and forecasts.
    """
    def __init__(self, timeout_seconds: float = 4.0):
        super().__init__(
            source_name="Open-Meteo Weather API",
            organization="Open-Meteo / DWD ICON & NOAA GFS Atmospheric Modeling",
            base_url="https://api.open-meteo.com/v1/forecast",
            timeout_seconds=timeout_seconds,
            max_retries=0
        )

    async def fetch_weather_data(
        self,
        lat: float,
        lon: float,
        target_datetime: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetches hourly meteorological variables for given coordinates and target timestamp.
        """
        params = {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "hourly": "temperature_2m,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation,visibility,weather_code",
            "timezone": "Asia/Kolkata"
        }

        resp = await self._safe_get("", params=params)
        if not resp["success"]:
            return resp

        data = resp["data"]
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        if not times:
            return {"success": False, "error": "Empty hourly time series in weather response", "status_code": 502}

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
        if not target_datetime:
            return 0, False, times[0]

        target_iso_prefix = target_datetime.strftime("%Y-%m-%dT%H:00")
        for i, t in enumerate(times):
            if t.startswith(target_iso_prefix):
                now_utc = datetime.now(timezone.utc)
                is_future = target_datetime.astimezone(timezone.utc) > now_utc
                return i, is_future, t

        return 0, False, times[0]

    def extract_datapoints(self, weather_payload: Dict[str, Any]) -> Dict[str, MarineDataPoint]:
        """Normalizes payload into standardized MarineDataPoints with explicit unit conversions."""
        if not weather_payload.get("success"):
            return {}

        lat = weather_payload["latitude"]
        lon = weather_payload["longitude"]
        idx = weather_payload["target_index"]
        is_forecast = weather_payload["is_forecast"]
        valid_time = weather_payload["valid_time"]
        retrieved_at = weather_payload["retrieved_at"]
        hourly = weather_payload["hourly"]

        data_type = DataStatus.FORECAST if is_forecast else DataStatus.OBSERVED

        def _make_point(var_name: str, out_name: str, unit: str, scale: float = 1.0) -> Optional[MarineDataPoint]:
            vals = hourly.get(var_name, [])
            if idx < len(vals) and vals[idx] is not None:
                val = round(float(vals[idx]) * scale, 2)
                return MarineDataPoint(
                    variable=out_name,
                    value=val,
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

        # Wind speed in knots (1 km/h = 0.539957 knots, 1 m/s = 1.94384 knots)
        # Open-Meteo wind_speed_10m is in km/h by default
        wind_speed = _make_point("wind_speed_10m", "wind_speed", "kts", scale=0.539957)
        wind_direction = _make_point("wind_direction_10m", "wind_direction", "deg")
        wind_gusts = _make_point("wind_gusts_10m", "wind_gusts", "kts", scale=0.539957)
        air_temp = _make_point("temperature_2m", "air_temperature", "°C")
        pressure = _make_point("surface_pressure", "surface_pressure", "hPa")
        precip = _make_point("precipitation", "precipitation", "mm")
        
        # Visibility: Open-Meteo returns meters, convert to km
        visibility = _make_point("visibility", "visibility", "km", scale=0.001)

        # Lightning / Thunderstorm probability from WMO weather code
        # Codes 95, 96, 99 indicate thunderstorm with or without hail
        w_codes = hourly.get("weather_code", [])
        w_code = w_codes[idx] if idx < len(w_codes) else None
        lightning_point = None
        if w_code is not None:
            is_thunderstorm = w_code in [95, 96, 99]
            lightning_point = MarineDataPoint(
                variable="lightning_risk",
                value=85.0 if is_thunderstorm else 5.0,
                unit="percent",
                latitude=lat,
                longitude=lon,
                data_type=data_type,
                valid_time=valid_time,
                retrieved_at=retrieved_at,
                source=self.source_name,
                source_url=self.base_url,
                quality=QualityFlag.GOOD
            )

        return {
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,
            "wind_gusts": wind_gusts,
            "air_temperature": air_temp,
            "surface_pressure": pressure,
            "precipitation": precip,
            "visibility": visibility,
            "lightning": lightning_point
        }
