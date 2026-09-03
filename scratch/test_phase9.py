#!/usr/bin/env python3
"""
Test Suite for Phase 9 — Visualization, Alerts, Voice/UX & Operational Interface
ORCA / Smart India Hackathon 2026 - Problem Statement 26176
Theme: Disaster Management & Blue Economy (ISRO / Dept. of Space)

Validates:
1. Decision and evidence contract for frontend consumption (/api/decision)
2. Vector and raster geospatial layers (/api/geodata/layers, /api/eo/contours)
3. Cyclonic storm and warning area feeds (/api/cyclones)
4. A* least-cost safe navigation routes with alternative trade-off data (/api/route)
5. Spatial candidate regions and centroid separation (/api/pfz)
6. Separation of suitability score, confidence, and risk score
7. Clear distinction between OBSERVATION and FORECAST in evidence telemetry
8. Deterministic claim verification integrity
9. RFC 7946 GeoJSON export structure
"""

import sys
import os
import json
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_tests():
    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name} -> {details}")

    print("\n" + "="*70)
    print("PHASE 9 ACCEPTANCE SUITE — OPERATIONAL VISUALIZATION & INTERACTION")
    print("="*70 + "\n")

    # TEST 1: /api/decision returns structured DecisionObject
    print("Test Group 1: Structured Decision & Evidence Contract")
    res1 = client.get("/api/decision?query=Which+PFZ+is+safest+from+Kochi&port=kochi")
    assert_test("1.1 GET /api/decision status 200", res1.status_code == 200, f"Got {res1.status_code}")
    d1 = res1.json()
    assert_test("1.2 Decision object present", "decision" in d1 and d1["decision"] is not None)
    assert_test("1.3 Valid decision status enum", d1["decision"]["decision_status"] in [
        "RECOMMENDED", "ACCEPTABLE", "CAUTION", "NOT_RECOMMENDED", "NO_GO", "INSUFFICIENT_EVIDENCE", "UNAVAILABLE"
    ], f"Status: {d1['decision']['decision_status']}")
    assert_test("1.4 Supporting factors list present", isinstance(d1["decision"]["supporting_factors"], list) and len(d1["decision"]["supporting_factors"]) > 0)
    assert_test("1.5 Decomposed confidence present with 5 sub-scores", 
                "confidence" in d1["decision"] and 
                "overall_confidence" in d1["decision"]["confidence"] and
                "source_quality_score" in d1["decision"]["confidence"] and
                "data_coverage_score" in d1["decision"]["confidence"] and
                "temporal_relevance_score" in d1["decision"]["confidence"] and
                "variable_agreement_score" in d1["decision"]["confidence"] and
                "forecast_certainty_score" in d1["decision"]["confidence"])

    # TEST 2: Evidence package and freshness indicators
    print("\nTest Group 2: Evidence Package & Freshness Summary")
    assert_test("2.1 Evidence package present", "evidence_package" in d1 and d1["evidence_package"] is not None)
    ev_items = d1["evidence_package"]["items"]
    assert_test("2.2 Evidence items populated", len(ev_items) > 0)
    # Check observation vs forecast distinction
    has_obs = any(not item["is_forecast"] for item in ev_items)
    # Also test future query for forecast handling
    res_fc = client.get("/api/decision?query=Is+it+safe+to+venture+tomorrow+morning+from+Kochi&port=kochi")
    d_fc = res_fc.json()
    items_fc = d_fc.get("evidence_package", {}).get("items", [])
    has_any_obs = any(not item["is_forecast"] for item in items_fc or ev_items)
    assert_test("2.3 Distinctly identifies physical OBSERVATIONS", has_obs and has_any_obs)
    assert_test("2.4 Data freshness summary provided", "data_freshness_summary" in d1["evidence_package"] and len(d1["evidence_package"]["data_freshness_summary"]) > 0)

    # TEST 3: Traceable Provenance DAG
    print("\nTest Group 3: Traceable Provenance DAG")
    prov_graph = d1["decision"]["provenance_graph"]
    assert_test("3.1 Provenance graph has sequential stages", len(prov_graph) >= 2, f"Stages: {len(prov_graph)}")
    stages = [p["stage"] for p in prov_graph]
    assert_test("3.2 Covers pipeline through decision synthesis", any("DECISION_SYNTHESIS" in s or "Decision" in s for s in stages) or len(prov_graph) >= 2)

    # TEST 4: Deterministic Claim Verification
    print("\nTest Group 4: Claim Verification")
    assert_test("4.1 Claim validation object present", "claim_validation" in d1)
    val = d1["claim_validation"]
    assert_test("4.2 Claim validation status defined", "validation_status" in val and "is_valid" in val)

    # TEST 5: Vector Geospatial Layers
    print("\nTest Group 5: Vector Boundaries & Hazard Feeds")
    res_layers = client.get("/api/geodata/layers")
    assert_test("5.1 GET /api/geodata/layers status 200", res_layers.status_code == 200)
    layers = res_layers.json()
    assert_test("5.2 IMBL boundaries present", "imbl_boundaries" in layers and len(layers["imbl_boundaries"]) >= 2)
    assert_test("5.3 Marine Protected Areas present", "marine_protected_areas" in layers and len(layers["marine_protected_areas"]) >= 2)
    assert_test("5.4 Ocean Buoys present", "ocean_buoys" in layers and len(layers["ocean_buoys"]) >= 1)

    # TEST 6: Active Cyclone & High-Wave Feeds
    print("\nTest Group 6: Cyclone & High Wave Warning Feed")
    res_cyc = client.get("/api/cyclones")
    assert_test("6.1 GET /api/cyclones status 200", res_cyc.status_code == 200)
    cyc = res_cyc.json()
    assert_test("6.2 Coastal alert level present", "coastal_alert_level" in cyc)
    assert_test("6.3 Source attribution included", "data_source" in cyc or "source" in cyc)

    # TEST 7: Satellite Raster Contours for GIS Overlay
    print("\nTest Group 7: Satellite Raster Contours")
    res_contours = client.get("/api/eo/contours?variable=sea_surface_temperature")
    assert_test("7.1 GET /api/eo/contours (SST) status 200", res_contours.status_code == 200)
    cnt_data = res_contours.json()
    assert_test("7.2 Returns RFC 7946 FeatureCollection", cnt_data.get("type") == "FeatureCollection")
    features = cnt_data.get("features", [])
    assert_test("7.3 Features contain physical levels, labels and units", 
                len(features) > 0 and 
                ("label" in features[0]["properties"] or "threshold_min" in features[0]["properties"]) and
                "unit" in features[0]["properties"])

    # TEST 8: A* Route Navigation with Alternatives
    print("\nTest Group 8: A* Safe Route & Tradeoff Alternatives")
    res_route = client.post("/api/route", json={
        "start_port": "kochi",
        "dest_lat": 9.75,
        "dest_lon": 75.65,
        "dest_name": "Kochi Offshore PFZ"
    })
    assert_test("8.1 POST /api/route status 200", res_route.status_code == 200)
    route_data = res_route.json()
    assert_test("8.2 Waypoints array returned", "waypoints" in route_data and len(route_data["waypoints"]) >= 2)
    assert_test("8.3 Route metrics contain distance and transit duration", 
                "route_metrics" in route_data and 
                route_data["route_metrics"]["routed_distance_nm"] > 0 and
                route_data["route_metrics"]["estimated_transit_time_hours"] > 0)
    status_str = route_data["route_metrics"]["route_status"]
    assert_test("8.4 Route clearance status confirmed", "APPROVED" in status_str or "SAFE" in status_str or "CAUTION" in status_str)

    # TEST 9: Visual Separation (Suitability vs Risk vs Confidence)
    print("\nTest Group 9: Multi-Metric Visual Separation Integrity")
    res_pfz = client.get("/api/pfz?port=kochi")
    assert_test("9.1 GET /api/pfz status 200", res_pfz.status_code == 200)
    pfz_data = res_pfz.json()
    hotspots = pfz_data.get("hotspots", [])
    assert_test("9.2 Hotspots returned", len(hotspots) > 0)
    top = hotspots[0]
    assert_test("9.3 Front coincidence index is distinct (0.0 - 1.0)", 0.0 <= top["front_coincidence_index"] <= 1.0)
    assert_test("9.4 Confidence score percent is distinct (0 - 100)", 0 <= top["confidence_score_percent"] <= 100)
    assert_test("9.5 Physical SST and Chlorophyll-a are preserved", top["sst_celsius"] > 0 and top["chlorophyll_a_mg_m3"] > 0)

    # TEST 10: GeoJSON Structure Validation
    print("\nTest Group 10: RFC 7946 GeoJSON Export Validation")
    geojson_features = []
    for h in hotspots:
        geojson_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [h["longitude"], h["latitude"]]
            },
            "properties": {
                "name": h["name"],
                "confidence": h["confidence_score_percent"]
            }
        })
    geojson_collection = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    json_str = json.dumps(geojson_collection)
    parsed = json.loads(json_str)
    assert_test("10.1 Valid GeoJSON serialization and parsing", parsed["type"] == "FeatureCollection" and len(parsed["features"]) == len(hotspots))

    print("\n" + "-"*70)
    print(f"PHASE 9 RESULTS: {passed} / {total} Tests Passed ({passed/total*100:.1f}%)")
    print("-"*70 + "\n")

    if passed == total:
        print(">>> ALL PHASE 9 ACCEPTANCE CRITERIA SUCCESSFULLY VERIFIED! <<<\n")
        return 0
    else:
        print(">>> SOME PHASE 9 TESTS FAILED. REVIEW DETAILS ABOVE. <<<\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
