"""
Marine & Geospatial Capability Wrappers for ORCA Tool Registry
ISRO SIH 2026 - Problem Statement 26176
"""

import re
from typing import Dict, Any, Optional, List
from backend.tools.base import BaseTool, ToolSchema, ToolParameter
from backend.data.geodata import INDIAN_PORTS

class PointObservationTool(BaseTool):
    name = "get_point_observation"
    description = "Retrieves satellite oceanographic radiometry (SST, Chlorophyll-a, salinity, cloud cover) for specific coordinates."
    purpose = "Oceanographic Earth Observation Telemetry"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "latitude": ToolParameter("latitude", "float", "Latitude in decimal degrees (-90 to 90)", required=True),
                "longitude": ToolParameter("longitude", "float", "Longitude in decimal degrees (-180 to 180)", required=True)
            },
            return_description="Dictionary containing SST, Chlorophyll-a, Salinity, Cloud Cover, and Radiometric Quality."
        )

    async def _run(self, latitude: float, longitude: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        return await self.marine_agent.get_point_observation_async(float(latitude), float(longitude), time_window=time_window)


class SatelliteTelemetryTool(BaseTool):
    name = "get_satellite_telemetry"
    description = "Retrieves orbital status, sensor health, and pass schedule for Oceansat-3, INSAT-3DR, and Sentinel-3."
    purpose = "Satellite Constellation Operational Status"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={},
            return_description="List of active Earth Observation satellite telemetry records."
        )

    def _run(self, **kwargs) -> Any:
        return self.marine_agent.get_satellite_telemetry()


class WeatherObservationTool(BaseTool):
    name = "get_weather_at_point"
    description = "Computes coastal and marine weather telemetry (wave height, wind speed, Beaufort scale, sea-state, fishermen safety index)."
    purpose = "Meteocean Hazard & Sea Safety Evaluation"

    def __init__(self, weather_agent):
        self.weather_agent = weather_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "latitude": ToolParameter("latitude", "float", "Latitude in decimal degrees (-90 to 90)", required=True),
                "longitude": ToolParameter("longitude", "float", "Longitude in decimal degrees (-180 to 180)", required=True)
            },
            return_description="Dictionary with significant wave height, wind, sea-state, safety index, and actionable safety status."
        )

    async def _run(self, latitude: float, longitude: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        return await self.weather_agent.get_weather_at_point_async(float(latitude), float(longitude), time_window=time_window)


class CycloneWarningsTool(BaseTool):
    name = "get_active_cyclones_and_warnings"
    description = "Retrieves active cyclonic storms, severe storm tracks, and high-wave hazard warnings across the North Indian Ocean."
    purpose = "Disaster Management & Extreme Weather Intelligence"

    def __init__(self, weather_agent):
        self.weather_agent = weather_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={},
            return_description="Active cyclone forecast parameters, storm position, and coastal alert level."
        )

    async def _run(self, latitude: Optional[float] = None, longitude: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        return await self.weather_agent.get_active_cyclones_and_warnings_async(ref_lat=latitude, ref_lon=longitude)


class PFZHotspotsTool(BaseTool):
    name = "generate_pfz_hotspots"
    description = "Generates Potential Fishing Zone (PFZ) advisories using thermal-chlorophyll front gradient coincidence (|∇SST| × |∇Chl-a|)."
    purpose = "Scientific Fisheries & Blue Economy Enhancement"

    def __init__(self, ocean_agent):
        self.ocean_agent = ocean_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "reference_port_key": ToolParameter("reference_port_key", "str", "Base Indian harbour key for proximity sorting", required=True, default="kochi")
            },
            return_description="Ranked list of PFZ hotspots with expected catch multiplier, depth, species suitability, and coordinates."
        )

    def _run(self, reference_port_key: str = "kochi", **kwargs) -> Any:
        return self.ocean_agent.generate_pfz_hotspots(reference_port_key=reference_port_key)


