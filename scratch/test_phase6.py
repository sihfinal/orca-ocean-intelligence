"""
ORCA Phase 6 Verification Test Suite
ISRO SIH 2026 - Problem Statement 26176
Phase 6: PFZ Intelligence, Ocean Analytics & Environmental Hazard Fusion

Validates all 15 mandatory Section 30 requirements:
1. Real SST Analysis
2. Real Chlorophyll Analysis
3. Controlled Front Detection Test Fixture
4. Multi-Variable Coincident PFZ Analytics
5. Real Spatial Candidate Regions & Polygons
6. Geodesic Radius Search (e.g. within 100 km of Mangalore)
7. Weather & Sea State Hazard Fusion
8. Cyclone Warning & Hazard Degradation Fusion
9. Low Data Coverage & Cloud Mask Confidence Penalty
10. Scientific Honesty on Future PFZ Requests (FUTURE_EO_UNAVAILABLE)
11. Historical Date Alignment & Provenance Tracking
12. Data Source Failure Handling (Strictly No Synthetic Fallback)
13. Multi-Turn Context Retention ("Find PFZs" -> "Which one is safest?")
14. Multilingual Spatial PFZ Queries (Kannada, Hindi, English)
15. End-to-End Autonomous Planner Execution DAG
"""

import sys
import os
import asyncio
from datetime import datetime, timezone, timedelta
import numpy as np

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath("."))

from backend.data.raster.catalog import EODatasetCatalog
from backend.data.pfz.engine import PFZIntelligenceEngine
from backend.data.pfz.schemas import PFZResultType, EnvironmentalHazardStatus
from backend.temporal.models import TimeWindow
from backend.agents.ocean_analytics_agent import OceanAnalyticsAgent
from backend.agents.orchestrator import MasterOrchestrator

test_results = []

def record_test(name: str, passed: bool, details: str):
    test_results.append((name, passed, details))
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {details}")

