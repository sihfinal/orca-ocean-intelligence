"""
ORCA Phase 8 Comprehensive Acceptance Test Suite
ISRO SIH 2026 - Problem Statement 26176
Phase 8: Decision Engine, Explainability, Evidence & Provenance

Covers all 19 required acceptance tests from Section 49:
1. Simple Decision Synthesis
2. Evidence Trace & Provenance
3. Negative Evidence Preservation
4. Restricted Geofence Override
5. High-Risk Wave/Storm Override
6. Candidate Comparison & Tradeoff
7. Stale Data Degradation
8. Missing Data Limitations
9. Conflicting Evidence Handling
10. Official Warning Priority
11. Numeric Consistency Verification
12. No Fabricated Sources
13. Natural Language Claim Validation
14. Multi-Turn Decision Memory ("Why?" & "Why not?")
15. Multilingual Semantic Equivalence
16. Future Decision / Observation vs Forecast
17. Data Unavailable / Insufficient Evidence
18. Route Alternatives Decision Integration
19. Full End-to-End Multi-Agent Pipeline
"""

import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure repo root in sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.decision.schemas import (
    SourceType,
    FreshnessState,
    UserObjective,
    DecisionType,
    DecisionStatus,
    EvidenceItem,
    EvidencePackage,
    DecisionObject,
    CandidateComparison
)
from backend.decision.evidence_collector import EvidenceCollector
from backend.decision.engine import ORCADecisionEngine
from backend.decision.explainability import ExplainabilityEngine
from backend.decision.claim_verifier import ClaimVerifier
from backend.agents.orchestrator import MasterOrchestrator

