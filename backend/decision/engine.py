"""
Core Decision Engine for ORCA
ISRO SIH 2026 - Problem Statement 26176
Phase 8: Decision Engine, Explainability, Evidence & Provenance
"""

import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta

from backend.decision.schemas import (
    SourceType,
    FreshnessState,
    UserObjective,
    DecisionType,
    DecisionStatus,
    ConfidenceDecomposition,
    CandidateComparison,
    DecisionObject,
    EvidencePackage
)
from backend.geospatial.schemas import GeofenceStatus, SafetyClassification

class ORCADecisionEngine:
    """
    Multi-objective, evidence-backed decision engine for ORCA.
    Separates environmental suitability from operational risk, enforces hard safety gates,
    evaluates tradeoffs between alternatives, and builds inspectable confidence decomposition.
    """

    def __init__(self):
        pass

    def _determine_objective(self, query: str, user_objective: Optional[UserObjective] = None) -> UserObjective:
        """Infers user objective from query semantics if not explicitly provided."""
        if user_objective:
            return user_objective

        q = query.lower()
        if any(k in q for k in ["safest", "minimum risk", "safely", "surakshit", "avoid danger"]):
            return UserObjective.MINIMIZE_RISK
        elif any(k in q for k in ["closest", "nearest", "minimum distance", "least fuel", "kam door"]):
            return UserObjective.MINIMIZE_DISTANCE
        elif any(k in q for k in ["avoid border", "avoid restricted", "avoid mpa", "border safe"]):
            return UserObjective.AVOID_RESTRICTIONS
        elif any(k in q for k in ["maximum catch", "highest catch", "best tuna", "highest pfz", "highest score"]):
            return UserObjective.MAXIMIZE_SUITABILITY
        else:
            return UserObjective.BALANCE_SUITABILITY_AND_SAFETY

    def synthesize_decision(
        self,
        query: str,
        evidence_pkg: EvidencePackage,
        candidates: List[Dict[str, Any]],
        weather: Optional[Dict[str, Any]] = None,
        geofence: Optional[Dict[str, Any]] = None,
        route: Optional[Dict[str, Any]] = None,
        safety_evals: Optional[List[Dict[str, Any]]] = None,
        user_objective: Optional[UserObjective] = None,
        decision_type: DecisionType = DecisionType.PFZ_RECOMMENDATION
    ) -> DecisionObject:
        """
        Synthesizes a structured, auditable decision from available evidence and candidates.
        """
        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        objective = self._determine_objective(query, user_objective)
        now_utc = datetime.now(timezone.utc).isoformat()

        hard_gates_triggered: List[str] = []
        operational_risks: List[str] = []
        data_limitations: List[str] = list(evidence_pkg.missing_variables)
        assumptions: List[str] = []
        reversibility: List[str] = []

        # ---------------------------------------------------------------------
        # 1. Evaluate Hard Safety Gates (Section 8)
        # ---------------------------------------------------------------------
        # Gate 1: Check Geofence / Regulatory Exclusion
        gf_status = geofence.get("geofence_status") if geofence else None
        if gf_status == "RESTRICTED":
            hard_gates_triggered.append(
                "HARD_SAFETY_GATE: Location lies inside an active Marine Protected Area or Sovereign Exclusion Zone."
            )

        # Gate 2: Severe Weather / Cyclone Gale Warning
        wave_height = weather.get("significant_wave_height_m") if weather else None
        wind_speed = weather.get("wind_speed_knots") if weather else None
        if wave_height is not None and wave_height >= 4.0:
            hard_gates_triggered.append(
                f"HARD_SAFETY_GATE: Significant wave height ({wave_height}m) exceeds extreme sea survival threshold (4.0m)."
            )
        if wind_speed is not None and wind_speed >= 34.0:
            hard_gates_triggered.append(
                f"HARD_SAFETY_GATE: Wind speed ({wind_speed} kts) represents gale/storm force winds hazardous to all craft."
            )

        # Gate 3: Navigational Impassability
        route_status = route.get("status") if route else None
        if route_status == "NO_VALID_ROUTE":
            hard_gates_triggered.append(
                "HARD_SAFETY_GATE: Destination or transit corridor is obstructed by land or impassable restricted barriers."
            )

        # Gate 4: Missing Critical Data
        if "significant_wave_height" in evidence_pkg.missing_variables and "wind_speed" in evidence_pkg.missing_variables:
            hard_gates_triggered.append(
                "HARD_SAFETY_GATE: Critical sea-state and wind telemetry missing. Safety cannot be affirmed without positive data."
            )

        # ---------------------------------------------------------------------
        # 2. Candidate Evaluation & Objective-Driven Ranking
        # ---------------------------------------------------------------------
        scored_candidates: List[Dict[str, Any]] = []

        if not candidates:
            # Handle Data Unavailable or Empty Scenario
            conf_decomp = ConfidenceDecomposition(
                overall_confidence=0.0,
                data_coverage_score=0.0,
                source_quality_score=0.0,
                variable_agreement_score=0.0,
                temporal_relevance_score=0.0,
                forecast_certainty_score=0.0,
                uncertainty_sources=["No candidate zones discovered in specified search region."],
                confidence_rationale="Observation feeds or spatial search yielded zero candidate zones."
            )
            return DecisionObject(
                decision_id=decision_id,
                decision_type=DecisionType.DATA_AVAILABILITY_DECISION,
                user_objective=objective,
                recommendation_title="No Actionable Candidate Available",
                decision_status=DecisionStatus.UNAVAILABLE,
                confidence=conf_decomp,
                supporting_factors=[],
                negative_factors=["Zero candidate zones identified in area of interest."],
                hard_safety_gates_triggered=hard_gates_triggered,
                operational_risks=["Lack of operational candidate coordinates."],
                data_limitations=["No satellite thermal/color front candidates exist in specified ROI."],
                assumptions_made=["Assumed standard EEZ search boundaries."],
                reversibility_conditions=["Issuance of new satellite pass or expansion of search radius."],
                evidence_ids=[ev.evidence_id for ev in evidence_pkg.items]
            )

        # Map safety evaluation metrics if provided from Phase 7
        eval_map = {}
        if safety_evals:
            for se in safety_evals:
                cid = se.get("candidate_id") or se.get("name")
                if cid:
                    eval_map[cid] = se

        for cand in candidates:
            cid = cand.get("candidate_id") or cand.get("id") or cand.get("name")
            se = eval_map.get(cid, {})

            pfz_score = float(cand.get("suitability_score") or cand.get("score") or 0.5)
            risk_score = float(se.get("risk_score", cand.get("risk_score", 0.25)))
            cand_gf_status = se.get("geofence_status") or cand.get("geofence_status") or "CLEAR"
            dist_km = float(cand.get("distance_km") or 50.0)
            confidence_val = float(cand.get("confidence", {}).get("overall_confidence", 0.8) if isinstance(cand.get("confidence"), dict) else (cand.get("confidence") or 0.8))

            # Candidate-level hard gate override
            is_cand_restricted = (cand_gf_status == "RESTRICTED")
            is_cand_high_risk = (risk_score >= 0.60)

            # Compute Objective-Weighted Rank Score
            if is_cand_restricted:
                composite_rank = -100.0  # Disqualified
            elif objective == UserObjective.MINIMIZE_RISK:
                composite_rank = (1.0 - risk_score) * 0.60 + pfz_score * 0.30 + (1.0 - min(1.0, dist_km / 150.0)) * 0.10
            elif objective == UserObjective.MAXIMIZE_SUITABILITY:
                composite_rank = pfz_score * 0.70 + (1.0 - risk_score) * 0.20 + (1.0 - min(1.0, dist_km / 150.0)) * 0.10
            elif objective == UserObjective.MINIMIZE_DISTANCE:
                composite_rank = (1.0 - min(1.0, dist_km / 150.0)) * 0.50 + (1.0 - risk_score) * 0.30 + pfz_score * 0.20
            else:  # BALANCE_SUITABILITY_AND_SAFETY
                composite_rank = pfz_score * 0.45 + (1.0 - risk_score) * 0.40 + (1.0 - min(1.0, dist_km / 150.0)) * 0.15

            scored_candidates.append({
                "candidate": cand,
                "candidate_id": cid,
                "name": cand.get("name") or cid,
                "pfz_score": pfz_score,
                "risk_score": risk_score,
                "geofence_status": cand_gf_status,
                "distance_km": dist_km,
                "confidence": confidence_val,
                "composite_rank": composite_rank,
                "is_restricted": is_cand_restricted,
                "is_high_risk": is_cand_high_risk
            })

        # Sort candidates descending by composite rank score
        scored_candidates.sort(key=lambda x: x["composite_rank"], reverse=True)
        top = scored_candidates[0]

        # ---------------------------------------------------------------------
        # 3. Determine Final Decision Status
        # ---------------------------------------------------------------------
        if top["is_restricted"] or any("Marine Protected Area" in g for g in hard_gates_triggered):
            status = DecisionStatus.NO_GO
            rec_title = f"Operations Prohibited: {top['name']} Inside Restricted Area"
        elif any("wave height" in g.lower() or "wind speed" in g.lower() for g in hard_gates_triggered):
            status = DecisionStatus.NO_GO
            rec_title = f"Operations Suspended: Severe Sea State at {top['name']}"
        elif any("Critical sea-state" in g for g in hard_gates_triggered):
            status = DecisionStatus.INSUFFICIENT_EVIDENCE
            rec_title = f"Indeterminate Safety: Missing Observations for {top['name']}"
        elif len(evidence_pkg.conflicting_indicators) > 0 or top["is_high_risk"]:
            status = DecisionStatus.CAUTION
            rec_title = f"Proceed with Caution: {top['name']} Favorable but Elevated Risk"
        elif top["risk_score"] <= 0.35 and top["pfz_score"] >= 0.50:
            status = DecisionStatus.RECOMMENDED
            rec_title = f"Recommended: {top['name']}"
        else:
            status = DecisionStatus.ACCEPTABLE
            rec_title = f"Acceptable Venture: {top['name']}"

        # ---------------------------------------------------------------------
        # 4. Extract Supporting vs Negative Factors (Section 13)
        # ---------------------------------------------------------------------
        supporting_factors: List[str] = []
        negative_factors: List[str] = []

        top_cand = top["candidate"]
        # Supporting factors
        if top["pfz_score"] >= 0.60:
            supporting_factors.append(f"High oceanographic suitability score: {top['pfz_score']:.2f}/1.0 based on coincident fronts.")
        if top["risk_score"] < 0.35:
            supporting_factors.append(f"Low operational marine risk ({top['risk_score']:.2f}/1.0) under current sea conditions.")
        if top["geofence_status"] == "CLEAR":
            supporting_factors.append("Coordinates lie in sovereign EEZ waters clear of Marine Protected Areas and IMBL buffers.")
        if top["distance_km"] <= 80.0:
            supporting_factors.append(f"Favorable coastal proximity ({top['distance_km']:.1f} km from reference port).")

        # Negative factors (Never hide risks!)
        if top["is_restricted"]:
            negative_factors.append("CRITICAL: Candidate polygon directly intersects legal fishing restriction boundary.")
        if top["risk_score"] >= 0.40:
            negative_factors.append(f"Elevated marine operational risk score: {top['risk_score']:.2f}/1.0.")
        if wave_height and wave_height >= 2.0:
            negative_factors.append(f"Significant wave height is {wave_height}m, requiring elevated navigational vigilance.")
        if wind_speed and wind_speed >= 22.0:
            negative_factors.append(f"Sustained wind speed is {wind_speed} knots.")
        if top["distance_km"] > 100.0:
            negative_factors.append(f"Long offshore transit distance ({top['distance_km']:.1f} km) increases fuel burn.")
        if "significant_wave_height" in evidence_pkg.missing_variables:
            negative_factors.append("Wave height observation was missing from telemetry feed.")

        # ---------------------------------------------------------------------
        # 5. Candidate Comparisons & Tradeoffs (Section 12)
        # ---------------------------------------------------------------------
        comparisons: List[CandidateComparison] = []
        for other in scored_candidates[1:4]:  # Compare top against up to 3 alternatives
            s_delta = round(top["pfz_score"] - other["pfz_score"], 3)
            r_delta = round(top["risk_score"] - other["risk_score"], 3)
            d_delta = round(top["distance_km"] - other["distance_km"], 1)

            advantages: List[str] = []
            disadvantages: List[str] = []

            if s_delta > 0:
                advantages.append(f"Higher oceanographic suitability (+{s_delta:.2f})")
            elif s_delta < 0:
                disadvantages.append(f"Lower oceanographic suitability ({s_delta:.2f})")

            if r_delta < 0:
                advantages.append(f"Lower operational risk ({r_delta:.2f})")
            elif r_delta > 0:
                disadvantages.append(f"Higher operational risk (+{r_delta:.2f})")

            if d_delta < 0:
                advantages.append(f"Closer to port ({abs(d_delta):.1f} km nearer)")
            elif d_delta > 0:
                disadvantages.append(f"Further from port (+{d_delta:.1f} km)")

            if other["is_restricted"]:
                advantages.append("Clear of restricted boundaries, whereas alternative is blocked")

            tradeoff = (
                f"{top['name']} is preferred over {other['name']} because "
                f"{'it presents lower risk' if r_delta < 0 else 'it provides superior habitat suitability'}, "
                f"balancing a PFZ score of {top['pfz_score']:.2f} against risk of {top['risk_score']:.2f}."
            )

            comparisons.append(CandidateComparison(
                primary_candidate_id=top["candidate_id"],
                primary_name=top["name"],
                compared_candidate_id=other["candidate_id"],
                compared_name=other["name"],
                suitability_delta=s_delta,
                risk_delta=r_delta,
                distance_delta_km=d_delta,
                tradeoff_summary=tradeoff,
                advantages_of_primary=advantages,
                disadvantages_of_primary=disadvantages,
                recommendation_rationale=f"Selected according to objective: {objective.value}."
            ))

        # ---------------------------------------------------------------------
        # 6. Confidence Decomposition (Section 23)
        # ---------------------------------------------------------------------
        cov_score = 0.90 if len(evidence_pkg.missing_variables) == 0 else max(0.3, 1.0 - len(evidence_pkg.missing_variables) * 0.25)
        src_score = 0.95 if evidence_pkg.official_advisories_present else 0.85
        temp_score = 0.65 if len(evidence_pkg.stale_variables) > 0 else 0.95
        agree_score = 0.50 if len(evidence_pkg.conflicting_indicators) > 0 else 0.90
        fc_certainty = 0.85

        uncertainty_sources: List[str] = []
        if len(evidence_pkg.missing_variables) > 0:
            uncertainty_sources.append(f"Missing variables: {', '.join(evidence_pkg.missing_variables)}")
        if len(evidence_pkg.stale_variables) > 0:
            uncertainty_sources.append(f"Stale observation feeds: {', '.join(evidence_pkg.stale_variables)}")
        if len(evidence_pkg.conflicting_indicators) > 0:
            uncertainty_sources.append(evidence_pkg.conflicting_indicators[0])

        overall_conf = round(
            0.30 * cov_score + 0.25 * src_score + 0.20 * temp_score + 0.15 * agree_score + 0.10 * fc_certainty,
            2
        )

        conf_decomp = ConfidenceDecomposition(
            overall_confidence=overall_conf,
            data_coverage_score=cov_score,
            source_quality_score=src_score,
            variable_agreement_score=agree_score,
            temporal_relevance_score=temp_score,
            forecast_certainty_score=fc_certainty,
            uncertainty_sources=uncertainty_sources,
            confidence_rationale=(
                f"High confidence ({overall_conf*100:.0f}%) supported by active satellite and weather feeds."
                if overall_conf >= 0.75
                else f"Moderate confidence ({overall_conf*100:.0f}%) due to {', '.join(uncertainty_sources) if uncertainty_sources else 'environmental uncertainty'}."
            )
        )

        # ---------------------------------------------------------------------
        # 7. Reversibility Conditions & Expiry (Section 42 & 43)
        # ---------------------------------------------------------------------
        reversibility.append("Recommendation would be revoked if significant wave height increases beyond 2.8m.")
        reversibility.append("Recommendation would be revoked if IMD issues a Depression or Cyclonic Storm alert in this sector.")
        reversibility.append("Recommendation would be invalidated if seasonal fisheries closure or defense NOTAM is activated.")

        assumptions.append("Assumed standard Indian motorized fishing vessel (OAL 9-12m) cruising at 9.5 knots.")
        assumptions.append("Assumed daylight or illuminated vessel navigation adhering to COLREGs Rule 5 lookout.")

        # Decision expiry (12 hours from generation)
        valid_until = (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat()

        return DecisionObject(
            decision_id=decision_id,
            decision_type=decision_type,
            user_objective=objective,
            recommendation_title=rec_title,
            recommended_target_id=top["candidate_id"],
            recommended_target_name=top["name"],
            decision_status=status,
            confidence=conf_decomp,
            supporting_factors=supporting_factors,
            negative_factors=negative_factors,
            hard_safety_gates_triggered=hard_gates_triggered,
            alternative_options=[s["candidate"] for s in scored_candidates[1:4]],
            candidate_comparisons=comparisons,
            operational_risks=negative_factors,
            data_limitations=data_limitations,
            assumptions_made=assumptions,
            reversibility_conditions=reversibility,
            evidence_ids=[ev.evidence_id for ev in evidence_pkg.items],
            evidence_summary=[
                {"param": ev.parameter_name, "value": ev.numeric_value or ev.string_value, "unit": ev.unit, "source": ev.source_name}
                for ev in evidence_pkg.items
            ],
            provenance_graph=list(evidence_pkg.provenance_chain) + [{
                "stage": "DECISION_SYNTHESIS",
                "parameter": "recommendation",
                "source": "ORCA Multi-Objective Decision Engine",
                "type": "SYNTHESIZED",
                "evidence_id": decision_id
            }],
            generated_at=now_utc,
            valid_until=valid_until,
            decision_support_only=True,
            navigation_certified=False
        )
