"""
PFZ Intelligence & Ocean Analytics Tools for ORCA Tool Registry
ISRO SIH 2026 - Problem Statement 26176
Phase 6: PFZ Intelligence, Ocean Analytics & Environmental Hazard Fusion
"""

from typing import Dict, Any, Optional, List
from backend.tools.base import BaseTool, ToolSchema, ToolParameter
from backend.data.pfz.engine import PFZIntelligenceEngine
from backend.temporal.models import TimeWindow

class AnalyzePFZTool(BaseTool):
    name = "analyze_pfz"
    description = "Performs scientific multi-variable PFZ analysis combining SST, Chlorophyll-a, gradients, and marine hazards."
    purpose = "Satellite Earth Observation PFZ Discovery"

    def __init__(self, pfz_engine: Optional[PFZIntelligenceEngine] = None):
        self.pfz_engine = pfz_engine or PFZIntelligenceEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude for bounding box", required=True),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude for bounding box", required=True),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude for bounding box", required=True),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude for bounding box", required=True),
                "reference_lat": ToolParameter("reference_lat", "float", "Reference harbor/boat latitude", required=False, default=None),
                "reference_lon": ToolParameter("reference_lon", "float", "Reference harbor/boat longitude", required=False, default=None)
            }
        )

    async def _run(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        reference_lat: Optional[float] = None,
        reference_lon: Optional[float] = None,
        time_window: Optional[TimeWindow] = None,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        active_cyclones: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        resp = self.pfz_engine.analyze_spatial_pfz(
            min_lat=float(min_lat),
            max_lat=float(max_lat),
            min_lon=float(min_lon),
            max_lon=float(max_lon),
            time_window=time_window,
            reference_lat=float(reference_lat) if reference_lat is not None else None,
            reference_lon=float(reference_lon) if reference_lon is not None else None,
            weather_telemetry=weather_telemetry,
            active_cyclones=active_cyclones
        )
        return resp.dict()


class DetectOceanFrontsTool(BaseTool):
    name = "detect_ocean_fronts"
    description = "Detects thermal infrared and ocean color fronts and calculates spatial coincidence strength."
    purpose = "Physical Frontal Boundary Detection"

    def __init__(self, pfz_engine: Optional[PFZIntelligenceEngine] = None):
        self.pfz_engine = pfz_engine or PFZIntelligenceEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude", required=True),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude", required=True),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude", required=True),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude", required=True)
            }
        )

    async def _run(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        time_window: Optional[TimeWindow] = None,
        **kwargs
    ) -> Dict[str, Any]:
        resp = self.pfz_engine.analyze_spatial_pfz(
            min_lat=float(min_lat),
            max_lat=float(max_lat),
            min_lon=float(min_lon),
            max_lon=float(max_lon),
            time_window=time_window
        )
        return {
            "status": resp.status,
            "region": resp.region,
            "fronts_detected_count": resp.candidates_count,
            "environmental_summary": resp.environmental_summary,
            "provenance": resp.provenance,
            "limitations": resp.limitations
        }


class CalculateOceanGradientsTool(BaseTool):
    name = "calculate_ocean_gradients"
    description = "Calculates geodetic spacing-aware horizontal gradients (dX/dy, dX/dx, |∇X|) in physical units/km."
    purpose = "Oceanographic Spatial Derivative Analysis"

    def __init__(self, pfz_engine: Optional[PFZIntelligenceEngine] = None):
        self.pfz_engine = pfz_engine or PFZIntelligenceEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "variable": ToolParameter("variable", "str", "Raster variable name (sea_surface_temperature or chlorophyll_a)", required=True),
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude", required=True),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude", required=True),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude", required=True),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude", required=True)
            }
        )

    async def _run(
        self,
        variable: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        time_window: Optional[TimeWindow] = None,
        **kwargs
    ) -> Dict[str, Any]:
        res = self.pfz_engine.catalog.get_spatial_gradients(
            variable=variable,
            min_lat=float(min_lat),
            max_lat=float(max_lat),
            min_lon=float(min_lon),
            max_lon=float(max_lon),
            time_window=time_window
        )
        return res.dict()