class GeofenceStatusTool(BaseTool):
    name = "check_geofence_status"
    description = "Evaluates proximity to International Maritime Boundary Lines (IMBL) and Marine Protected Areas (MPA) for vessel compliance."
    purpose = "Maritime Border Security & Environmental Regulatory Compliance"

    def __init__(self, geo_agent):
        self.geo_agent = geo_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "latitude": ToolParameter("latitude", "float", "Vessel latitude in decimal degrees", required=True),
                "longitude": ToolParameter("longitude", "float", "Vessel longitude in decimal degrees", required=True)
            },
            return_description="Geofence alert level, distance to nearest IMBL in nautical miles, and MPA compliance status."
        )

    def _run(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        return self.geo_agent.check_geofence_status(float(latitude), float(longitude))


class SafeRouteTool(BaseTool):
    name = "compute_safe_route"
    description = "Calculates a weather-aware, border-safe navigation route with waypoints, fuel burn estimation, and transit time."
    purpose = "Safe Maritime Route Planning & Fuel Optimization"

    def __init__(self, geo_agent):
        self.geo_agent = geo_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "start_port_key": ToolParameter("start_port_key", "str", "Departure harbour identifier", required=True),
                "dest_lat": ToolParameter("dest_lat", "float", "Destination latitude", required=True),
                "dest_lon": ToolParameter("dest_lon", "float", "Destination longitude", required=True),
                "dest_name": ToolParameter("dest_name", "str", "Name of destination target", required=False, default="Target PFZ")
            },
            return_description="Waypoints, distance in NM, transit time in hours, fuel in liters, and leg-by-leg safety status."
        )

    def _run(self, start_port_key: str, dest_lat: float, dest_lon: float, dest_name: str = "Target PFZ", **kwargs) -> Dict[str, Any]:
        return self.geo_agent.compute_safe_route(
            start_port_key=start_port_key,
            dest_lat=float(dest_lat),
            dest_lon=float(dest_lon),
            dest_name=dest_name
        )


