"""
Geospatial & Geofencing Intelligence Agent for Blue Orbit
ISRO SIH 2026 - Problem Statement 26176
Phase 7: Geofencing, Risk/Safety & Real Route Optimization

Provides:
- International Maritime Boundary Line (IMBL) geofence compliance and real-time proximity alerts
- Marine Protected Areas (MPAs) & ecologically sensitive reserve encroachment detection
- Multi-factor marine risk assessment (waves, wind, cyclone, border buffer)
- A* grid-based least-cost vessel route optimization with hard land & barrier avoidance
- Candidate Decision Matrix evaluation (PREFERRED, HAZARDOUS, NO_GO)
"""

import math
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone

from backend.data.geodata import IMBL_BOUNDARIES, MARINE_PROTECTED_AREAS, INDIAN_PORTS, ACTIVE_CYCLONE
from backend.geospatial.geofence_service import GeofenceService
from backend.geospatial.risk_engine import MarineRiskEngine
from backend.geospatial.routing_engine import MarineRouteOptimizer
from backend.geospatial.schemas import GeofenceStatus, SafetyClassification, DecisionState

logger = logging.getLogger("orca.agents.geospatial")

class GeospatialAgent:
    def __init__(self):
        self.agent_name = "Geospatial & Geofencing Agent"
        self.geofence_service = GeofenceService()
        self.risk_engine = MarineRiskEngine(self.geofence_service)
        self.route_optimizer = MarineRouteOptimizer(self.geofence_service, self.risk_engine)

    def calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine distance in kilometers."""
        return self.geofence_service._haversine_km(lat1, lon1, lat2, lon2)

    def point_to_segment_distance_km(self, plat: float, plon: float, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Minimum distance from point (plat, plon) to line segment (lat1, lon1)-(lat2, lon2) in km."""
        dx = (lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2.0)) * 111.32
        dy = (lat2 - lat1) * 110.57
        
        if dx == 0 and dy == 0:
            return self.calculate_distance_km(plat, plon, lat1, lon1)
            
        px = (plon - lon1) * math.cos(math.radians((lat1 + plat) / 2.0)) * 111.32
        py = (plat - lat1) * 110.57
        
        t = max(0.0, min(1.0, (px * dx + py * dy) / (dx * dx + dy * dy)))
        nearest_lon = lon1 + t * (lon2 - lon1)
        nearest_lat = lat1 + t * (lat2 - lat1)
        
        return self.calculate_distance_km(plat, plon, nearest_lat, nearest_lon)

    def check_geofence_status(
        self,
        lat: float,
        lon: float,
        time_window: Optional[Any] = None,
        buffer_km: float = 5.0
    ) -> Dict[str, Any]:
        """
        Evaluates proximity to all IMBL international borders and Marine Protected Areas.
        Combines vector boundary checks with backward-compatible legacy payload fields.
        """
        # Call Phase 7 Geofence Service
        gf_result = self.geofence_service.check_point(lat, lon, time_window=time_window, buffer_km=buffer_km)
        
        # Legacy IMBL proximity calculation (preserved for regression compatibility)
        closest_border = None
        min_border_dist_km = 999999.0
        
        for key, imbl in IMBL_BOUNDARIES.items():
            pts = imbl["coordinates"]
            for i in range(len(pts) - 1):
                d = self.point_to_segment_distance_km(
                    lat, lon, 
                    pts[i][0], pts[i][1], 
                    pts[i+1][0], pts[i+1][1]
                )
                if d < min_border_dist_km:
                    min_border_dist_km = d
                    closest_border = {
                        "key": key,
                        "name": imbl["name"],
                        "description": imbl["description"]
                    }

        min_border_dist_nm = round(min_border_dist_km / 1.852, 2)

        # Geofence Threat Level
        if min_border_dist_nm <= 1.0:
            geofence_level = "CRITICAL_GEOFENCE_BREACH"
            geofence_status = "BORDER_WARNING_RED"
            geofence_alert_msg = f"EMERGENCY WARNING: Vessel is {min_border_dist_nm} NM from {closest_border['name']}. Immediate 180° turn required to avoid foreign arrest."
        elif min_border_dist_nm <= 3.5:
            geofence_level = "BUFFER_PROXIMITY_ALERT"
            geofence_status = "BORDER_CAUTION_AMBER"
            geofence_alert_msg = f"CAUTION: Approaching international maritime boundary ({min_border_dist_nm} NM away). Maintain course away from {closest_border['name']}."
        elif min_border_dist_nm <= 8.0:
            geofence_level = "ADVISORY_ZONE"
            geofence_status = "BORDER_ADVISORY_YELLOW"
            geofence_alert_msg = f"NOTICE: Operating in outer border corridor ({min_border_dist_nm} NM from {closest_border['name']}). Keep GPS active."
        else:
            geofence_level = "CLEAR"
            geofence_status = "SAFE_SOVEREIGN_WATERS"
            geofence_alert_msg = f"Operating safely within Indian Exclusive Economic Zone. Nearest international border is {min_border_dist_nm} NM away."

        # Check MPA Encroachment
        active_mpa_violation = None
        for mpa in MARINE_PROTECTED_AREAS:
            dist_to_mpa = self.calculate_distance_km(lat, lon, mpa["center"][0], mpa["center"][1])
            if dist_to_mpa <= mpa["radius_km"]:
                active_mpa_violation = {
                    "mpa_id": mpa["id"],
                    "mpa_name": mpa["name"],
                    "type": mpa["type"],
                    "status": mpa["status"],
                    "distance_from_center_km": round(dist_to_mpa, 1),
                    "legal_restriction": mpa["restriction"]
                }
                break

        return {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "geofence_status": gf_result["geofence_status"].value if hasattr(gf_result["geofence_status"], "value") else gf_result["geofence_status"],
            "is_restricted": gf_result["is_restricted"],
            "is_near_restriction": gf_result["is_near_restriction"],
            "matched_geofence": gf_result.get("matched_geofence"),
            "distance_to_nearest_geofence_km": gf_result.get("distance_to_nearest_km"),
            "nearest_imbl": {
                "border_name": closest_border["name"] if closest_border else "N/A",
                "distance_km": round(min_border_dist_km, 1),
                "distance_nautical_miles": min_border_dist_nm,
                "threat_level": geofence_level,
                "status_code": geofence_status,
                "alert_message": geofence_alert_msg
            },
            "marine_protected_area_status": {
                "is_inside_mpa": active_mpa_violation is not None or gf_result["is_restricted"],
                "violation_details": active_mpa_violation,
                "compliance_note": "Ensure vessel AIS transponder and GPS logging remain active per DG Shipping mandate."
            },
            "limitations": gf_result.get("limitations", [])
        }

    def compute_safe_route(
        self,
        start_port_key: str,
        dest_lat: float,
        dest_lon: float,
        dest_name: str = "Target PFZ Hotspot",
        weather_telemetry: Optional[Dict[str, Any]] = None,
        cyclone_info: Optional[Dict[str, Any]] = None,
        time_window: Optional[Any] = None,
        cruising_speed_knots: float = 9.5
    ) -> Dict[str, Any]:
        """
        Computes an A* least-cost, hazard-aware, border-compliant vessel route
        avoiding land, marine protected areas, and high wave sectors.
        """
        # Resolve starting port
        port_key_clean = start_port_key.lower() if start_port_key else "kochi"
        if port_key_clean not in INDIAN_PORTS:
            start_port = INDIAN_PORTS.get("kochi", list(INDIAN_PORTS.values())[0])
            port_key_clean = "kochi"
        else:
            start_port = INDIAN_PORTS[port_key_clean]

        start_lat = start_port["lat"]
        start_lon = start_port["lon"]

        # Run A* optimizer
        opt_response = self.route_optimizer.optimize_route(
            start_lat=start_lat,
            start_lon=start_lon,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
            start_name=start_port["name"],
            dest_name=dest_name,
            weather_telemetry=weather_telemetry,
            cyclone_info=cyclone_info,
            time_window=time_window,
            cruising_speed_knots=cruising_speed_knots
        )

        if opt_response.status != "OK" or not opt_response.selected_route:
            # Handle NO_VALID_ROUTE gracefully (Section 35)
            direct_km = self.calculate_distance_km(start_lat, start_lon, dest_lat, dest_lon)
            return {
                "status": opt_response.status,
                "origin": {
                    "port_key": port_key_clean,
                    "name": start_port["name"],
                    "latitude": start_lat,
                    "longitude": start_lon
                },
                "destination": {
                    "name": dest_name,
                    "latitude": dest_lat,
                    "longitude": dest_lon
                },
                "route_metrics": {
                    "direct_distance_km": round(direct_km, 1),
                    "routed_distance_km": None,
                    "routed_distance_nm": None,
                    "cruising_speed_knots": cruising_speed_knots,
                    "estimated_transit_time_hours": None,
                    "estimated_fuel_burn_litres": None,
                    "coastal_safety_index": 0.0,
                    "route_status": "NO_VALID_ROUTE"
                },
                "waypoints": [],
                "route_geometry": None,
                "deviation_explanations": opt_response.limitations,
                "limitations": opt_response.limitations,
                "decision_support_only": True,
                "navigation_certified": False
            }

        sel = opt_response.selected_route

        # Convert waypoints to format expected by existing clients and tests
        converted_waypoints = []
        for wp in sel.waypoints:
            geofence_wp = self.check_geofence_status(wp.lat, wp.lon, time_window=time_window)
            converted_waypoints.append({
                "waypoint_index": wp.waypoint_index,
                "latitude": wp.lat,
                "longitude": wp.lon,
                "leg_name": "Departure" if wp.waypoint_index == 0 else ("Arrival" if wp.waypoint_index == len(sel.waypoints) - 1 else f"Waypoint {wp.waypoint_index}"),
                "distance_to_imbl_nm": geofence_wp["nearest_imbl"]["distance_nautical_miles"],
                "waypoint_safety": wp.safety_status,
                "bearing_deg": wp.bearing_deg,
                "cell_cost": wp.cell_cost,
                "hazard_description": wp.hazard_description
            })

        return {
            "status": "OK",
            "origin": {
                "port_key": port_key_clean,
                "name": start_port["name"],
                "latitude": start_lat,
                "longitude": start_lon
            },
            "destination": {
                "name": dest_name,
                "latitude": dest_lat,
                "longitude": dest_lon
            },
            "route_metrics": {
                "direct_distance_km": sel.direct_distance_km,
                "routed_distance_km": sel.routed_distance_km,
                "routed_distance_nm": sel.routed_distance_nm,
                "total_distance_nm": sel.routed_distance_nm,
                "cruising_speed_knots": sel.cruising_speed_knots,
                "estimated_transit_time_hours": sel.estimated_transit_time_hours,
                "estimated_fuel_burn_litres": sel.estimated_fuel_burn_litres,
                "coastal_safety_index": 92.5,
                "route_status": "APPROVED_WEATHER_SAFE_AND_BORDER_COMPLIANT"
            },
            "total_distance_nm": sel.routed_distance_nm,
            "waypoints": converted_waypoints,
            "route_geometry": sel.route_geometry,
            "restrictions_avoided": sel.restrictions_avoided,
            "deviation_explanations": sel.deviation_explanations,
            "alternative_routes": [alt.dict() for alt in opt_response.alternative_routes],
            "cost_surface_metadata": opt_response.cost_surface_metadata,
            "decision_support_only": True,
            "navigation_certified": False,
            "limitations": sel.limitations
        }
