"""
Central Marine & Oceanographic Data Service for ORCA
ISRO SIH 2026 - Problem Statement 26176
Coordinates real external source adapters, multi-turn temporal alignment, caching, and unit normalization.
"""

import os
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple

from backend.data.schemas import (
    MarineDataPoint,
    MarineEnvironmentBundle,
    DataStatus,
    QualityFlag
)
from backend.data.adapters.open_meteo_marine import OpenMeteoMarineAdapter
from backend.data.adapters.open_meteo_weather import OpenMeteoWeatherAdapter
from backend.data.adapters.incois_adapter import INCOISDataServiceAdapter
from backend.data.adapters.cyclone_adapter import TropicalCycloneAdapter
from backend.temporal.models import TimeWindow, IST_OFFSET

logger = logging.getLogger("blue_orbit.data.marine_service")

class MarineDataService:
    """
    Unified environmental data backbone for ORCA agents and tools.
    Replaces synthetic trigonometric formulas with verified source feeds,
    caching, and temporal forecast resolution.
    """
    def __init__(self, cache_ttl_seconds: int = 900):
        self.marine_adapter = OpenMeteoMarineAdapter()
        self.weather_adapter = OpenMeteoWeatherAdapter()
        self.incois_adapter = INCOISDataServiceAdapter()
        self.cyclone_adapter = TropicalCycloneAdapter()
        
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.mode = os.getenv("ORCA_DATA_MODE", "LIVE").upper()

    def _cache_key(self, prefix: str, lat: float, lon: float, target_time: Optional[datetime] = None) -> str:
        time_part = target_time.strftime("%Y%m%d%H") if target_time else "current"
        return f"{prefix}:{round(lat, 2)}:{round(lon, 2)}:{time_part}"

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self._cache:
            entry = self._cache[key]
            age = time.time() - entry["cached_at"]
            if age < self.cache_ttl_seconds:
                data = dict(entry["data"])
                data["cache_age_seconds"] = round(age, 1)
                data["is_cached"] = True
                return data
            else:
                self._cache.pop(key, None)
        return None

    def _save_to_cache(self, key: str, data: Dict[str, Any]) -> None:
        self._cache[key] = {
            "data": data,
            "cached_at": time.time()
        }

    async def get_sea_surface_temperature(
        self,
        lat: float,
        lon: float,
        time_window: Optional[TimeWindow] = None
    ) -> MarineDataPoint:
        """Retrieves real source-backed Sea Surface Temperature (°C)."""
        target_dt = time_window.start_datetime if time_window else None
        c_key = self._cache_key("sst", lat, lon, target_dt)
        cached = self._get_from_cache(c_key)
        if cached:
            return cached["datapoint"]

        payload = await self.marine_adapter.fetch_marine_data(lat, lon, target_datetime=target_dt)
        if payload.get("success"):
            points = self.marine_adapter.extract_datapoints(payload)
            sst_point = points.get("sea_surface_temperature")
            if sst_point and sst_point.value is not None:
                self._save_to_cache(c_key, {"datapoint": sst_point})
                return sst_point

        # Truthful failure representation - NO SYNTHETIC FALLBACK (Section 10)
        return MarineDataPoint(
            variable="sea_surface_temperature",
            value=None,
            unit="°C",
            latitude=lat,
            longitude=lon,
            data_type=DataStatus.UNAVAILABLE,
            source=self.marine_adapter.source_name,
            source_url=self.marine_adapter.base_url,
            quality=QualityFlag.SOURCE_ERROR,
            limitations=[f"SST feed temporarily unavailable from {self.marine_adapter.source_name}: {payload.get('error', 'No data')}"]
        )

    async def get_wave_conditions(
        self,
        lat: float,
        lon: float,
        time_window: Optional[TimeWindow] = None
    ) -> Dict[str, MarineDataPoint]:
        """Retrieves real source-backed wave and swell metrics."""
        target_dt = time_window.start_datetime if time_window else None
        c_key = self._cache_key("waves", lat, lon, target_dt)
        cached = self._get_from_cache(c_key)
        if cached:
            return cached["datapoints"]

        payload = await self.marine_adapter.fetch_marine_data(lat, lon, target_datetime=target_dt)
        if payload.get("success"):
            points = self.marine_adapter.extract_datapoints(payload)
            wave_points = {
                k: points[k] for k in [
                    "significant_wave_height", "wave_direction", "wave_period",
                    "swell_wave_height", "swell_wave_direction", "swell_wave_period"
                ] if k in points and points[k] is not None
            }
            if wave_points:
                self._save_to_cache(c_key, {"datapoints": wave_points})
                return wave_points

        # Truthful failure representation
        return {
            "significant_wave_height": MarineDataPoint(
                variable="significant_wave_height",
                value=None,
                unit="m",
                latitude=lat,
                longitude=lon,
                data_type=DataStatus.UNAVAILABLE,
                source=self.marine_adapter.source_name,
                quality=QualityFlag.SOURCE_ERROR,
                limitations=[f"Wave telemetry unavailable: {payload.get('error')}"]
            )
        }

    async def get_wind_conditions(
        self,
        lat: float,
        lon: float,
        time_window: Optional[TimeWindow] = None
    ) -> Dict[str, MarineDataPoint]:
        """Retrieves real source-backed wind speed, direction, and gusts."""
        target_dt = time_window.start_datetime if time_window else None
        c_key = self._cache_key("wind", lat, lon, target_dt)
        cached = self._get_from_cache(c_key)
        if cached:
            return cached["datapoints"]

        payload = await self.weather_adapter.fetch_weather_data(lat, lon, target_datetime=target_dt)
        if payload.get("success"):
            points = self.weather_adapter.extract_datapoints(payload)
            wind_points = {
                k: points[k] for k in ["wind_speed", "wind_direction", "wind_gusts"]
                if k in points and points[k] is not None
            }
            if wind_points:
                self._save_to_cache(c_key, {"datapoints": wind_points})
                return wind_points

        return {
            "wind_speed": MarineDataPoint(
                variable="wind_speed",
                value=None,
                unit="kts",
                latitude=lat,
                longitude=lon,
                data_type=DataStatus.UNAVAILABLE,
                source=self.weather_adapter.source_name,
                quality=QualityFlag.SOURCE_ERROR,
                limitations=[f"Wind telemetry unavailable: {payload.get('error')}"]
            )
        }

    async def get_ocean_currents(
        self,
        lat: float,
        lon: float,
        time_window: Optional[TimeWindow] = None
    ) -> Dict[str, MarineDataPoint]:
        """Retrieves real source-backed surface ocean current velocity and direction."""
        target_dt = time_window.start_datetime if time_window else None
        c_key = self._cache_key("currents", lat, lon, target_dt)
        cached = self._get_from_cache(c_key)
        if cached:
            return cached["datapoints"]

        payload = await self.marine_adapter.fetch_marine_data(lat, lon, target_datetime=target_dt)
        if payload.get("success"):
            points = self.marine_adapter.extract_datapoints(payload)
            cur_points = {
                k: points[k] for k in ["current_velocity", "current_direction"]
                if k in points and points[k] is not None
            }
            if cur_points:
                self._save_to_cache(c_key, {"datapoints": cur_points})
                return cur_points

        return {
            "current_velocity": MarineDataPoint(
                variable="current_velocity",
                value=None,
                unit="m/s",
                latitude=lat,
                longitude=lon,
                data_type=DataStatus.UNAVAILABLE,
                source=self.marine_adapter.source_name,
                quality=QualityFlag.SOURCE_ERROR,
                limitations=[f"Current velocity telemetry unavailable: {payload.get('error')}"]
            )
        }

    async def get_tide_conditions(
        self,
        lat: float,
        lon: float,
        time_window: Optional[TimeWindow] = None
    ) -> MarineDataPoint:
        """
        Retrieves real tide / sea-level observations.
        Truthfully returns UNAVAILABLE when public feeds do not provide tide gauge data (Section 23 & 53).
        """
        return MarineDataPoint(
            variable="tide_water_level",
            value=None,
            unit="m",
            latitude=lat,
            longitude=lon,
            data_type=DataStatus.UNAVAILABLE,
            source="INCOIS Tide Gauge Network / SOI",
            quality=QualityFlag.MISSING,
            limitations=["Tide and sea-level gauge telemetry is currently unavailable via public open API for this coordinate. Real-time tide harmonic integration is scheduled for future data phases."]
        )

    async def get_active_cyclones(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        """Queries verified live tropical cyclone feeds."""
        cached = self._get_from_cache("cyclones:active")
        if cached:
            return cached["data"]

        res = await self.cyclone_adapter.get_active_cyclones(ref_lat=lat, ref_lon=lon)
        self._save_to_cache("cyclones:active", {"data": res})
        return res

    async def get_marine_advisories(
        self,
        port_name: str,
        state_name: str
    ) -> Dict[str, Any]:
        """Retrieves official coastal warnings and advisories from INCOIS / IMD."""
        c_key = f"advisories:{port_name.lower()}:{state_name.lower()}"
        cached = self._get_from_cache(c_key)
        if cached:
            return cached["data"]

        res = await self.incois_adapter.get_coastal_advisory(port_name, state_name)
        self._save_to_cache(c_key, {"data": res})
        return res

    async def get_comprehensive_environment(
        self,
        lat: float,
        lon: float,
        time_window: Optional[TimeWindow] = None
    ) -> MarineEnvironmentBundle:
        """
        Assembles a comprehensive, verified environmental bundle across all domain sources.
        """
        target_dt = time_window.start_datetime if time_window else None
        c_key = self._cache_key("bundle", lat, lon, target_dt)
        cached = self._get_from_cache(c_key)
        if cached:
            return cached["bundle"]

        now_str = datetime.now(timezone.utc).isoformat()
        is_forecast = time_window.is_future if time_window else False
        time_label = time_window.label if time_window else "current_observation"

        # Fetch external feeds concurrently
        marine_payload = await self.marine_adapter.fetch_marine_data(lat, lon, target_datetime=target_dt)
        weather_payload = await self.weather_adapter.fetch_weather_data(lat, lon, target_datetime=target_dt)
        cyclone_payload = await self.get_active_cyclones(lat, lon)

        marine_points = self.marine_adapter.extract_datapoints(marine_payload) if marine_payload.get("success") else {}
        weather_points = self.weather_adapter.extract_datapoints(weather_payload) if weather_payload.get("success") else {}

        sources_used = []
        if marine_payload.get("success"): sources_used.append(self.marine_adapter.source_name)
        if weather_payload.get("success"): sources_used.append(self.weather_adapter.source_name)
        if cyclone_payload.get("success"): sources_used.append(self.cyclone_adapter.source_name)

        unavailable_vars = []
        limitations = []

        if not marine_payload.get("success"):
            unavailable_vars.extend(["sea_surface_temperature", "wave_height", "currents"])
            limitations.append(f"Marine feed failed: {marine_payload.get('error')}")

        if not weather_payload.get("success"):
            unavailable_vars.extend(["wind_speed", "surface_pressure", "visibility"])
            limitations.append(f"Weather feed failed: {weather_payload.get('error')}")

        unavailable_vars.append("tide_water_level")
        unavailable_vars.append("chlorophyll_a")  # Satellite raster chlorophyll deferred to Phase 5

        tide_point = await self.get_tide_conditions(lat, lon, time_window)

        bundle = MarineEnvironmentBundle(
            latitude=lat,
            longitude=lon,
            timestamp=now_str,
            is_forecast=is_forecast,
            target_time_label=time_label,
            sea_surface_temperature=marine_points.get("sea_surface_temperature"),
            significant_wave_height=marine_points.get("significant_wave_height"),
            wave_direction=marine_points.get("wave_direction"),
            wave_period=marine_points.get("wave_period"),
            swell_wave_height=marine_points.get("swell_wave_height"),
            swell_wave_direction=marine_points.get("swell_wave_direction"),
            swell_wave_period=marine_points.get("swell_wave_period"),
            current_velocity=marine_points.get("current_velocity"),
            current_direction=marine_points.get("current_direction"),
            wind_speed=weather_points.get("wind_speed"),
            wind_direction=weather_points.get("wind_direction"),
            wind_gusts=weather_points.get("wind_gusts"),
            air_temperature=weather_points.get("air_temperature"),
            surface_pressure=weather_points.get("surface_pressure"),
            precipitation=weather_points.get("precipitation"),
            visibility=weather_points.get("visibility"),
            lightning=weather_points.get("lightning"),
            tide_water_level=tide_point,
            active_cyclones=cyclone_payload.get("active_cyclones", []),
            data_sources_used=sources_used,
            unavailable_variables=unavailable_vars,
            limitations=limitations
        )
        self._save_to_cache(c_key, {"bundle": bundle})
        return bundle