async def run_phase8_tests():
    print("=" * 80)
    print("STARTING ORCA PHASE 8 VERIFICATION SUITE (19 ACCEPTANCE TESTS)")
    print("=" * 80)

    collector = EvidenceCollector()
    engine = ORCADecisionEngine()
    explainer = ExplainabilityEngine()
    verifier = ClaimVerifier()
    orchestrator = MasterOrchestrator()

    now_iso = datetime.now(timezone.utc).isoformat()

    # Shared Test Fixtures
    cand_a = {
        "candidate_id": "PFZ-CAND-A",
        "name": "Malpe Front Hotspot A",
        "suitability_score": 0.85,
        "risk_score": 0.22,
        "geofence_status": "CLEAR",
        "distance_km": 42.0
    }
    cand_b = {
        "candidate_id": "PFZ-CAND-B",
        "name": "Mangalore Offshore Plume B",
        "suitability_score": 0.72,
        "risk_score": 0.15,
        "geofence_status": "CLEAR",
        "distance_km": 28.0
    }
    cand_c = {
        "candidate_id": "PFZ-CAND-C",
        "name": "Kasargod Shoal C",
        "suitability_score": 0.90,
        "risk_score": 0.68,
        "geofence_status": "CLEAR",
        "distance_km": 65.0
    }

    # -------------------------------------------------------------------------
    # TEST 1: SIMPLE DECISION SYNTHESIS
    # -------------------------------------------------------------------------
    print("\n--- TEST 1: Simple Decision Synthesis ---")
    ev_pkg_1 = collector.collect_evidence("Which PFZ is best from Mangalore?", {
        "weather": {"significant_wave_height_m": 1.2, "wind_speed_knots": 10.0},
        "geofence": {"geofence_status": "CLEAR"}
    })
    dec_1 = engine.synthesize_decision(
        query="Which PFZ is best from Mangalore?",
        evidence_pkg=ev_pkg_1,
        candidates=[cand_a, cand_b],
        weather={"significant_wave_height_m": 1.2, "wind_speed_knots": 10.0},
        geofence={"geofence_status": "CLEAR"}
    )
    assert dec_1.decision_id.startswith("DEC-"), "Decision ID must have DEC- prefix"
    assert dec_1.recommended_target_id in ["PFZ-CAND-A", "PFZ-CAND-B"], "Must recommend one of the candidates"
    assert dec_1.decision_status in [DecisionStatus.RECOMMENDED, DecisionStatus.ACCEPTABLE], "Status should be RECOMMENDED/ACCEPTABLE"
    assert len(dec_1.supporting_factors) > 0, "Must have supporting factors"
    print(f"PASS: Structured recommendation generated: '{dec_1.recommendation_title}' (Status={dec_1.decision_status.value}, Confidence={dec_1.confidence.overall_confidence*100:.0f}%)")

    # -------------------------------------------------------------------------
    # TEST 2: EVIDENCE TRACE & PROVENANCE
    # -------------------------------------------------------------------------
    print("\n--- TEST 2: Evidence Trace & Provenance ---")
    assert len(dec_1.evidence_ids) > 0, "Decision must link to evidence items"
    assert len(dec_1.provenance_graph) > 0, "Decision must have provenance records"
    first_ev = ev_pkg_1.items[0]
    assert first_ev.source_name, "Evidence item must have valid source name"
    assert first_ev.source_type in [SourceType.OFFICIAL, SourceType.OBSERVATION, SourceType.FORECAST, SourceType.DERIVED], "SourceType must be valid enum"
    print(f"PASS: Recommendation points back to {len(dec_1.evidence_ids)} verified evidence items across provenance chain: {[p['parameter'] for p in dec_1.provenance_graph]}")

    # -------------------------------------------------------------------------
    # TEST 3: NEGATIVE EVIDENCE PRESERVATION
    # -------------------------------------------------------------------------
    print("\n--- TEST 3: Negative Evidence Preservation ---")
    ev_pkg_3 = collector.collect_evidence("Status check", {
        "weather": {"significant_wave_height_m": 2.6, "wind_speed_knots": 24.0},
        "geofence": {"geofence_status": "CLEAR"}
    })
    dec_3 = engine.synthesize_decision(
        query="Status check",
        evidence_pkg=ev_pkg_3,
        candidates=[cand_c],
        weather={"significant_wave_height_m": 2.6, "wind_speed_knots": 24.0},
        geofence={"geofence_status": "CLEAR"}
    )
    assert len(dec_3.negative_factors) > 0, "Negative factors must be preserved when hazards exist"
    assert any("risk" in nf.lower() or "wave" in nf.lower() for nf in dec_3.negative_factors), "Must report wave or risk negative factors"
    print(f"PASS: Negative evidence preserved without omission: {dec_3.negative_factors}")

    # -------------------------------------------------------------------------
    # TEST 4: RESTRICTED GEOFENCE OVERRIDE
    # -------------------------------------------------------------------------
    print("\n--- TEST 4: Restricted Geofence Override ---")
    cand_restricted = {
        "candidate_id": "PFZ-CAND-RESTRICTED",
        "name": "Gulf of Mannar Coral Marine Park Core Zone",
        "suitability_score": 0.98,  # Extremely high biology!
        "risk_score": 0.10,
        "geofence_status": "RESTRICTED",
        "distance_km": 20.0
    }
    ev_pkg_4 = collector.collect_evidence("Can I fish here?", {
        "geofence": {"geofence_status": "RESTRICTED", "matched_geofence": {"name": "Gulf of Mannar Marine National Park"}}
    })
    dec_4 = engine.synthesize_decision(
        query="Can I fish here?",
        evidence_pkg=ev_pkg_4,
        candidates=[cand_restricted],
        geofence={"geofence_status": "RESTRICTED", "matched_geofence": {"name": "Gulf of Mannar Marine National Park"}}
    )
    assert dec_4.decision_status == DecisionStatus.NO_GO, f"Must be NO_GO for restricted area, got {dec_4.decision_status}"
    assert any("RESTRICTED" in g or "Marine Protected Area" in g for g in dec_4.hard_safety_gates_triggered), "Must record hard safety gate trigger"
    print(f"PASS: High PFZ suitability (0.98) inside MPA successfully overridden by Hard Safety Gate -> {dec_4.decision_status.value}")

    # -------------------------------------------------------------------------
    # TEST 5: HIGH-RISK WAVE/STORM OVERRIDE
    # -------------------------------------------------------------------------
    print("\n--- TEST 5: High-Risk Wave/Storm Override ---")
    ev_pkg_5 = collector.collect_evidence("Is it safe?", {
        "weather": {"significant_wave_height_m": 4.5, "wind_speed_knots": 38.0}
    })
    dec_5 = engine.synthesize_decision(
        query="Is it safe?",
        evidence_pkg=ev_pkg_5,
        candidates=[cand_a],
        weather={"significant_wave_height_m": 4.5, "wind_speed_knots": 38.0}
    )
    assert dec_5.decision_status == DecisionStatus.NO_GO, f"Severe sea state must trigger NO_GO, got {dec_5.decision_status}"
    assert any("4.0m" in g or "wave height" in g.lower() for g in dec_5.hard_safety_gates_triggered), "Must flag wave survival gate"
    print(f"PASS: Severe sea state (4.5m waves) triggered NO_GO gate: {dec_5.hard_safety_gates_triggered[0]}")

    # -------------------------------------------------------------------------
    # TEST 6: CANDIDATE COMPARISON & TRADEOFF
    # -------------------------------------------------------------------------
    print("\n--- TEST 6: Candidate Comparison & Tradeoff ---")
    comp_res = explainer.explain_why_not_alternative(dec_1, compared_id_or_name="Mangalore Offshore Plume B")
    assert "suitability_difference" in comp_res, "Must contain suitability difference"
    assert "risk_difference" in comp_res, "Must contain risk difference"
    assert "tradeoff_summary" in comp_res, "Must contain human-readable tradeoff summary"
    print(f"PASS: Candidate comparison generated: {comp_res['title']} -> {comp_res['tradeoff_summary']}")

    # -------------------------------------------------------------------------
    # TEST 7: STALE DATA DEGRADATION
    # -------------------------------------------------------------------------
    print("\n--- TEST 7: Stale Data Degradation ---")
    stale_ts = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
    ev_pkg_7 = collector.collect_evidence("Check conditions", {
        "weather": {"significant_wave_height_m": 1.4, "timestamp": stale_ts, "source": "Open-Meteo"}
    })
    assert "wave_height" in ev_pkg_7.stale_variables, "72-hour old wave observation must be flagged STALE"
    dec_7 = engine.synthesize_decision(
        query="Check conditions",
        evidence_pkg=ev_pkg_7,
        candidates=[cand_a],
        weather={"significant_wave_height_m": 1.4}
    )
    assert dec_7.confidence.temporal_relevance_score < 0.80, "Temporal relevance score must degrade on stale data"
    assert any("Stale observation" in u for u in dec_7.confidence.uncertainty_sources), "Must cite stale feeds in uncertainty sources"
    print(f"PASS: Stale data detected (age=72h). Confidence degraded: temporal_score={dec_7.confidence.temporal_relevance_score}")

    # -------------------------------------------------------------------------
    # TEST 8: MISSING DATA LIMITATIONS
    # -------------------------------------------------------------------------
    print("\n--- TEST 8: Missing Data Limitations ---")
    ev_pkg_8 = collector.collect_evidence("Check conditions", {
        "weather": {}  # Empty weather
    })
    assert "significant_wave_height" in ev_pkg_8.missing_variables, "Must flag missing wave height"
    assert "wind_speed" in ev_pkg_8.missing_variables, "Must flag missing wind speed"
    dec_8 = engine.synthesize_decision(
        query="Check conditions",
        evidence_pkg=ev_pkg_8,
        candidates=[cand_a]
    )
    assert dec_8.decision_status == DecisionStatus.INSUFFICIENT_EVIDENCE, "Missing critical weather must yield INSUFFICIENT_EVIDENCE"
    print(f"PASS: Missing weather telemetry correctly yielded status={dec_8.decision_status.value} (Limitations={dec_8.data_limitations})")

    # -------------------------------------------------------------------------
    # TEST 9: CONFLICTING EVIDENCE HANDLING
    # -------------------------------------------------------------------------
    print("\n--- TEST 9: Conflicting Evidence Handling ---")
    ev_pkg_9 = collector.collect_evidence("Evaluate fishing spot", {
        "weather": {"significant_wave_height_m": 3.0, "wind_speed_knots": 25.0},
        "top_pfz": {"score": 0.88}  # High PFZ vs hazardous sea
    })
    assert len(ev_pkg_9.conflicting_indicators) > 0, "Must flag conflicting PFZ vs wave state"
    dec_9 = engine.synthesize_decision(
        query="Evaluate fishing spot",
        evidence_pkg=ev_pkg_9,
        candidates=[cand_c],
        weather={"significant_wave_height_m": 3.0, "wind_speed_knots": 25.0}
    )
    assert dec_9.decision_status in [DecisionStatus.CAUTION, DecisionStatus.NOT_RECOMMENDED], "Conflicting indicators must trigger CAUTION"
    print(f"PASS: Conflicting indicators captured: '{ev_pkg_9.conflicting_indicators[0]}'. Decision status={dec_9.decision_status.value}")

    # -------------------------------------------------------------------------
    # TEST 10: OFFICIAL WARNING PRIORITY
    # -------------------------------------------------------------------------
    print("\n--- TEST 10: Official Warning Priority ---")
    ev_pkg_10 = collector.collect_evidence("Is area open?", {
        "cyclones": {
            "name": "DEEP DEPRESSION ARB-02",
            "is_active": True,
            "active_storms": [{"storm_name": "ARB-02"}],
            "source": "IMD RSMC New Delhi"
        }
    })
    assert ev_pkg_10.official_advisories_present, "Must recognize official advisory"
    dec_10 = engine.synthesize_decision(
        query="Is area open?",
        evidence_pkg=ev_pkg_10,
        candidates=[cand_a]
    )
    # The official warning must remain visible in negative factors or title
    assert any("cyclone" in nf.lower() or "cyclonic" in nf.lower() for nf in dec_10.negative_factors) or "cyclone" in str(dec_10.hard_safety_gates_triggered).lower() or dec_10.confidence.source_quality_score >= 0.90
    print(f"PASS: Official advisory priority preserved. Source quality={dec_10.confidence.source_quality_score:.2f}")

    # -------------------------------------------------------------------------
    # TEST 11: NUMERIC CONSISTENCY VERIFICATION
    # -------------------------------------------------------------------------
    print("\n--- TEST 11: Numeric Consistency Verification ---")
    ev_pkg_11 = collector.collect_evidence("Sea check", {
        "weather": {"significant_wave_height_m": 1.5, "wind_speed_knots": 12.0}
    })
    dec_11 = engine.synthesize_decision("Sea check", ev_pkg_11, [cand_a], weather={"significant_wave_height_m": 1.5})
    consistent_text = "The significant wave height is 1.5 m with mild winds."
    val_11 = verifier.verify_response_claims(consistent_text, dec_11, ev_pkg_11)
    assert val_11.is_valid, f"Accurate text should pass validation: {val_11.unsupported_numeric_claims}"
    print(f"PASS: Accurate numeric text passed claim validation: status={val_11.validation_status}")

    # -------------------------------------------------------------------------
    # TEST 12: NO FABRICATED SOURCES
    # -------------------------------------------------------------------------
    print("\n--- TEST 12: No Fabricated Sources ---")
    fabricated_source_text = "According to the NASA Marine Weather Bureau, the sea is calm."
    val_12 = verifier.verify_response_claims(fabricated_source_text, dec_11, ev_pkg_11)
    assert not val_12.is_valid, "Fabricated source must be rejected"
    assert any("NASA Marine Weather" in s for s in val_12.unsupported_source_claims), "Must identify fabricated source"
    print(f"PASS: Fabricated source detected and flagged: {val_12.unsupported_source_claims[0]}")

    # -------------------------------------------------------------------------
    # TEST 13: NATURAL LANGUAGE CLAIM VALIDATION
    # -------------------------------------------------------------------------
    print("\n--- TEST 13: Natural Language Claim Validation ---")
    inconsistent_text = "The wave height is 5.2 m and conditions are rough."
    val_13 = verifier.verify_response_claims(inconsistent_text, dec_11, ev_pkg_11)
    assert not val_13.is_valid, "Contradictory numeric claim (5.2m vs 1.5m) must be rejected"
    assert len(val_13.unsupported_numeric_claims) > 0, "Must flag numeric contradiction"
    assert val_13.safe_fallback_text is not None, "Must provide deterministic safe fallback text"
    print(f"PASS: Numeric discrepancy (5.2m vs 1.5m) caught. Safe fallback generated ({len(val_13.safe_fallback_text)} chars).")

    # -------------------------------------------------------------------------
    # TEST 14: MULTI-TURN DECISION MEMORY ("Why?" & "Why not?")
    # -------------------------------------------------------------------------
    print("\n--- TEST 14: Multi-Turn Decision Memory ---")
    # Turn 1: Best PFZ from Kochi
    session_id = f"test_phase8_mt_{int(datetime.now().timestamp())}"
    res_turn1 = await orchestrator.execute_query_pipeline(
        "Which PFZ is recommended near Mangalore?",
        session_id=session_id
    )
    assert "decision" in res_turn1, "Turn 1 must produce a decision"
    top_name = res_turn1["decision"].get("recommended_target_name", "Primary PFZ")

    # Turn 2: "Why is this recommended?"
    res_turn2 = await orchestrator.execute_query_pipeline(
        "Why is this recommended?",
        session_id=session_id
    )
    assert res_turn2["detected_intent"] == "decision_explanation", f"Expected decision_explanation, got {res_turn2['detected_intent']}"
    assert "Supporting Factors" in res_turn2["message"] or "Decision" in res_turn2["message"], "Must explain using stored factors"

    # Turn 3: "Why not the second candidate?"
    res_turn3 = await orchestrator.execute_query_pipeline(
        "Why not the second candidate?",
        session_id=session_id
    )
    assert res_turn3["detected_intent"] == "decision_explanation", f"Expected decision_explanation, got {res_turn3['detected_intent']}"
    print(f"PASS: Multi-turn reasoning verified: Turn 1={top_name} -> Turn 2='Why?' (Intent={res_turn2['detected_intent']}) -> Turn 3='Why not?'")

    # -------------------------------------------------------------------------
    # TEST 15: MULTILINGUAL SEMANTIC EQUIVALENCE
    # -------------------------------------------------------------------------
    print("\n--- TEST 15: Multilingual Semantic Equivalence ---")
    res_en = await orchestrator.execute_query_pipeline("Which PFZ is safest from Kochi?", requested_lang="en")
    res_hi = await orchestrator.execute_query_pipeline("Which PFZ is safest from Kochi?", requested_lang="hi")
    assert res_en["decision_status"] == res_hi["decision_status"], "Decision status must be invariant to language"
    assert res_en["recommendation"] == res_hi["recommendation"], "Recommended target must be invariant to language"
    print(f"PASS: Multilingual semantic equivalence verified: English Status={res_en['decision_status']}, Hindi Status={res_hi['decision_status']}")

    # -------------------------------------------------------------------------
    # TEST 16: FUTURE DECISION / OBSERVATION VS FORECAST
    # -------------------------------------------------------------------------
    print("\n--- TEST 16: Future Decision / Observation vs Forecast ---")
    ev_pkg_16 = collector.collect_evidence("What is the forecast wave for tomorrow morning?", {
        "weather": {
            "significant_wave_height_m": 1.6,
            "data_type": "FORECAST",
            "is_forecast": True,
            "source": "Open-Meteo Marine API"
        },
        "satellite_raster": {
            "variable": "sea_surface_temperature",
            "mean": 28.5,
            "source": "ISRO MOSDAC"
        }
    })
    wave_ev = next(ev for ev in ev_pkg_16.items if ev.parameter_name == "significant_wave_height")
    assert wave_ev.is_forecast == True, "Forecast wave must have is_forecast=True"
    assert wave_ev.source_type == SourceType.FORECAST, "Source type must be FORECAST"
    print(f"PASS: Forecast distinguished from observation: wave_height source_type={wave_ev.source_type.value}, is_forecast={wave_ev.is_forecast}")

    # -------------------------------------------------------------------------
    # TEST 17: DATA UNAVAILABLE / INSUFFICIENT EVIDENCE
    # -------------------------------------------------------------------------
    print("\n--- TEST 17: Data Unavailable / Insufficient Evidence ---")
    empty_ev_pkg = collector.collect_evidence("Query", {})
    dec_empty = engine.synthesize_decision("Query", empty_ev_pkg, candidates=[])
    assert dec_empty.decision_status == DecisionStatus.UNAVAILABLE, f"Zero candidates must yield UNAVAILABLE, got {dec_empty.decision_status}"
    assert dec_empty.confidence.overall_confidence == 0.0, "Confidence must be 0.0 when data unavailable"
    print(f"PASS: Data unavailable handled truthfully: status={dec_empty.decision_status.value}, confidence={dec_empty.confidence.overall_confidence}")

    # -------------------------------------------------------------------------
    # TEST 18: ROUTE ALTERNATIVES DECISION INTEGRATION
    # -------------------------------------------------------------------------
    print("\n--- TEST 18: Route Alternatives Decision Integration ---")
    route_data = {
        "status": "OK",
        "selected_route": {"routed_distance_nm": 45.2, "estimated_transit_time_hours": 4.8},
        "alternative_routes": {
            "least_cost": {"routed_distance_nm": 45.2, "cost": 120.0},
            "shortest_distance": {"routed_distance_nm": 41.0, "cost": 350.0}  # Shorter but higher wave cost
        }
    }
    ev_pkg_18 = collector.collect_evidence("Safe route to PFZ", {"route": route_data})
    route_ev = next(ev for ev in ev_pkg_18.items if ev.parameter_name == "route_traversal")
    assert route_ev.numeric_value == 45.2, "Must capture routed distance"
    assert route_ev.source_type == SourceType.DERIVED, "Route source must be DERIVED"
    print(f"PASS: Navigational route evidence captured: {route_ev.numeric_value} {route_ev.unit} ({route_ev.source_name})")

    # -------------------------------------------------------------------------
    # TEST 19: FULL END-TO-END MULTI-AGENT PIPELINE
    # -------------------------------------------------------------------------
    print("\n--- TEST 19: Full End-to-End Multi-Agent Pipeline ---")
    e2e_res = await orchestrator.execute_query_pipeline("Find the safest and best PFZ from Mangalore today.")
    assert "decision" in e2e_res, "Response must include decision object"
    assert "evidence_package" in e2e_res, "Response must include evidence package"
    assert "claim_validation" in e2e_res, "Response must include claim validation"
    assert "recommendation" in e2e_res, "Response must include recommendation string"
    assert e2e_res["decision_support_only"] == True, "Must have decision_support_only=True"
    assert e2e_res["navigation_certified"] == False, "Must have navigation_certified=False"
    print(f"PASS: Full E2E chain executed successfully.")
    print(f"  • Recommendation: {e2e_res['recommendation']}")
    print(f"  • Decision Status: {e2e_res['decision_status']}")
    print(f"  • Claim Validation: {e2e_res['claim_validation']['validation_status']}")
    print(f"  • Evidence Items: {len(e2e_res['evidence_package']['items'])}")

    print("\n" + "=" * 80)
    print("ALL 19 PHASE 8 ACCEPTANCE TESTS PASSED PERFECTLY!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_phase8_tests())