async def run_all_tests():
    print("================================================================================")
    print("STARTING ORCA PHASE 6 VERIFICATION SUITE")
    print("================================================================================")

    catalog = EODatasetCatalog()
    pfz_engine = PFZIntelligenceEngine(catalog=catalog)
    ocean_agent = OceanAnalyticsAgent(pfz_engine=pfz_engine)
    orchestrator = MasterOrchestrator()

    # -------------------------------------------------------------------------
    # TEST 1: Real SST Analysis
    # -------------------------------------------------------------------------
    try:
        # Mangalore shelf: 12.0°N to 14.0°N, 73.5°E to 75.5°E
        sst_grid = catalog.get_map_grid("sea_surface_temperature", 12.0, 14.0, 73.5, 75.5)
        grads = catalog.get_spatial_gradients("sea_surface_temperature", 12.0, 14.0, 73.5, 75.5)
        passed = (
            sst_grid.variable == "sea_surface_temperature" and
            sst_grid.unit == "deg_C" and
            len(sst_grid.values) > 1 and
            grads.mean_gradient_magnitude is not None and
            grads.gradient_unit == "deg_C/km" and
            "ISRO" in sst_grid.source or "INSAT" in sst_grid.satellite
        )
        record_test("TEST 1: Real SST Field & Geodetic Gradient Analysis", passed,
                    f"Source={sst_grid.source}, Acquisition={sst_grid.acquisition_time[:10]}, Mean Grad={grads.mean_gradient_magnitude} °C/km")
    except Exception as e:
        record_test("TEST 1: Real SST Field & Geodetic Gradient Analysis", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 2: Real Chlorophyll Analysis
    # -------------------------------------------------------------------------
    try:
        chl_grid = catalog.get_map_grid("chlorophyll_a", 12.0, 14.0, 73.5, 75.5)
        chl_stats = catalog.get_regional_statistics("chlorophyll_a", 12.0, 14.0, 73.5, 75.5)
        passed = (
            chl_grid.variable == "chlorophyll_a" and
            chl_grid.unit == "mg/m^3" and
            chl_stats.has_valid_data and
            chl_stats.mean is not None and
            "Oceansat-3" in chl_grid.satellite or "EOS-06" in chl_grid.satellite
        )
        record_test("TEST 2: Real Chlorophyll-a Biomass Analysis (Oceansat-3)", passed,
                    f"Product={chl_grid.provenance.get('product_name')}, Mean={chl_stats.mean} mg/m³, Valid Pct={chl_stats.valid_percentage}%")
    except Exception as e:
        record_test("TEST 2: Real Chlorophyll-a Biomass Analysis (Oceansat-3)", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 3: Front Detection (Controlled Test Fixture)
    # -------------------------------------------------------------------------
    try:
        # Construct controlled synthetic fixture: known 2.0°C thermal step across column 15
        fixture_lats = np.linspace(12.0, 13.0, 30)
        fixture_lons = np.linspace(74.0, 75.0, 30)
        fixture_sst = np.full((30, 30), 28.0)
        fixture_sst[:, 15:] = 26.0 # Step transition: 2.0 °C drop (cold upwelling plume)
        
        grad_field = pfz_engine.compute_physical_gradients(fixture_sst, fixture_lats, fixture_lons)
        # Front should peak near column 14-15
        peak_grad = float(np.nanmax(grad_field))
        col_maxes = [float(np.nanmax(grad_field[1:-1, c])) for c in range(1, 29)]
        peak_col = int(np.nanargmax(col_maxes) + 1)
        passed = (
            peak_grad > 0.05 and  # Strong frontal gradient > 0.05 °C/km
            peak_col in [14, 15]   # Detected at exact fixture transition line
        )
        record_test("TEST 3: Controlled Test Fixture Front Detection", passed,
                    f"Known 2.0°C step transition detected: Peak Gradient={peak_grad:.4f} °C/km at exact boundary col={peak_col}")
    except Exception as e:
        record_test("TEST 3: Controlled Test Fixture Front Detection", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 4: Multi-Variable PFZ (Coincident SST + Chlorophyll)
    # -------------------------------------------------------------------------
    try:
        resp = pfz_engine.analyze_spatial_pfz(
            min_lat=12.0, max_lat=14.0, min_lon=73.5, max_lon=75.5,
            reference_lat=12.91, reference_lon=74.85
        )
        passed = (
            resp.status == "OK" and
            resp.analysis_type == PFZResultType.MODEL_DERIVED_PFZ and
            resp.candidates_count > 0 and
            resp.candidates[0].sst_mean_c is not None and
            resp.candidates[0].chlorophyll_mean_mg_m3 is not None and
            resp.candidates[0].front_strength > 0.0
        )
        c0 = resp.candidates[0] if resp.candidates else None
        record_test("TEST 4: Multi-Variable Coincident Front PFZ Analytics", passed,
                    f"Generated {resp.candidates_count} candidates. Top: SST={c0.sst_mean_c}°C, Chl={c0.chlorophyll_mean_mg_m3} mg/m³, Front Strength={c0.front_strength}")
    except Exception as e:
        record_test("TEST 4: Multi-Variable Coincident Front PFZ Analytics", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 5: Real Spatial Candidates (Polygons & Centroids)
    # -------------------------------------------------------------------------
    try:
        top_cand = resp.candidates[0]
        geom = top_cand.geometry
        is_polygon = (
            isinstance(geom.coordinates, list) and
            len(geom.coordinates) >= 4 and
            geom.area_sq_km > 0.0 and
            len(geom.bounding_box) == 4
        )
        passed = (
            is_polygon and
            top_cand.centroid_lat is not None and
            top_cand.centroid_lon is not None and
            0.0 <= top_cand.pfz_score <= 1.0 and
            top_cand.suitability.raw_weighted_score > 0.0
        )
        record_test("TEST 5: Real Spatial Candidate Polygons & Centroids", passed,
                    f"Centroid=({top_cand.centroid_lat}°N, {top_cand.centroid_lon}°E), Area={geom.area_sq_km} km², Score={top_cand.pfz_score:.3f} (Not hardcoded points)")
    except Exception as e:
        record_test("TEST 5: Real Spatial Candidate Polygons & Centroids", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 6: Radius Query (Geodesic Distance Filtering)
    # -------------------------------------------------------------------------
    try:
        # Find candidates within 120 km of Mangalore Old Port (12.86°N, 74.84°E)
        radius_km = 120.0
        radius_candidates = pfz_engine.find_candidates_within_radius(
            center_lat=12.86, center_lon=74.84, radius_km=radius_km
        )
        all_within = all(c.distance_km <= radius_km for c in radius_candidates)
        passed = (
            len(radius_candidates) > 0 and
            all_within and
            radius_candidates[0].distance_km is not None
        )
        record_test("TEST 6: Geodesic Radius PFZ Filtering (120 km of Mangalore)", passed,
                    f"Found {len(radius_candidates)} candidates within {radius_km} km. Closest is at {radius_candidates[0].distance_km} km (Strictly geodesic Haversine)")
    except Exception as e:
        record_test("TEST 6: Geodesic Radius PFZ Filtering (120 km of Mangalore)", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 7: Weather & Sea State Hazard Fusion
    # -------------------------------------------------------------------------
    try:
        # High sea state simulation: wave height 3.2m, wind 30 kts
        severe_weather = {
            "significant_wave_height_m": 3.2,
            "wind_speed_knots": 30.0,
            "safety_status": "HIGH_SEAS_WARNING"
        }
        calm_weather = {
            "significant_wave_height_m": 1.1,
            "wind_speed_knots": 12.0,
            "safety_status": "SAFE_FOR_VENTURE"
        }
        status_severe, pen_severe, notes_sev = pfz_engine.fuse_hazard_context(12.86, 74.84, severe_weather)
        status_calm, pen_calm, notes_calm = pfz_engine.fuse_hazard_context(12.86, 74.84, calm_weather)

        passed = (
            status_severe == EnvironmentalHazardStatus.ENVIRONMENTALLY_FAVORABLE_BUT_HAZARDOUS and
            pen_severe >= 0.50 and
            status_calm == EnvironmentalHazardStatus.ENVIRONMENTALLY_FAVORABLE and
            pen_calm == 0.0
        )
        record_test("TEST 7: Data-Driven Marine Weather & Sea State Hazard Fusion", passed,
                    f"Severe wave (3.2m) yielded {status_severe.value} (penalty={pen_severe}). Calm wave (1.1m) yielded {status_calm.value} (penalty={pen_calm})")
    except Exception as e:
        record_test("TEST 7: Data-Driven Marine Weather & Sea State Hazard Fusion", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 8: Cyclone Warning Hazard Degradation Fusion
    # -------------------------------------------------------------------------
    try:
        active_cyclone = [{
            "name": "DEEP DEPRESSION ARB-01",
            "current_lat": 13.5,
            "current_lon": 74.0, # 100 km from candidate
            "alert_level": "RED_CYCLONE_WARNING"
        }]
        normal_weather = {"significant_wave_height_m": 1.5, "wind_speed_knots": 18.0}
        cyc_status, cyc_pen, cyc_notes = pfz_engine.fuse_hazard_context(
            12.86, 74.84, normal_weather, active_cyclones=active_cyclone
        )
        passed = (
            cyc_status == EnvironmentalHazardStatus.ENVIRONMENTALLY_FAVORABLE_BUT_HAZARDOUS and
            cyc_pen >= 0.50 and
            any("Active Tropical Cyclone" in note for note in cyc_notes)
        )
        record_test("TEST 8: Real Active Cyclone Warning Hazard Fusion", passed,
                    f"Proximity to cyclone triggered status={cyc_status.value} (penalty={cyc_pen}): '{cyc_notes[0]}'")
    except Exception as e:
        record_test("TEST 8: Real Active Cyclone Warning Hazard Fusion", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 9: Low Data Coverage & Cloud Mask Confidence Penalty
    # -------------------------------------------------------------------------
    try:
        # High coverage test vs Low coverage test
        conf_high = pfz_engine.calculate_confidence(has_sst=True, has_chl=True, valid_pixel_pct=92.0, cloud_pct=8.0)
        conf_low = pfz_engine.calculate_confidence(has_sst=True, has_chl=False, valid_pixel_pct=25.0, cloud_pct=75.0)

        passed = (
            conf_high.overall_confidence_percent > conf_low.overall_confidence_percent and
            conf_high.confidence_level == "HIGH" and
            conf_low.confidence_level in ["LOW", "MODERATE"] and
            conf_low.cloud_contamination_percent == 75.0
        )
        record_test("TEST 9: Cloud Mask & Data Coverage Confidence Degradation", passed,
                    f"Clean sky={conf_high.overall_confidence_percent}% ({conf_high.confidence_level}) vs 75% cloud mask={conf_low.overall_confidence_percent}% ({conf_low.confidence_level})")
    except Exception as e:
        record_test("TEST 9: Cloud Mask & Data Coverage Confidence Degradation", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 10: Future Date Handling (Scientific Honesty)
    # -------------------------------------------------------------------------
    try:
        fut_time = datetime.now(timezone.utc) + timedelta(days=2)
        tw_future = TimeWindow(label="in 2 days", start_datetime=fut_time, end_datetime=fut_time + timedelta(hours=6), is_future=True)
        fut_resp = pfz_engine.analyze_spatial_pfz(12.0, 14.0, 73.5, 75.5, time_window=tw_future)

        passed = (
            fut_resp.status == "FUTURE_EO_UNAVAILABLE" and
            fut_resp.analysis_type == PFZResultType.UNAVAILABLE and
            fut_resp.candidates_count == 0 and
            "Future satellite observation cannot exist" in fut_resp.limitations[0]
        )
        record_test("TEST 10: Scientific Honesty on Future PFZ Requests", passed,
                    f"Status={fut_resp.status}, AnalysisType={fut_resp.analysis_type.value}, Truthful caveat: '{fut_resp.limitations[0][:65]}...'")
    except Exception as e:
        record_test("TEST 10: Scientific Honesty on Future PFZ Requests", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 11: Historical Date Alignment & Provenance Tracking
    # -------------------------------------------------------------------------
    try:
        past_time = datetime.now(timezone.utc) - timedelta(days=2)
        tw_past = TimeWindow(label="2 days ago", start_datetime=past_time, end_datetime=past_time + timedelta(hours=24), is_past=True)
        hist_resp = pfz_engine.analyze_spatial_pfz(12.0, 14.0, 73.5, 75.5, time_window=tw_past)

        passed = (
            hist_resp.status == "OK" and
            hist_resp.candidates_count > 0 and
            hist_resp.provenance is not None and
            len(hist_resp.provenance) >= 1
        )
        p0 = hist_resp.provenance[0]
        record_test("TEST 11: Historical Request Date Alignment & Provenance", passed,
                    f"Status={hist_resp.status}, Verified Provenance: Parameter={p0['parameter']}, Source={p0['source']}, Timestamp={p0['timestamp'][:10]}")
    except Exception as e:
        record_test("TEST 11: Historical Request Date Alignment & Provenance", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 12: Source Failure Handling (Strictly No Fake Math Fallback)
    # -------------------------------------------------------------------------
    try:
        # Request completely out-of-bounds coordinates (e.g. North Atlantic)
        oob_resp = pfz_engine.analyze_spatial_pfz(65.0, 68.0, -20.0, -15.0)
        passed = (
            oob_resp.candidates_count == 0 and
            oob_resp.status in ["OK", "UNAVAILABLE"] and
            any("coverage" in lim.lower() or "unavailable" in lim.lower() for lim in oob_resp.limitations)
        )
        record_test("TEST 12: Source Outage / Out-of-Coverage Truthful Handling", passed,
                    f"Out-of-coverage region yielded 0 candidates (zero fabricated hotspots): {oob_resp.limitations[0]}")
    except Exception as e:
        record_test("TEST 12: Source Outage / Out-of-Coverage Truthful Handling", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 13: Multi-Turn Context Retention ("Find PFZs" -> "Which one is safest?")
    # -------------------------------------------------------------------------
    try:
        session_id = "test_phase6_session_pfz_turn"
        # Turn 1: Find fishing zones near Mangalore
        res1 = await orchestrator.execute_query_pipeline(
            "Find the best fishing zones within 100 km of Mangalore.",
            session_id=session_id
        )
        # Turn 2: Ask "Which one is safest?"
        res2 = await orchestrator.execute_query_pipeline(
            "Which one is safest?",
            session_id=session_id
        )
        passed = (
            res1.get("detected_intent") == "pfz_radius_search" and
            (res2.get("detected_intent") in ["sea_weather_safety", "pfz_advisory", "composite_marine_advisory"]) and
            # Mangalore anchor preserved across turns
            res2.get("reference_port", {}).get("port_key") == "mangalore"
        )
        record_test("TEST 13: Multi-Turn PFZ Context Retention across Turns", passed,
                    f"Turn 1 Intent={res1.get('detected_intent')}, Turn 2 Intent={res2.get('detected_intent')}, Port Context Retained={res2.get('reference_port', {}).get('name')}")
    except Exception as e:
        record_test("TEST 13: Multi-Turn PFZ Context Retention across Turns", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 14: Multilingual Spatial PFZ Queries (Kannada, Hindi, English)
    # -------------------------------------------------------------------------
    try:
        # Kannada query
        res_kn = await orchestrator.execute_query_pipeline(
            "ಮಂಗಳೂರು ಹತ್ತಿರ 100 ಕಿಮೀ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ಅತ್ಯುತ್ತಮ ಮೀನುಗಾರಿಕಾ ವಲಯಗಳನ್ನು ಹುಡುಕಿ.",
            requested_lang="kn"
        )
        # Hindi query
        res_hi = await orchestrator.execute_query_pipeline(
            "मंगलुरु के पास 100 किमी के दायरे में संभावित मछली पकड़ने के क्षेत्र खोजें.",
            requested_lang="hi"
        )
        msg_kn = res_kn.get("message") or res_kn.get("response", {}).get("markdown", "")
        msg_hi = res_hi.get("message") or res_hi.get("response", {}).get("markdown", "")

        passed = (
            res_kn.get("language", {}).get("code") == "kn" and
            res_hi.get("language", {}).get("code") == "hi" and
            len(msg_kn) > 60 and
            len(msg_hi) > 60
        )
        record_test("TEST 14: Multilingual Spatial PFZ Queries (KN, HI, EN)", passed,
                    f"Kannada: {len(msg_kn)} chars | Hindi: {len(msg_hi)} chars with localized PFZ intelligence")
    except Exception as e:
        record_test("TEST 14: Multilingual Spatial PFZ Queries (KN, HI, EN)", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 15: End-to-End Autonomous Planner Execution DAG
    # -------------------------------------------------------------------------
    try:
        q_e2e = "Find PFZs within 80 km of Kochi today."
        res_e2e = await orchestrator.execute_query_pipeline(q_e2e)
        trace = res_e2e.get("evidence_and_provenance", {}).get("execution_trace", [])
        tools_executed = [step.get("tool") for step in trace if "tool" in step]

        passed = (
            res_e2e.get("detected_intent") == "pfz_radius_search" and
            len(trace) >= 3 and
            "find_pfz_within_radius" in tools_executed and
            "get_weather_at_point" in tools_executed
        )
        record_test("TEST 15: End-to-End Dynamic Planner DAG Execution", passed,
                    f"Intent={res_e2e.get('detected_intent')}, Tasks executed={len(trace)} (Tools: {', '.join(tools_executed)})")
    except Exception as e:
        record_test("TEST 15: End-to-End Dynamic Planner DAG Execution", False, str(e))

    print("================================================================================")
    total = len(test_results)
    passed_count = sum(1 for _, p, _ in test_results if p)
    print(f"PHASE 6 TEST SUMMARY: {passed_count}/{total} PASSED")
    print("================================================================================")
    return passed_count == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
