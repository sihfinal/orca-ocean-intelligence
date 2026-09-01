"""
Phase 7 Geospatial, Geofencing & Route Optimization Tools
ISRO SIH 2026 - Problem Statement 26176
Phase 7: Geofencing, Risk/Safety & Real Route Optimization
"""

from typing import Dict, Any, List, Optional
from backend.tools.base import BaseTool, ToolSchema, ToolParameter, ToolResult
from backend.geospatial.geofence_service import GeofenceService
from backend.geospatial.risk_engine import MarineRiskEngine
from backend.geospatial.routing_engine import MarineRouteOptimizer
from backend.data.geodata import INDIAN_PORTS

class CheckGeofenceStatusTool(BaseTool):
    name = "check_geofence_status"
    description = "Checks whether coordinates or vessels lie within or near Marine Protected Areas, IMBL international borders, or military exclusion zones."
    purpose = "Boundary Compliance and Proximity Verification"

    def __init__(self, geofence_service: Optional[GeofenceService] = None):
        self.geofence_service = geofence_service or GeofenceService()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "lat": ToolParameter("lat", "float", "Latitude in decimal degrees", required=False, default=9.94),
                "lon": ToolParameter("lon", "float", "Longitude in decimal degrees", required=False, default=76.25),
                "buffer_km": ToolParameter("buffer_km", "float", "Safety buffer distance in km", required=False, default=5.0),
                "time_window": ToolParameter("time_window", "object", "Optional temporal window for seasonal restrictions", required=False, default=None)
            },
            return_description="Geofence status (CLEAR, RESTRICTED, NEAR_RESTRICTION, UNKNOWN) and distance to nearest boundary."
        )

    async def _run(self, lat: Optional[float] = None, lon: Optional[float] = None, buffer_km: float = 5.0, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        latitude = float(lat) if lat is not None else 9.94
        longitude = float(lon) if lon is not None else 76.25
        return self.geofence_service.check_point(latitude, longitude, time_window=time_window, buffer_km=buffer_km)

class FindRestrictionsTool(BaseTool):
    name = "find_restrictions"
    description = "Lists all active maritime regulatory restrictions and protected zones in the Indian EEZ for the given time window."
    purpose = "Regulatory Maritime Boundary Discovery"

    def __init__(self, geofence_service: Optional[GeofenceService] = None):
        self.geofence_service = geofence_service or GeofenceService()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "time_window": ToolParameter("time_window", "object", "Temporal context window", required=False, default=None)
            },
            return_description="List of active geofence boundaries with legal restrictions."
        )

    async def _run(self, time_window: Optional[Any] = None, **kwargs) -> List[Dict[str, Any]]:
        active_gfs = self.geofence_service.get_active_geofences(time_window)
        return [
            {
                "id": gf.id,
                "name": gf.name,
                "type": gf.type.value,
                "jurisdiction": gf.jurisdiction,
                "status": gf.status,
                "restrictions": gf.restrictions
            }
            for gf in active_gfs
        ]

class AssessMarineRiskTool(BaseTool):
    name = "assess_marine_risk"
    description = "Evaluates multi-factor marine risk (waves, wind, cyclone, geofence boundaries) for any maritime location."
    purpose = "Multi-Factor Maritime Peril Assessment"

    def __init__(self, risk_engine: Optional[MarineRiskEngine] = None):
        self.risk_engine = risk_engine or MarineRiskEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "lat": ToolParameter("lat", "float", "Latitude in decimal degrees", required=True),
                "lon": ToolParameter("lon", "float", "Longitude in decimal degrees", required=True),
                "weather_telemetry": ToolParameter("weather_telemetry", "object", "Retrieved marine weather data", required=False, default=None),
                "cyclone_info": ToolParameter("cyclone_info", "object", "Retrieved active cyclone telemetry", required=False, default=None),
                "time_window": ToolParameter("time_window", "object", "Temporal window", required=False, default=None)
            },
            return_description="Composite risk score [0.0 - 1.0], SafetyClassification, and component risk breakdown."
        )

    async def _run(self, lat: float, lon: float, weather_telemetry: Optional[Dict[str, Any]] = None, cyclone_info: Optional[Dict[str, Any]] = None, time_window: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        return self.risk_engine.evaluate_point_risk(
            float(lat), float(lon), weather_telemetry=weather_telemetry, cyclone_info=cyclone_info, time_window=time_window
        )

class ScoreCandidateSafetyTool(BaseTool):
    name = "score_candidate_safety"
    description = "Evaluates PFZ candidates across the Decision Matrix: separates PFZ suitability from operational risk and assigns PREFERRED, HAZARDOUS, or NO_GO."
    purpose = "Candidate Decision Matrix Evaluation"

    def __init__(self, risk_engine: Optional[MarineRiskEngine] = None):
        self.risk_engine = risk_engine or MarineRiskEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "candidates": ToolParameter("candidates", "object", "List of PFZ candidates to evaluate", required=True),
                "weather_telemetry": ToolParameter("weather_telemetry", "object", "Retrieved marine weather data", required=False, default=None),
                "cyclone_info": ToolParameter("cyclone_info", "object", "Retrieved active cyclone telemetry", required=False, default=None),
                "time_window": ToolParameter("time_window", "object", "Temporal window", required=False, default=None)
            },
            return_description="Ranked candidates with DecisionState, RiskScore, and traceable safety explanations."
        )

    async def _run(self, candidates: Any, weather_telemetry: Optional[Dict[str, Any]] = None, cyclone_info: Optional[Dict[str, Any]] = None, time_window: Optional[Any] = None, **kwargs) -> List[Dict[str, Any]]:
        if not candidates:
            return []
        if not isinstance(candidates, list):
            candidates = [candidates]

        ranked = self.risk_engine.rank_candidates_by_safety(
            candidates, weather_telemetry=weather_telemetry, cyclone_info=cyclone_info, time_window=time_window
        )
        return [r.dict() for r in ranked]