class PortResolverTool(BaseTool):
    name = "resolve_reference_port"
    description = "Resolves reference Indian coastal port or harbour from natural language query or user GPS coordinates."
    purpose = "Geographic Anchor & Spatial Grounding"

    PORT_PATTERNS = {
        "munambam": r'\b(munambam|paravur)\b',
        "neendakara": r'\b(neendakara|quilon|ashtamudi)\b',
        "sakthikulangara": r'\b(sakthikulangara)\b',
        "vizhinjam": r'\b(vizhinjam|trivandrum|thiruvananthapuram)\b',
        "koyilandy": r'\b(koyilandy|calicut|kozhikode)\b',
        "malpe": r'\b(malpe|udupi|st mary)\b',
        "karwar": r'\b(karwar|baithkol|anjadip)\b',
        "mallet_bunder": r'\b(mallet|ferry wharf|bunder)\b',
        "ratnagiri": r'\b(ratnagiri|mirkarwada|mirya)\b',
        "malim": r'\b(malim|goa|panaji|betim)\b',
        "mangrol": r'\b(mangrol)\b',
        "nagapattinam": r'\b(nagapattinam|nagapatnam|calimere)\b',
        "chinnamuttom": r'\b(chinnamuttom)\b',
        "kakinada": r'\b(kakinada|godavari delta)\b',
        "dhamara": r'\b(dhamara|dhamra|bhadrak)\b',
        "petuaghat": r'\b(petuaghat|deshapran|digha|purba medinipur)\b',
        "kochi": r'\b(cochin|kochi|kerala)\b',
        "chennai": r'\b(madras|chennai|kasimedu)\b',
        "visakhapatnam": r'\b(vizag|visakhapatnam|andhra)\b',
        "mumbai": r'\b(bombay|mumbai|sassoon|versova|maharashtra)\b',
        "porbandar": r'\b(porbandar|gujarat)\b',
        "rameswaram": r'\b(rameswaram|rameshwaram|mandapam|palk)\b',
        "mangalore": r'\b(mangalore|karnataka)\b',
        "paradip": r'\b(paradip|orissa|odisha)\b',
        "kanyakumari": r'\b(kanyakumari|cape comorin)\b',
        "port_blair": r'\b(port blair|andaman|nicobar)\b',
    }

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "query": ToolParameter("query", "str", "User text query", required=True),
                "user_lat": ToolParameter("user_lat", "float", "User latitude if provided", required=False, default=None),
                "user_lon": ToolParameter("user_lon", "float", "User longitude if provided", required=False, default=None),
                "reference_port_override": ToolParameter("reference_port_override", "str", "Explicit port override", required=False, default=None)
            },
            return_description="Port details (key, name, state, lat, lon, region, primary catch)."
        )

    def _run(self, query: str, user_lat: Optional[float] = None, user_lon: Optional[float] = None, reference_port_override: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        if reference_port_override and reference_port_override in INDIAN_PORTS:
            port_key = reference_port_override
            p = INDIAN_PORTS[port_key]
            return {"port_key": port_key, **p}

        q = (query or "").lower()
        port_key = "kochi"
        matched = False

        for key, pattern in self.PORT_PATTERNS.items():
            if re.search(pattern, q):
                port_key = key
                matched = True
                break

        if not matched:
            for key in INDIAN_PORTS:
                if key in q:
                    port_key = key
                    matched = True
                    break

        if not matched and user_lat is not None and user_lon is not None and abs(user_lat) > 0.1:
            closest_key = "kochi"
            min_dist_sq = float("inf")
            for k, p in INDIAN_PORTS.items():
                d_sq = (p["lat"] - user_lat) ** 2 + (p["lon"] - user_lon) ** 2
                if d_sq < min_dist_sq:
                    min_dist_sq = d_sq
                    closest_key = k
            port_key = closest_key

        p = INDIAN_PORTS[port_key]
        return {"port_key": port_key, **p}


class SeaSurfaceTemperatureTool(BaseTool):
    name = "get_sst"
    description = "Retrieves verified real source-backed Sea Surface Temperature (°C) for coastal and offshore coordinates."
    purpose = "Physical Oceanographic SST Telemetry"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "latitude": ToolParameter("latitude", "float", "Latitude in decimal degrees", required=True),
                "longitude": ToolParameter("longitude", "float", "Longitude in decimal degrees", required=True)
            },
            return_description="Standardized MarineDataPoint with SST value, units, valid time, and source provenance."
        )

    async def _run(self, latitude: float, longitude: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        dp = await self.marine_agent.data_service.get_sea_surface_temperature(float(latitude), float(longitude), time_window=time_window)
        return dp.to_dict()


class WaveConditionsTool(BaseTool):
    name = "get_waves"
    description = "Retrieves real source-backed significant wave height, wave direction, wave period, and swell parameters."
    purpose = "Maritime Wave & Swell Hydrodynamic Telemetry"

    def __init__(self, weather_agent):
        self.weather_agent = weather_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "latitude": ToolParameter("latitude", "float", "Latitude in decimal degrees", required=True),
                "longitude": ToolParameter("longitude", "float", "Longitude in decimal degrees", required=True)
            },
            return_description="Dictionary of wave and swell MarineDataPoints."
        )

    async def _run(self, latitude: float, longitude: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        waves = await self.weather_agent.data_service.get_wave_conditions(float(latitude), float(longitude), time_window=time_window)
        return {k: v.to_dict() for k, v in waves.items()}


class WindConditionsTool(BaseTool):
    name = "get_wind"
    description = "Retrieves real source-backed wind speed (knots), wind direction (degrees), and gusts."
    purpose = "Atmospheric Wind Vector Telemetry"

    def __init__(self, weather_agent):
        self.weather_agent = weather_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "latitude": ToolParameter("latitude", "float", "Latitude in decimal degrees", required=True),
                "longitude": ToolParameter("longitude", "float", "Longitude in decimal degrees", required=True)
            },
            return_description="Dictionary of wind MarineDataPoints with knots, degrees, and provenance."
        )

    async def _run(self, latitude: float, longitude: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        winds = await self.weather_agent.data_service.get_wind_conditions(float(latitude), float(longitude), time_window=time_window)
        return {k: v.to_dict() for k, v in winds.items()}


class OceanCurrentsTool(BaseTool):
    name = "get_ocean_currents"
    description = "Retrieves verified surface ocean current velocity (m/s) and current direction (degrees)."
    purpose = "Surface Ocean Current Hydrodynamic Telemetry"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "latitude": ToolParameter("latitude", "float", "Latitude in decimal degrees", required=True),
                "longitude": ToolParameter("longitude", "float", "Longitude in decimal degrees", required=True)
            },
            return_description="Dictionary of current velocity and direction MarineDataPoints."
        )

    async def _run(self, latitude: float, longitude: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        currents = await self.marine_agent.data_service.get_ocean_currents(float(latitude), float(longitude), time_window=time_window)
        return {k: v.to_dict() for k, v in currents.items()}


class TideConditionsTool(BaseTool):
    name = "get_tide"
    description = "Retrieves coastal tide and sea-level gauge data; truthfully returns UNAVAILABLE when not provided."
    purpose = "Tidal & Water-Level Telemetry"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "latitude": ToolParameter("latitude", "float", "Latitude in decimal degrees", required=True),
                "longitude": ToolParameter("longitude", "float", "Longitude in decimal degrees", required=True)
            },
            return_description="Standardized MarineDataPoint reporting tide status or unavailable state."
        )

    async def _run(self, latitude: float, longitude: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        dp = await self.marine_agent.data_service.get_tide_conditions(float(latitude), float(longitude), time_window=time_window)
        return dp.to_dict()


class MarineAdvisoriesTool(BaseTool):
    name = "get_marine_advisories"
    description = "Retrieves official coastal advisories and weather warnings from INCOIS and IMD."
    purpose = "Official Government Coastal Warnings & Advisories"

    def __init__(self, weather_agent):
        self.weather_agent = weather_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "port_name": ToolParameter("port_name", "str", "Reference port name", required=True),
                "state_name": ToolParameter("state_name", "str", "Coastal state name", required=True)
            },
            return_description="Official coastal advisory record with issuing authority and severity."
        )

    async def _run(self, port_name: str, state_name: str, **kwargs) -> Dict[str, Any]:
        return await self.weather_agent.data_service.get_marine_advisories(port_name, state_name)


