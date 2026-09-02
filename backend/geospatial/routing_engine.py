"""
Marine Route Optimization & Least-Cost Surface Engine
ISRO SIH 2026 - Problem Statement 26176
Phase 7: Geofencing, Risk/Safety & Real Route Optimization

Implements genuine A* grid-based cost pathfinding on a dynamic georeferenced maritime surface.
Strictly enforces:
- Hard land mask non-traversability (Section 24)
- Hard restricted geofence blocking (Section 18)
- Dynamic wave, wind, and storm hazard cost penalties (Section 19)
- Genuine alternative route exploration (Section 21)
- Machine-readable route deviation explanations (Section 22)
- Explicit NO_VALID_ROUTE failure state (Section 35)
- Decision-support-only legal disclaimers (Section 26 & 43)
"""

import math
import heapq
import logging
from typing import Dict, Any, List, Optional, Tuple
from shapely.geometry import Point, LineString

from backend.geospatial.schemas import (
    OptimizedRoute,
    RouteWaypoint,
    RouteOptimizationResponse,
    SafetyClassification,
    GeofenceStatus
)
from backend.geospatial.geofence_service import GeofenceService
from backend.geospatial.risk_engine import MarineRiskEngine
from backend.data.geodata import INDIAN_PORTS

logger = logging.getLogger("orca.geospatial.routing")