class ComputeSafeRouteTool(BaseTool):
    name = "compute_safe_route"
    description = "Computes an A* least-cost, hazard-aware, border-compliant vessel route avoiding land barriers, restricted zones, and high wave sectors."
    purpose = "Vessel Navigational Path Optimization"

    def __init__(self, route_optimizer: Optional[MarineRouteOptimizer] = None):
        self.route_optimizer = route_optimizer or MarineRouteOptimizer()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "start_lat": ToolParameter("start_lat", "float", "Origin latitude", required=False, default=None),
                "start_lon": ToolParameter("start_lon", "float", "Origin longitude", required=False, default=None),
                "start_port_key": ToolParameter("start_port_key", "string", "Origin port key", required=False, default=None),
                "dest_lat": ToolParameter("dest_lat", "float", "Destination latitude", required=True),
                "dest_lon": ToolParameter("dest_lon", "float", "Destination longitude", required=True),
                "dest_name": ToolParameter("dest_name", "string", "Destination label", required=False, default="Target PFZ"),
                "weather_telemetry": ToolParameter("weather_telemetry", "object", "Retrieved marine weather data", required=False, default=None),
                "cyclone_info": ToolParameter("cyclone_info", "object", "Retrieved active cyclone telemetry", required=False, default=None),
                "time_window": ToolParameter("time_window", "object", "Temporal window", required=False, default=None),
                "cruising_speed_knots": ToolParameter("cruising_speed_knots", "float", "Vessel speed in knots", required=False, default=9.5)
            },
            return_description="OptimizedRoute payload with waypoints, transit time, diesel consumption, and deviation explanations."
        )

    async def _run(
        self,
        dest_lat: float,
        dest_lon: float,
        start_lat: Optional[float] = None,
        start_lon: Optional[float] = None,
        start_port_key: Optional[str] = None,
        dest_name: str = "Target PFZ",
        weather_telemetry: Optional[Dict[str, Any]] = None,
        cyclone_info: Optional[Dict[str, Any]] = None,
        time_window: Optional[Any] = None,
        cruising_speed_knots: float = 9.5,
        **kwargs
    ) -> Dict[str, Any]:
        # Resolve starting coordinates
        start_name = "Departure Port"
        if start_port_key and start_port_key.lower() in INDIAN_PORTS:
            port = INDIAN_PORTS[start_port_key.lower()]
            start_lat = port["lat"]
            start_lon = port["lon"]
            start_name = port["name"]
        elif start_lat is None or start_lon is None:
            port = INDIAN_PORTS["kochi"]
            start_lat = port["lat"]
            start_lon = port["lon"]
            start_name = port["name"]

        res = self.route_optimizer.optimize_route(
            start_lat=float(start_lat),
            start_lon=float(start_lon),
            dest_lat=float(dest_lat),
            dest_lon=float(dest_lon),
            start_name=start_name,
            dest_name=dest_name,
            weather_telemetry=weather_telemetry,
            cyclone_info=cyclone_info,
            time_window=time_window,
            cruising_speed_knots=cruising_speed_knots
        )
        return res.dict()

class ComputeAlternativeRoutesTool(BaseTool):
    name = "compute_alternative_routes"
    description = "Generates both the Least-Cost hazard-aware route and the Shortest Navigable distance route for comparison."
    purpose = "Alternative Maritime Trajectory Exploration"

    def __init__(self, route_optimizer: Optional[MarineRouteOptimizer] = None):
        self.route_optimizer = route_optimizer or MarineRouteOptimizer()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "start_lat": ToolParameter("start_lat", "float", "Origin latitude", required=True),
                "start_lon": ToolParameter("start_lon", "float", "Origin longitude", required=True),
                "dest_lat": ToolParameter("dest_lat", "float", "Destination latitude", required=True),
                "dest_lon": ToolParameter("dest_lon", "float", "Destination longitude", required=True),
                "start_name": ToolParameter("start_name", "string", "Origin label", required=False, default="Departure"),
                "dest_name": ToolParameter("dest_name", "string", "Destination label", required=False, default="Destination"),
                "weather_telemetry": ToolParameter("weather_telemetry", "object", "Retrieved marine weather data", required=False, default=None),
                "cyclone_info": ToolParameter("cyclone_info", "object", "Retrieved active cyclone telemetry", required=False, default=None),
                "time_window": ToolParameter("time_window", "object", "Temporal window", required=False, default=None)
            },
            return_description="List of alternative routes (Least-Cost vs Shortest-Distance)."
        )

    async def _run(
        self,
        start_lat: float,
        start_lon: float,
        dest_lat: float,
        dest_lon: float,
        start_name: str = "Departure",
        dest_name: str = "Destination",
        weather_telemetry: Optional[Dict[str, Any]] = None,
        cyclone_info: Optional[Dict[str, Any]] = None,
        time_window: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        res = self.route_optimizer.optimize_route(
            start_lat=float(start_lat),
            start_lon=float(start_lon),
            dest_lat=float(dest_lat),
            dest_lon=float(dest_lon),
            start_name=start_name,
            dest_name=dest_name,
            weather_telemetry=weather_telemetry,
            cyclone_info=cyclone_info,
            time_window=time_window
        )
        return res.dict()