class GeneratePFZCandidatesTool(BaseTool):
    name = "generate_pfz_candidates"
    description = "Extracts connected candidate ocean regions and bounding polygons from multi-variable suitability fields."
    purpose = "Spatial PFZ Region Clustering"

    def __init__(self, pfz_engine: Optional[PFZIntelligenceEngine] = None):
        self.pfz_engine = pfz_engine or PFZIntelligenceEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "min_lat": ToolParameter("min_lat", "float", "Minimum latitude", required=True),
                "max_lat": ToolParameter("max_lat", "float", "Maximum latitude", required=True),
                "min_lon": ToolParameter("min_lon", "float", "Minimum longitude", required=True),
                "max_lon": ToolParameter("max_lon", "float", "Maximum longitude", required=True)
            }
        )

    async def _run(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        time_window: Optional[TimeWindow] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        resp = self.pfz_engine.analyze_spatial_pfz(
            min_lat=float(min_lat),
            max_lat=float(max_lat),
            min_lon=float(min_lon),
            max_lon=float(max_lon),
            time_window=time_window
        )
        return [c.dict() for c in resp.candidates]


class RankPFZCandidatesTool(BaseTool):
    name = "rank_pfz_candidates"
    description = "Ranks PFZ candidates by composite environmental suitability score, proximity, confidence, and hazard status."
    purpose = "Multi-Criteria Decision Ranking"

    def __init__(self, pfz_engine: Optional[PFZIntelligenceEngine] = None):
        self.pfz_engine = pfz_engine or PFZIntelligenceEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "candidates": ToolParameter("candidates", "list", "List of PFZ candidates", required=True)
            }
        )

    async def _run(self, candidates: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        ranked = sorted(
            candidates,
            key=lambda c: (
                c.get("pfz_score", 0.0),
                c.get("confidence", {}).get("overall_confidence_percent", 0.0),
                -(c.get("distance_km") or 9999.0)
            ),
            reverse=True
        )
        return ranked


class EvaluatePFZEnvironmentTool(BaseTool):
    name = "evaluate_pfz_environment"
    description = "Fuses wave, wind, and tropical cyclone telemetry onto candidate regions to assign environmental hazard status."
    purpose = "Multi-Hazard Maritime Safety Fusion"

    def __init__(self, pfz_engine: Optional[PFZIntelligenceEngine] = None):
        self.pfz_engine = pfz_engine or PFZIntelligenceEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "lat": ToolParameter("lat", "float", "Target latitude", required=True),
                "lon": ToolParameter("lon", "float", "Target longitude", required=True)
            }
        )

    async def _run(
        self,
        lat: float,
        lon: float,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        active_cyclones: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        status, penalty, penalties = self.pfz_engine.fuse_hazard_context(
            float(lat), float(lon), weather_telemetry, active_cyclones
        )
        return {
            "hazard_status": status.value,
            "hazard_penalty": penalty,
            "penalties_applied": penalties
        }


class FindNearestPFZTool(BaseTool):
    name = "find_nearest_pfz"
    description = "Finds the closest verified PFZ candidate zone to a reference vessel or port coordinate."
    purpose = "Proximity-Based Target Discovery"

    def __init__(self, pfz_engine: Optional[PFZIntelligenceEngine] = None):
        self.pfz_engine = pfz_engine or PFZIntelligenceEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "lat": ToolParameter("lat", "float", "Reference latitude", required=True),
                "lon": ToolParameter("lon", "float", "Reference longitude", required=True)
            }
        )

    async def _run(
        self,
        lat: float,
        lon: float,
        time_window: Optional[TimeWindow] = None,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        active_cyclones: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        candidate = self.pfz_engine.find_nearest_candidate(
            ref_lat=float(lat),
            ref_lon=float(lon),
            time_window=time_window,
            weather_telemetry=weather_telemetry,
            active_cyclones=active_cyclones
        )
        return candidate.dict() if candidate else None


class FindPFZWithinRadiusTool(BaseTool):
    name = "find_pfz_within_radius"
    description = "Searches for all PFZ candidate zones within a specified geodesic radius (km) of a location."
    purpose = "Geodesic Radius Spatial Search"

    def __init__(self, pfz_engine: Optional[PFZIntelligenceEngine] = None):
        self.pfz_engine = pfz_engine or PFZIntelligenceEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "center_lat": ToolParameter("center_lat", "float", "Center latitude", required=True),
                "center_lon": ToolParameter("center_lon", "float", "Center longitude", required=True),
                "radius_km": ToolParameter("radius_km", "float", "Search radius in kilometers", required=True)
            }
        )

    async def _run(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        time_window: Optional[TimeWindow] = None,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        active_cyclones: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        candidates = self.pfz_engine.find_candidates_within_radius(
            center_lat=float(center_lat),
            center_lon=float(center_lon),
            radius_km=float(radius_km),
            time_window=time_window,
            weather_telemetry=weather_telemetry,
            active_cyclones=active_cyclones
        )
        return [c.dict() for c in candidates]