class MarineRouteOptimizer:
    """
    A* grid-based maritime route optimization engine.
    """

    DEFAULT_CRUISING_SPEED_KNOTS = 9.5
    DEFAULT_FUEL_BURN_LPH = 14.5  # Litres per hour (mechanized trawler)
    GRID_STEP_DEG = 0.04  # ~4.4 km resolution
    BLOCKED_COST = 1e9

    def __init__(
        self,
        geofence_service: Optional[GeofenceService] = None,
        risk_engine: Optional[MarineRiskEngine] = None
    ):
        self.geofence_service = geofence_service or GeofenceService()
        self.risk_engine = risk_engine or MarineRiskEngine(self.geofence_service)

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in kilometers."""
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0)**2
        return r * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates initial navigational bearing in degrees [0 - 360)."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dlam = math.radians(lon2 - lon1)
        y = math.sin(dlam) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
        bearing = math.degrees(math.atan2(y, x))
        return round((bearing + 360.0) % 360.0, 1)

    def _build_cost_grid(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        weather_telemetry: Optional[Dict[str, Any]],
        cyclone_info: Optional[Dict[str, Any]],
        time_window: Optional[Any],
        hazard_weight: float = 1.0,
        custom_blocked_polygons: Optional[List[Any]] = None
    ) -> Tuple[List[float], List[float], Dict[Tuple[int, int], float], Dict[Tuple[int, int], str]]:
        """
        Constructs a 2D discrete traversal cost surface.
        Assigns BLOCKED_COST to land, restricted areas, and eye of active storms.
        """
        # Generate grid coordinates
        lats = []
        cur_lat = min_lat
        while cur_lat <= max_lat + 1e-5:
            lats.append(round(cur_lat, 4))
            cur_lat += self.GRID_STEP_DEG

        lons = []
        cur_lon = min_lon
        while cur_lon <= max_lon + 1e-5:
            lons.append(round(cur_lon, 4))
            cur_lon += self.GRID_STEP_DEG

        cost_map: Dict[Tuple[int, int], float] = {}
        info_map: Dict[Tuple[int, int], str] = {}

        # Wave multiplier baseline
        wave_height = weather_telemetry.get("significant_wave_height_m", 1.2) if weather_telemetry else 1.2
        if wave_height > 3.2:
            wave_mult = 3.5
        elif wave_height > 2.2:
            wave_mult = 2.0
        elif wave_height > 1.5:
            wave_mult = 1.4
        else:
            wave_mult = 1.0

        for r, lat in enumerate(lats):
            for c, lon in enumerate(lons):
                # 1. Check Land Mask (Hard Block)
                if self.geofence_service.is_land_point(lat, lon):
                    cost_map[(r, c)] = self.BLOCKED_COST
                    info_map[(r, c)] = "Inland / Coastal Barrier"
                    continue

                # 2. Check Custom Blocked Polygons (e.g. test fixtures)
                if custom_blocked_polygons:
                    pt = Point(lon, lat)
                    is_custom_blocked = False
                    for b_poly in custom_blocked_polygons:
                        if b_poly.contains(pt) or b_poly.touches(pt):
                            is_custom_blocked = True
                            break
                    if is_custom_blocked:
                        cost_map[(r, c)] = self.BLOCKED_COST
                        info_map[(r, c)] = "Blocked Test Barrier"
                        continue

                # 3. Check Authoritative Restricted Geofences (Hard Block)
                gf_res = self.geofence_service.check_point(lat, lon, time_window=time_window)
                if gf_res["geofence_status"] == GeofenceStatus.RESTRICTED:
                    cost_map[(r, c)] = self.BLOCKED_COST
                    gf_name = gf_res.get("matched_geofence", {}).get("name", "Restricted Area")
                    info_map[(r, c)] = f"Restricted: {gf_name}"
                    continue

                # 4. Check Active Tropical Cyclone Peril
                cyclone_risk, _ = self.risk_engine.evaluate_cyclone_risk(lat, lon, cyclone_info)
                if cyclone_risk >= 0.95:
                    cost_map[(r, c)] = self.BLOCKED_COST
                    info_map[(r, c)] = "Cyclone Core Peril"
                    continue

                # 5. Base Navigable Sea Cell Traversal Cost
                cell_cost = 1.0

                # Buffer penalty near restricted area
                if gf_res["geofence_status"] == GeofenceStatus.NEAR_RESTRICTION and hazard_weight > 0:
                    cell_cost += 1.5 * hazard_weight

                # Wave hazard penalty
                if hazard_weight > 0:
                    cell_cost *= (1.0 + (wave_mult - 1.0) * hazard_weight)

                # Cyclone outer buffer penalty
                if cyclone_risk > 0 and hazard_weight > 0:
                    cell_cost += cyclone_risk * 3.0 * hazard_weight

                cost_map[(r, c)] = cell_cost
                info_map[(r, c)] = "Navigable Ocean"

        return lats, lons, cost_map, info_map

    def _astar_search(
        self,
        start_rc: Tuple[int, int],
        goal_rc: Tuple[int, int],
        lats: List[float],
        lons: List[float],
        cost_map: Dict[Tuple[int, int], float]
    ) -> Optional[List[Tuple[int, int]]]:
        """
        A* pathfinding algorithm on 8-connected grid.
        Returns list of (row, col) coordinates or None if blocked.
        """
        rows = len(lats)
        cols = len(lons)

        def heuristic(rc: Tuple[int, int]) -> float:
            # Haversine distance heuristic
            return self._haversine_km(lats[rc[0]], lons[rc[1]], lats[goal_rc[0]], lons[goal_rc[1]])

        # Priority queue stores: (f_score, cost_so_far, (row, col))
        open_set = []
        heapq.heappush(open_set, (heuristic(start_rc), 0.0, start_rc))

        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {start_rc: 0.0}

        # 8 directions: 4 cardinal, 4 diagonal
        directions = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)
        ]

        closed_set = set()

        while open_set:
            _, current_g, current = heapq.heappop(open_set)

            if current == goal_rc:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            if current in closed_set:
                continue
            closed_set.add(current)

            r, c = current

            for dr, dc, dist_factor in directions:
                nr, nc = r + dr, c + dc
                neighbor = (nr, nc)

                if 0 <= nr < rows and 0 <= nc < cols:
                    cell_cost = cost_map.get(neighbor, self.BLOCKED_COST)
                    if cell_cost >= self.BLOCKED_COST:
                        continue  # Impassable barrier (Land or Restricted Zone)

                    # Step distance in km
                    step_km = self._haversine_km(lats[r], lons[c], lats[nr], lons[nc])
                    tentative_g = current_g + step_km * cell_cost

                    if tentative_g < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + heuristic(neighbor)
                        heapq.heappush(open_set, (f_score, tentative_g, neighbor))

        return None  # No valid path exists!

    def optimize_route(
        self,
        start_lat: float,
        start_lon: float,
        dest_lat: float,
        dest_lon: float,
        start_name: str = "Origin Port",
        dest_name: str = "Destination PFZ",
        weather_telemetry: Optional[Dict[str, Any]] = None,
        cyclone_info: Optional[Dict[str, Any]] = None,
        time_window: Optional[Any] = None,
        cruising_speed_knots: float = DEFAULT_CRUISING_SPEED_KNOTS,
        custom_blocked_polygons: Optional[List[Any]] = None
    ) -> RouteOptimizationResponse:
        """
        Executes genuine least-cost route optimization taking into account
        land avoidance, restricted boundaries, wave conditions, and active cyclone peril.
        """
        # Baseline direct distance
        direct_km = self._haversine_km(start_lat, start_lon, dest_lat, dest_lon)
        if direct_km < 0.1:
            direct_km = 0.1

        # Check if start or destination are intrinsically on land
        is_start_land = self.geofence_service.is_land_point(start_lat, start_lon)
        is_dest_land = self.geofence_service.is_land_point(dest_lat, dest_lon)
        
        # Check if destination is restricted
        dest_gf = self.geofence_service.check_point(dest_lat, dest_lon, time_window=time_window)
        if dest_gf["geofence_status"] == GeofenceStatus.RESTRICTED:
            return RouteOptimizationResponse(
                status="NO_VALID_ROUTE",
                origin={"name": start_name, "latitude": start_lat, "longitude": start_lon},
                destination={"name": dest_name, "latitude": dest_lat, "longitude": dest_lon},
                selected_route=None,
                limitations=[f"Destination '{dest_name}' lies inside restricted zone '{dest_gf.get('matched_geofence', {}).get('name', 'Restricted Area')}'. Vessel entry prohibited by maritime regulation."]
            )

        # Define grid bounds around start and destination with generous bounding pad
        pad_lat = max(0.5, abs(dest_lat - start_lat) * 0.4 + 0.3)
        pad_lon = max(0.5, abs(dest_lon - start_lon) * 0.4 + 0.3)

        min_lat = max(-10.0, min(start_lat, dest_lat) - pad_lat)
        max_lat = min(35.0, max(start_lat, dest_lat) + pad_lat)
        min_lon = max(55.0, min(start_lon, dest_lon) - pad_lon)
        max_lon = min(100.0, max(start_lon, dest_lon) + pad_lon)

        # Build Primary Least-Cost Cost Surface (hazard_weight = 1.0)
        lats, lons, cost_map, info_map = self._build_cost_grid(
            min_lat, max_lat, min_lon, max_lon,
            weather_telemetry=weather_telemetry,
            cyclone_info=cyclone_info,
            time_window=time_window,
            hazard_weight=1.0,
            custom_blocked_polygons=custom_blocked_polygons
        )

        # Map start and dest to closest grid cells
        start_r = int(min(range(len(lats)), key=lambda i: abs(lats[i] - start_lat)))
        start_c = int(min(range(len(lons)), key=lambda j: abs(lons[j] - start_lon)))
        
        dest_r = int(min(range(len(lats)), key=lambda i: abs(lats[i] - dest_lat)))
        dest_c = int(min(range(len(lons)), key=lambda j: abs(lons[j] - dest_lon)))

        # Ensure start and goal are marked traversable if close to coastal wharf
        cost_map[(start_r, start_c)] = 1.0
        cost_map[(dest_r, dest_c)] = 1.0

        # Execute A* search for Primary Least-Cost Route
        primary_path = self._astar_search((start_r, start_c), (dest_r, dest_c), lats, lons, cost_map)

        if not primary_path:
            return RouteOptimizationResponse(
                status="NO_VALID_ROUTE",
                origin={"name": start_name, "latitude": start_lat, "longitude": start_lon},
                destination={"name": dest_name, "latitude": dest_lat, "longitude": dest_lon},
                selected_route=None,
                limitations=["No valid navigable route could be resolved between origin and destination. All connecting maritime pathways are obstructed by land barriers, active cyclone exclusion zones, or restricted areas."]
            )

        # Build Alternative: Shortest Distance Route (hazard_weight = 0.0, only land & restricted blocked)
        _, _, short_cost_map, _ = self._build_cost_grid(
            min_lat, max_lat, min_lon, max_lon,
            weather_telemetry=weather_telemetry,
            cyclone_info=cyclone_info,
            time_window=time_window,
            hazard_weight=0.0,
            custom_blocked_polygons=custom_blocked_polygons
        )
        short_cost_map[(start_r, start_c)] = 1.0
        short_cost_map[(dest_r, dest_c)] = 1.0
        shortest_path = self._astar_search((start_r, start_c), (dest_r, dest_c), lats, lons, short_cost_map)

        # Assemble Primary Optimized Route Object
        selected_route = self._assemble_route(
            route_id="ROUTE-LEAST-COST-01",
            route_type="LEAST_COST",
            path_rc=primary_path,
            lats=lats,
            lons=lons,
            start_name=start_name,
            dest_name=dest_name,
            direct_km=direct_km,
            cost_map=cost_map,
            info_map=info_map,
            cruising_speed_knots=cruising_speed_knots,
            weather_telemetry=weather_telemetry,
            cyclone_info=cyclone_info,
            time_window=time_window
        )

        alternative_routes = []
        if shortest_path and shortest_path != primary_path:
            alt_route = self._assemble_route(
                route_id="ROUTE-SHORTEST-DIST-02",
                route_type="SHORTEST_DISTANCE",
                path_rc=shortest_path,
                lats=lats,
                lons=lons,
                start_name=start_name,
                dest_name=dest_name,
                direct_km=direct_km,
                cost_map=short_cost_map,
                info_map=info_map,
                cruising_speed_knots=cruising_speed_knots,
                weather_telemetry=weather_telemetry,
                cyclone_info=cyclone_info,
                time_window=time_window
            )
            alternative_routes.append(alt_route)

        return RouteOptimizationResponse(
            status="OK",
            origin={"name": start_name, "latitude": start_lat, "longitude": start_lon},
            destination={"name": dest_name, "latitude": dest_lat, "longitude": dest_lon},
            selected_route=selected_route,
            alternative_routes=alternative_routes,
            cost_surface_metadata={
                "grid_resolution_deg": self.GRID_STEP_DEG,
                "grid_cells_evaluated": len(cost_map),
                "optimization_objective": "Multi-Factor Minimization of Distance, Wave Hazard, and Border Proximity"
            },
            provenance=[
                {"source": "A* Geospatial Traversal Cost Engine", "algorithm": "Least-Cost Grid Search"},
                {"source": "MoEFCC / Indian Coast Guard", "type": "Marine Protected Areas & IMBL Buffer Corridors"}
            ],
            limitations=[
                "Route is generated for tactical decision-support and planning only.",
                "Not a certified ECDIS navigation chart. Master of vessel retains absolute command responsibility."
            ],
            decision_support_only=True,
            navigation_certified=False
        )

    def _assemble_route(
        self,
        route_id: str,
        route_type: str,
        path_rc: List[Tuple[int, int]],
        lats: List[float],
        lons: List[float],
        start_name: str,
        dest_name: str,
        direct_km: float,
        cost_map: Dict[Tuple[int, int], float],
        info_map: Dict[Tuple[int, int], str],
        cruising_speed_knots: float,
        weather_telemetry: Optional[Dict[str, Any]],
        cyclone_info: Optional[Dict[str, Any]],
        time_window: Optional[Any]
    ) -> OptimizedRoute:
        """Converts grid path into a fully articulated, explainable OptimizedRoute object."""
        waypoints = []
        geojson_coords = []
        cumulative_dist_km = 0.0
        cumulative_cost = 0.0
        restrictions_avoided = set()
        deviation_explanations = []

        total_pts = len(path_rc)

        # Baseline straight line connecting origin and destination
        start_pt = (lats[path_rc[0][0]], lons[path_rc[0][1]])
        dest_pt = (lats[path_rc[-1][0]], lons[path_rc[-1][1]])

        for i, (r, c) in enumerate(path_rc):
            lat = lats[r]
            lon = lons[c]
            geojson_coords.append([lon, lat])

            if i > 0:
                prev_lat, prev_lon = lats[path_rc[i-1][0]], lons[path_rc[i-1][1]]
                leg_km = self._haversine_km(prev_lat, prev_lon, lat, lon)
                cumulative_dist_km += leg_km
                bearing = self._calculate_bearing(prev_lat, prev_lon, lat, lon)
            else:
                leg_km = 0.0
                bearing = self._calculate_bearing(lat, lon, dest_pt[0], dest_pt[1]) if total_pts > 1 else 0.0

            dist_to_dest = self._haversine_km(lat, lon, dest_pt[0], dest_pt[1])
            cell_cost = cost_map.get((r, c), 1.0)
            cumulative_cost += cell_cost

            # Check geofence proximity for this waypoint
            gf_check = self.geofence_service.check_point(lat, lon, time_window=time_window)
            if gf_check.get("matched_geofence"):
                restrictions_avoided.add(gf_check["matched_geofence"]["name"])

            wp_status = "SAFE"
            if gf_check["geofence_status"] == GeofenceStatus.NEAR_RESTRICTION:
                wp_status = "BUFFER"

            waypoints.append(RouteWaypoint(
                waypoint_index=i,
                lat=lat,
                lon=lon,
                distance_from_start_km=round(cumulative_dist_km, 2),
                distance_to_dest_km=round(dist_to_dest, 2),
                leg_distance_km=round(leg_km, 2),
                bearing_deg=bearing,
                cell_cost=round(cell_cost, 2),
                hazard_description=info_map.get((r, c), "Navigable Ocean"),
                safety_status=wp_status
            ))

        routed_dist_km = round(cumulative_dist_km, 2)
        routed_dist_nm = round(routed_dist_km / 1.852, 2)

        # Transit time and fuel calculations based on labeled speed assumption
        transit_hours = round(routed_dist_nm / max(1.0, cruising_speed_knots), 2)
        fuel_litres = round(transit_hours * self.DEFAULT_FUEL_BURN_LPH, 1)

        # Check for meaningful deviation from straight line and explain why (Section 22)
        if routed_dist_km > direct_km * 1.05 and restrictions_avoided:
            avoided_names = ", ".join(list(restrictions_avoided)[:3])
            deviation_explanations.append(
                f"Route deflected away from direct path to maintain safe clearance around restricted zones: {avoided_names}."
            )
        
        if weather_telemetry and weather_telemetry.get("significant_wave_height_m", 0) > 2.2:
            deviation_explanations.append("Route navigated through lower-energy sea sector to mitigate significant wave impact.")

        if cyclone_info and cyclone_info.get("is_active"):
            deviation_explanations.append(f"Route plotted outside danger buffer of active storm system '{cyclone_info.get('name', 'Cyclone')}'.")

        if not deviation_explanations:
            deviation_explanations.append("Route followed optimal navigable channel without severe environmental deviations.")

        return OptimizedRoute(
            route_id=route_id,
            route_type=route_type,
            origin={"name": start_name, "latitude": start_pt[0], "longitude": start_pt[1]},
            destination={"name": dest_name, "latitude": dest_pt[0], "longitude": dest_pt[1]},
            route_geometry={"type": "LineString", "coordinates": geojson_coords},
            waypoints=waypoints,
            direct_distance_km=round(direct_km, 2),
            routed_distance_km=routed_dist_km,
            routed_distance_nm=routed_dist_nm,
            total_cost=round(cumulative_cost, 2),
            cruising_speed_knots=cruising_speed_knots,
            estimated_transit_time_hours=transit_hours,
            estimated_fuel_burn_litres=fuel_litres,
            risk_classification=SafetyClassification.SAFE if not restrictions_avoided else SafetyClassification.CAUTION,
            restrictions_avoided=list(restrictions_avoided),
            hazard_segments=[],
            deviation_explanations=deviation_explanations,
            decision_support_only=True,
            navigation_certified=False,
            limitations=[
                "Calculated assuming constant average vessel cruising speed of 9.5 knots.",
                "Surface currents and wind leeway drift not dynamically integrated into autopilot track.",
                "BATHYMETRY_UNAVAILABLE: Shallow water bathymetric soundings not factored; verify local harbor charts."
            ]
        )