class SatelliteRasterTool(BaseTool):
    name = "get_satellite_raster"
    description = "Retrieves spatial Earth Observation satellite raster grid (SST, Chlorophyll-a) for a given region."
    purpose = "Satellite Earth Observation Spatial Field Analysis"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "variable": ToolParameter("variable", "str", "Target ocean variable ('sea_surface_temperature' or 'chlorophyll_a')", required=True),
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude in decimal degrees", required=False),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude in decimal degrees", required=False),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude in decimal degrees", required=False),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude in decimal degrees", required=False)
            },
            return_description="Map-ready downsampled 2D grid matrix and metadata for Leaflet canvas overlay."
        )

    async def _run(self, variable: str, min_lat: Optional[float] = None, max_lat: Optional[float] = None, min_lon: Optional[float] = None, max_lon: Optional[float] = None, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        grid = self.marine_agent.catalog.get_map_grid(variable, min_lat, max_lat, min_lon, max_lon, time_window=time_window)
        return grid.model_dump()


class SatellitePointValueTool(BaseTool):
    name = "get_satellite_point_value"
    description = "Extracts exact pixel observation from satellite raster field at target coordinates."
    purpose = "Satellite EO Ground Truth Extraction"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "variable": ToolParameter("variable", "str", "Variable name ('sea_surface_temperature' or 'chlorophyll_a')", required=True),
                "latitude": ToolParameter("latitude", "float", "Target latitude in decimal degrees", required=True),
                "longitude": ToolParameter("longitude", "float", "Target longitude in decimal degrees", required=True)
            },
            return_description="Extracted pixel value, sensor platform, acquisition time, and quality state."
        )

    async def _run(self, variable: str, latitude: float, longitude: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        return self.marine_agent.get_satellite_point_value(variable, latitude, longitude, time_window=time_window)


class SatelliteRegionStatisticsTool(BaseTool):
    name = "get_satellite_region_statistics"
    description = "Calculates zonal statistics (mean, median, min, max, std, valid pixels) over a marine region."
    purpose = "Zonal Earth Observation Statistical Evaluation"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "variable": ToolParameter("variable", "str", "Variable name ('sea_surface_temperature' or 'chlorophyll_a')", required=True),
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude in decimal degrees", required=True),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude in decimal degrees", required=True),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude in decimal degrees", required=True),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude in decimal degrees", required=True)
            },
            return_description="Statistical metrics strictly computed over valid ocean pixels."
        )

    async def _run(self, variable: str, min_lat: float, max_lat: float, min_lon: float, max_lon: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        return self.marine_agent.get_regional_statistics(variable, min_lat, max_lat, min_lon, max_lon, time_window=time_window)


class SSTRasterTool(BaseTool):
    name = "get_sst_raster"
    description = "Retrieves spatial Sea Surface Temperature field from ISRO INSAT-3DR / Copernicus SLSTR."
    purpose = "Satellite Thermal Radiometry Spatial Mapping"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude in decimal degrees", required=False),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude in decimal degrees", required=False),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude in decimal degrees", required=False),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude in decimal degrees", required=False)
            },
            return_description="Thermal SST spatial field and map grid representation."
        )

    async def _run(self, min_lat: Optional[float] = None, max_lat: Optional[float] = None, min_lon: Optional[float] = None, max_lon: Optional[float] = None, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        grid = self.marine_agent.catalog.get_map_grid("sea_surface_temperature", min_lat, max_lat, min_lon, max_lon, time_window=time_window)
        return grid.model_dump()


class ChlorophyllRasterTool(BaseTool):
    name = "get_chlorophyll_raster"
    description = "Retrieves spatial Chlorophyll-a concentration field from ISRO Oceansat-3 (EOS-06) OCM-3."
    purpose = "Satellite Ocean Colour Spatial Mapping"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude in decimal degrees", required=False),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude in decimal degrees", required=False),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude in decimal degrees", required=False),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude in decimal degrees", required=False)
            },
            return_description="Chlorophyll-a spatial field from Oceansat-3 OCM-3."
        )

    async def _run(self, min_lat: Optional[float] = None, max_lat: Optional[float] = None, min_lon: Optional[float] = None, max_lon: Optional[float] = None, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        grid = self.marine_agent.catalog.get_map_grid("chlorophyll_a", min_lat, max_lat, min_lon, max_lon, time_window=time_window)
        return grid.model_dump()


class RasterContoursTool(BaseTool):
    name = "get_raster_contours"
    description = "Generates RFC 7946 GeoJSON contour bands from satellite raster fields for Leaflet display."
    purpose = "Vector GIS Contour Generation"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "variable": ToolParameter("variable", "str", "Variable name ('sea_surface_temperature' or 'chlorophyll_a')", required=True),
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude in decimal degrees", required=False),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude in decimal degrees", required=False),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude in decimal degrees", required=False),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude in decimal degrees", required=False)
            },
            return_description="GeoJSON FeatureCollection containing contour intervals."
        )

    async def _run(self, variable: str, min_lat: Optional[float] = None, max_lat: Optional[float] = None, min_lon: Optional[float] = None, max_lon: Optional[float] = None, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        return self.marine_agent.get_raster_contours(variable, min_lat, max_lat, min_lon, max_lon, time_window=time_window)


class SpatialGradientTool(BaseTool):
    name = "get_spatial_gradient"
    description = "Computes horizontal physical gradients (dX/dx, dX/dy, |grad X| in unit/km) across satellite fields."
    purpose = "Thermal & Ocean Color Frontal Detection"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "variable": ToolParameter("variable", "str", "Target variable ('sea_surface_temperature' or 'chlorophyll_a')", required=True),
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude in decimal degrees", required=True),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude in decimal degrees", required=True),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude in decimal degrees", required=True),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude in decimal degrees", required=True)
            },
            return_description="Physical gradient magnitude, frontal coordinates, and directional components."
        )

    async def _run(self, variable: str, min_lat: float, max_lat: float, min_lon: float, max_lon: float, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        return self.marine_agent.get_spatial_gradient(variable, min_lat, max_lat, min_lon, max_lon, time_window=time_window)


class AvailableEOProductsTool(BaseTool):
    name = "get_available_eo_products"
    description = "Lists all cataloged satellite Earth Observation products, sensors, and coverage."
    purpose = "Satellite Product Discovery"

    def __init__(self, marine_agent):
        self.marine_agent = marine_agent
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={},
            return_description="List of satellite datasets with variable, resolution, and sensor metadata."
        )

    async def _run(self, **kwargs) -> List[Dict[str, Any]]:
        return self.marine_agent.get_available_eo_products()

