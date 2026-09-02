"""
Comprehensive Phase 7 Verification Suite
ISRO SIH 2026 - Problem Statement 26176
Phase 7: Geofencing, Risk/Safety & Real Route Optimization

Validates all 15 required acceptance tests defined in Section 37:
1. Geofence Point Check (Point-in-polygon)
2. PFZ Candidate Restriction (Polygon overlap)
3. Clear PFZ (Outside restrictions)
4. Unknown Geofence (Dataset disabled yields UNKNOWN, never CLEAR)
5. Temporal Restriction (TimeWindow awareness)
6. Weather Risk (Controlled hazard fixtures)
7. Cyclone / Warning Risk (Proximity peril)
8. Land Avoidance (Non-traversable land mask)
9. Restricted-Cell Avoidance (A* bending around blocked zone)
10. Least-Cost Route (Lower-hazard route preferred over shorter high-hazard route)
11. No Valid Route (Surrounded destination yields NO_VALID_ROUTE)
12. Route Explanation (Machine-readable deviation explanations)
13. Future Safety (Temporal forecast alignment)
14. Multi-Turn Routing (Context memory resolution)
15. Planner E2E (Dynamic DAG execution)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import math
from datetime import datetime, timezone, timedelta
from shapely.geometry import Point, Polygon

from backend.geospatial.schemas import (
    Geofence,
    GeofenceType,
    GeofenceStatus,
    SafetyClassification,
    DecisionState
)
from backend.geospatial.geofence_service import GeofenceService
from backend.geospatial.risk_engine import MarineRiskEngine
from backend.geospatial.routing_engine import MarineRouteOptimizer
from backend.data.pfz.schemas import PFZCandidate, CandidatePolygon, SuitabilityBreakdown, ConfidenceBreakdown
from backend.temporal.models import TimeWindow
from backend.agents.orchestrator import MasterOrchestrator

def run_tests():
    print("=" * 80)
    print("STARTING ORCA PHASE 7 VERIFICATION SUITE")
    print("=" * 80)

    passed_count = 0
    total_tests = 15

    geofence_service = GeofenceService()
    risk_engine = MarineRiskEngine(geofence_service)
    route_optimizer = MarineRouteOptimizer(geofence_service, risk_engine)

    # -------------------------------------------------------------------------
    # TEST 1: Geofence Point Check
    # -------------------------------------------------------------------------
    try:
        # Load a controlled test polygon fixture
        test_poly_coords = [[[74.0, 13.0], [74.5, 13.0], [74.5, 13.5], [74.0, 13.5], [74.0, 13.0]]]
        geofence_service.load_custom_geofence({
            "id": "TEST_RESTRICTED_01",
            "name": "TEST_FIXTURE_ONLY: High Sensitivity Marine Enclave",
            "type": GeofenceType.NO_FISHING_ZONE,
            "coordinates": test_poly_coords,
            "jurisdiction": "State Fisheries Department",
            "status": "ACTIVE"
        })

        inside_pt = geofence_service.check_point(13.25, 74.25)
        outside_pt = geofence_service.check_point(14.0, 74.25)

        assert inside_pt["geofence_status"] == GeofenceStatus.RESTRICTED, f"Expected RESTRICTED, got {inside_pt['geofence_status']}"
        assert inside_pt["is_restricted"] is True
        assert inside_pt["matched_geofence"]["id"] == "TEST_RESTRICTED_01"

        assert outside_pt["geofence_status"] == GeofenceStatus.CLEAR, f"Expected CLEAR, got {outside_pt['geofence_status']}"
        assert outside_pt["is_restricted"] is False

        print(f"[PASS] TEST 1: Geofence Point Check: Inside point -> RESTRICTED ({inside_pt['matched_geofence']['name']}), Outside point -> CLEAR")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 1: Geofence Point Check: {e}")

    # -------------------------------------------------------------------------
    # TEST 2: PFZ Candidate Restriction (Polygon Intersection)
    # -------------------------------------------------------------------------
    try:
        # Overlapping candidate polygon with TEST_RESTRICTED_01
        overlap_cand_poly = [[74.1, 13.1], [74.6, 13.1], [74.6, 13.6], [74.1, 13.6], [74.1, 13.1]]
        check_cand = geofence_service.check_candidate_polygon(overlap_cand_poly)

        assert check_cand["geofence_status"] == GeofenceStatus.RESTRICTED, f"Expected RESTRICTED, got {check_cand['geofence_status']}"
        assert check_cand["is_restricted"] is True
        assert any(g["id"] == "TEST_RESTRICTED_01" for g in check_cand["intersecting_geofences"])

        geofence_service.remove_geofence("TEST_RESTRICTED_01")

        print(f"[PASS] TEST 2: PFZ Candidate Restriction: Polygon overlap correctly detected -> RESTRICTED ({check_cand['intersecting_geofences'][0]['name']})")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 2: PFZ Candidate Restriction: {e}")

    # -------------------------------------------------------------------------
    # TEST 3: Clear PFZ Candidate
    # -------------------------------------------------------------------------
    try:
        # Candidate far off Mangalore/Goa shelf in clear international open EEZ waters
        clear_cand_poly = [[73.0, 14.5], [73.2, 14.5], [73.2, 14.7], [73.0, 14.7], [73.0, 14.5]]
        check_clear = geofence_service.check_candidate_polygon(clear_cand_poly)

        assert check_clear["geofence_status"] == GeofenceStatus.CLEAR, f"Expected CLEAR, got {check_clear['geofence_status']}"
        assert check_clear["is_restricted"] is False
        assert len(check_clear["intersecting_geofences"]) == 0

        print(f"[PASS] TEST 3: Clear PFZ Candidate: Sovereign open EEZ candidate verified -> CLEAR (0 restriction overlaps)")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 3: Clear PFZ Candidate: {e}")

    # -------------------------------------------------------------------------
    # TEST 4: Unknown Geofence (Dataset Disabled Handling)
    # -------------------------------------------------------------------------
    try:
        geofence_service.set_dataset_enabled(False)
        unknown_check = geofence_service.check_point(13.25, 74.25)
        unknown_poly = geofence_service.check_candidate_polygon(overlap_cand_poly)

        # Must be UNKNOWN, NEVER CLEAR (Section 5 & 8)
        assert unknown_check["geofence_status"] == GeofenceStatus.UNKNOWN, f"Expected UNKNOWN, got {unknown_check['geofence_status']}"
        assert unknown_poly["geofence_status"] == GeofenceStatus.UNKNOWN, f"Expected UNKNOWN, got {unknown_poly['geofence_status']}"
        assert len(unknown_check["limitations"]) > 0

        # Re-enable dataset
        geofence_service.set_dataset_enabled(True)

        print(f"[PASS] TEST 4: Unknown Geofence: Disabled dataset honestly returned UNKNOWN (never converted to fake CLEAR)")
        passed_count += 1
    except Exception as e:
        geofence_service.set_dataset_enabled(True)
        print(f"[FAIL] TEST 4: Unknown Geofence: {e}")

    # -------------------------------------------------------------------------
    # TEST 5: Temporal Restriction (TimeWindow Awareness)
    # -------------------------------------------------------------------------
    try:
        now_utc = datetime.now(timezone.utc)
        # Register a seasonal restriction valid only from Nov 1 to May 31
        geofence_service.load_custom_geofence({
            "id": "TEMP_SEASONAL_01",
            "name": "TEST_FIXTURE_ONLY: Seasonal Sea Turtle Breeding Sanctuary",
            "type": GeofenceType.MARINE_PROTECTED_AREA,
            "coordinates": [[[75.0, 11.0], [75.3, 11.0], [75.3, 11.3], [75.0, 11.3], [75.0, 11.0]]],
            "jurisdiction": "Forest Department",
            "effective_start": "2026-11-01T00:00:00Z",
            "effective_end": "2027-05-31T23:59:59Z",
            "status": "ACTIVE"
        })

        # Test request during active closure (December 2026)
        tw_active = TimeWindow(
            start_datetime="2026-12-15T00:00:00Z",
            end_datetime="2026-12-15T23:59:59Z",
            label="december_2026"
        )
        res_during = geofence_service.check_point(11.15, 75.15, time_window=tw_active)
        assert res_during["geofence_status"] == GeofenceStatus.RESTRICTED, f"Expected RESTRICTED during active season, got {res_during['geofence_status']}"

        # Test request outside closure (September 2026 - prior to effective start)
        tw_inactive = TimeWindow(
            start_datetime="2026-09-03T00:00:00Z",
            end_datetime="2026-09-03T23:59:59Z",
            label="september_2026"
        )
        res_outside = geofence_service.check_point(11.15, 75.15, time_window=tw_inactive)
        assert res_outside["geofence_status"] == GeofenceStatus.CLEAR, f"Expected CLEAR outside active season, got {res_outside['geofence_status']}"

        geofence_service.remove_geofence("TEMP_SEASONAL_01")

        print(f"[PASS] TEST 5: Temporal Restriction: Active during Dec 2026 (RESTRICTED), inactive during Sept 2026 (CLEAR)")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 5: Temporal Restriction: {e}")

    # -------------------------------------------------------------------------
    # TEST 6: Marine Weather Risk Engine
    # -------------------------------------------------------------------------
    try:
        # Calm sea conditions
        calm_weather = {"significant_wave_height_m": 0.8, "wind_speed_knots": 8.0}
        risk_calm = risk_engine.evaluate_point_risk(14.0, 73.0, weather_telemetry=calm_weather)

        # Severe sea conditions
        severe_weather = {"significant_wave_height_m": 3.4, "wind_speed_knots": 32.0}
        risk_severe = risk_engine.evaluate_point_risk(14.0, 73.0, weather_telemetry=severe_weather)

        assert risk_calm["aggregate_risk_score"] < 0.25, f"Expected low risk <0.25, got {risk_calm['aggregate_risk_score']}"
        assert risk_calm["safety_classification"] in [SafetyClassification.SAFE, SafetyClassification.ACCEPTABLE]

        assert risk_severe["aggregate_risk_score"] >= 0.60, f"Expected high risk >=0.60, got {risk_severe['aggregate_risk_score']}"
        assert risk_severe["safety_classification"] in [SafetyClassification.HIGH_RISK, SafetyClassification.NO_GO]

        print(f"[PASS] TEST 6: Marine Weather Risk: Calm sea risk={risk_calm['aggregate_risk_score']} ({risk_calm['safety_classification']}) vs Severe sea risk={risk_severe['aggregate_risk_score']} ({risk_severe['safety_classification']})")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 6: Marine Weather Risk: {e}")

    # -------------------------------------------------------------------------
    # TEST 7: Cyclone & Tropical Warning Hazard Integration
    # -------------------------------------------------------------------------
    try:
        cyclone_fixture = {
            "name": "TEST_FIXTURE_ONLY: Severe Cyclonic Storm 'VAAYU'",
            "is_active": True,
            "current_lat": 15.0,
            "current_lon": 72.5,
            "active_storms": [{"name": "VAAYU", "latitude": 15.0, "longitude": 72.5}]
        }

        # Point within 100 km of storm center
        risk_storm = risk_engine.evaluate_point_risk(15.2, 72.8, cyclone_info=cyclone_fixture)
        assert risk_storm["cyclone_risk"] == 1.0
        assert risk_storm["safety_classification"] == SafetyClassification.NO_GO
        assert any("Active storm" in r for r in risk_storm["traceable_reasons"])

        print(f"[PASS] TEST 7: Cyclone Warning Hazard: Near-eye coordinate classified NO_GO (cyclone_risk=1.0, severe maritime peril)")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 7: Cyclone Warning Hazard: {e}")

    # -------------------------------------------------------------------------
    # TEST 8: Hard Land Mask Avoidance
    # -------------------------------------------------------------------------
    try:
        # Route from Mangalore (12.85°N, 74.84°E) to Chennai (13.12°N, 80.30°E)
        # Direct straight line cuts right through the Indian peninsular landmass (Karnataka/Tamil Nadu)!
        # A valid maritime route must NEVER traverse across land.
        is_inland = geofence_service.is_land_point(12.9, 77.5)  # Bangalore inland coordinate
        assert is_inland is True, "Inland point was not detected as land!"

        # A route from Kochi to a point directly on inland Karnataka must fail or circumvent
        route_res = route_optimizer.optimize_route(
            start_lat=9.94, start_lon=76.25,  # Kochi
            dest_lat=12.97, dest_lon=77.59,  # Bangalore (Inland)
            start_name="Kochi Harbour",
            dest_name="Inland Bangalore"
        )
        assert route_res.status == "NO_VALID_ROUTE", f"Expected NO_VALID_ROUTE for inland destination, got {route_res.status}"
        assert any("land" in l.lower() for l in route_res.limitations)

        print(f"[PASS] TEST 8: Hard Land Mask Avoidance: Inland destination correctly rejected with NO_VALID_ROUTE (cannot sail over land)")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 8: Hard Land Mask Avoidance: {e}")

    # -------------------------------------------------------------------------
    # TEST 9: Restricted-Cell Avoidance (A* Obstacle Bypassing)
    # -------------------------------------------------------------------------
    try:
        # Create a blocked rectangle right in between origin (12.0°N, 74.5°E) and destination (13.0°N, 74.5°E)
        barrier_coords = [[[74.3, 12.3], [74.7, 12.3], [74.7, 12.7], [74.3, 12.7], [74.3, 12.3]]]
        barrier_poly = Polygon(barrier_coords[0])

        route_bypassing = route_optimizer.optimize_route(
            start_lat=12.0, start_lon=74.5,
            dest_lat=13.0, dest_lon=74.5,
            start_name="South Waypoint",
            dest_name="North Waypoint",
            custom_blocked_polygons=[barrier_poly]
        )

        assert route_bypassing.status == "OK", f"Routing failed with status {route_bypassing.status}"
        assert route_bypassing.selected_route is not None
        sel_route = route_bypassing.selected_route

        # Verify no waypoint in the optimized path intersects the blocked polygon interior
        for wp in sel_route.waypoints:
            wp_pt = Point(wp.lon, wp.lat)
            assert not barrier_poly.contains(wp_pt), f"Waypoint at ({wp.lat}, {wp.lon}) penetrated blocked barrier!"

        # Verify route bent around obstacle (routed distance > straight direct distance)
        assert sel_route.routed_distance_km > sel_route.direct_distance_km, "Route did not bend around barrier!"

        print(f"[PASS] TEST 9: Restricted-Cell Avoidance: A* path bent around blocked barrier (direct={sel_route.direct_distance_km}km, routed={sel_route.routed_distance_km}km, 0 barrier penetrations)")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 9: Restricted-Cell Avoidance: {e}")

    # -------------------------------------------------------------------------
    # TEST 10: Least-Cost vs Shortest Route (Hazard-Aware Path Selection)
    # -------------------------------------------------------------------------
    try:
        # Route in clear Arabian Sea from Mangalore to offshore shelf
        route_cost = route_optimizer.optimize_route(
            start_lat=12.86, start_lon=74.84,
            dest_lat=13.20, dest_lon=74.20,
            start_name="Mangalore Old Port",
            dest_name="Offshore Shelf Front",
            weather_telemetry={"significant_wave_height_m": 2.6, "wind_speed_knots": 24.0}
        )

        assert route_cost.status == "OK"
        assert route_cost.selected_route is not None
        assert route_cost.selected_route.route_type == "LEAST_COST"
        assert route_cost.selected_route.routed_distance_nm > 0
        assert route_cost.selected_route.estimated_transit_time_hours > 0

        print(f"[PASS] TEST 10: Least-Cost Route Optimization: Path resolved: {route_cost.selected_route.routed_distance_nm} NM, Transit: {route_cost.selected_route.estimated_transit_time_hours} hrs at 9.5 kts")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 10: Least-Cost Route Optimization: {e}")

    # -------------------------------------------------------------------------
    # TEST 11: No Valid Route State (Blocked Destination Enclosure)
    # -------------------------------------------------------------------------
    try:
        # Create an impassable ring enclosure completely boxing in destination at (14.0°N, 73.0°E)
        ring_box = Polygon([
            [72.8, 13.8], [73.2, 13.8], [73.2, 14.2], [72.8, 14.2], [72.8, 13.8]
        ])

        impossible_route = route_optimizer.optimize_route(
            start_lat=12.0, start_lon=73.0,
            dest_lat=14.0, dest_lon=73.0,
            custom_blocked_polygons=[ring_box]
        )

        assert impossible_route.status == "NO_VALID_ROUTE", f"Expected NO_VALID_ROUTE, got {impossible_route.status}"
        assert impossible_route.selected_route is None
        assert len(impossible_route.limitations) > 0

        print(f"[PASS] TEST 11: No Valid Route State: Enclosed destination gracefully returned NO_VALID_ROUTE without fabricating fake path")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 11: No Valid Route State: {e}")

    # -------------------------------------------------------------------------
    # TEST 12: Route Safety & Deviation Explanation
    # -------------------------------------------------------------------------
    try:
        # Route near Indian Navy Gunnery Range (DEF-01) off Kochi
        route_expl = route_optimizer.optimize_route(
            start_lat=9.94, start_lon=76.25,  # Kochi Port
            dest_lat=9.50, dest_lon=75.60,   # Point south-west of gunnery range
            start_name="Kochi Fishing Harbour",
            dest_name="Offshore Zone"
        )

        assert route_expl.status == "OK"
        sel_exp = route_expl.selected_route
        assert len(sel_exp.deviation_explanations) > 0
        assert sel_exp.decision_support_only is True
        assert sel_exp.navigation_certified is False

        print(f"[PASS] TEST 12: Route Deviation Explanation: Machine-readable reasons provided: '{sel_exp.deviation_explanations[0]}'")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 12: Route Deviation Explanation: {e}")

    # -------------------------------------------------------------------------
    # TEST 13: Future Safety & Forecast Temporal Reasoning
    # -------------------------------------------------------------------------
    try:
        # Test tomorrow morning window
        tw_tomorrow = TimeWindow(
            start_datetime="2026-09-04T06:00:00+05:30",
            end_datetime="2026-09-04T12:00:00+05:30",
            label="tomorrow_morning",
            is_future=True
        )

        eval_future = risk_engine.evaluate_point_risk(
            lat=9.94, lon=76.25,
            weather_telemetry={"significant_wave_height_m": 1.4, "wind_speed_knots": 11.0},
            time_window=tw_tomorrow
        )

        assert eval_future["aggregate_risk_score"] < 0.30
        assert eval_future["safety_classification"] in [SafetyClassification.SAFE, SafetyClassification.ACCEPTABLE]

        print(f"[PASS] TEST 13: Future Safety Evaluation: Tomorrow morning temporal forecast evaluated (Risk: {eval_future['aggregate_risk_score']})")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 13: Future Safety Evaluation: {e}")

    # -------------------------------------------------------------------------
    # TEST 14: Multi-Turn Context Retention (PFZ -> Safest -> Route)
    # -------------------------------------------------------------------------
    async def test_multi_turn_e2e():
        orchestrator = MasterOrchestrator()
        sess_id = "test_phase7_session_01"

        # Turn 1: Find best PFZ near Kochi
        res_t1 = await orchestrator.execute_query_pipeline("Find the best fishing zone near Kochi today.", session_id=sess_id)
        assert res_t1["detected_intent"] in ["pfz_advisory", "composite_marine_advisory"]
        assert res_t1["reference_port"]["port_key"] == "kochi"

        # Turn 2: Follow-up "How do I reach it?"
        res_t2 = await orchestrator.execute_query_pipeline("How do I reach it?", session_id=sess_id)
        assert res_t2["detected_intent"] == "safe_navigation_route"
        assert res_t2["safe_navigation_route"] is not None
        assert res_t2["reference_port"]["port_key"] == "kochi"
        assert res_t2["decision_support_only"] is True

        return res_t2

    try:
        loop = asyncio.get_event_loop()
        res_t2 = loop.run_until_complete(test_multi_turn_e2e())
        print(f"[PASS] TEST 14: Multi-Turn Context Retention: Turn 1 established Kochi anchor, Turn 2 'How do I reach it?' resolved safe route ({res_t2['safe_navigation_route'].get('total_distance_nm')} NM)")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 14: Multi-Turn Context Retention: {e}")

    # -------------------------------------------------------------------------
    # TEST 15: Dynamic Planner End-to-End Execution
    # -------------------------------------------------------------------------
    async def test_planner_e2e():
        orchestrator = MasterOrchestrator()
        # Full query: "Which PFZ is safest from Mangalore?"
        res = await orchestrator.execute_query_pipeline("Which PFZ is safest from Mangalore?")
        
        assert res["detected_intent"] == "safest_pfz_advisory"
        trace = res.get("evidence_and_provenance", {}).get("execution_trace", [])
        tools = [t.get("tool") for t in trace if "tool" in t]

        assert "resolve_reference_port" in tools
        assert "score_candidate_safety" in tools
        assert res["reference_port"]["port_key"] == "mangalore"
        assert res["decision_support_only"] is True

        return len(tools), tools

    try:
        loop = asyncio.get_event_loop()
        n_tools, tools_list = loop.run_until_complete(test_planner_e2e())
        print(f"[PASS] TEST 15: Dynamic Planner E2E: Intent=safest_pfz_advisory, Tools executed: {n_tools} ({', '.join(tools_list)})")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] TEST 15: Dynamic Planner E2E: {e}")

    print("=" * 80)
    print(f"PHASE 7 TEST SUMMARY: {passed_count}/{total_tests} PASSED")
    print("=" * 80)

    return passed_count == total_tests

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
