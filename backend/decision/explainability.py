"""
Dedicated Explainability Engine for ORCA Decisions
ISRO SIH 2026 - Problem Statement 26176
Phase 8: Decision Engine, Explainability, Evidence & Provenance
"""

from typing import Dict, Any, List, Optional
from backend.decision.schemas import (
    DecisionObject,
    EvidencePackage,
    CandidateComparison,
    DecisionStatus
)

class ExplainabilityEngine:
    """
    Transforms structured decision objects and evidence packages into transparent,
    factual, and auditable explanations.
    """

    def __init__(self):
        pass

    def explain_why_recommended(self, decision: DecisionObject) -> Dict[str, Any]:
        """
        Explains the top factual and mathematical rationale for the recommended choice.
        """
        return {
            "title": f"Why {decision.recommended_target_name or 'the zone'} is Recommended",
            "decision_status": decision.decision_status.value,
            "user_objective": decision.user_objective.value,
            "supporting_factors": decision.supporting_factors,
            "confidence_percent": round(decision.confidence.overall_confidence * 100, 1),
            "confidence_rationale": decision.confidence.confidence_rationale
        }

    def explain_why_not_alternative(
        self,
        decision: DecisionObject,
        compared_id_or_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Explains why a specific alternative (or the runner-up) was NOT recommended over the primary choice.
        """
        if not decision.candidate_comparisons:
            return {
                "title": "Alternative Comparison",
                "message": "No alternative candidates were available for comparison in this sector."
            }

        target_comp: Optional[CandidateComparison] = None
        if compared_id_or_name:
            c_query = compared_id_or_name.lower()
            for c in decision.candidate_comparisons:
                if c_query in c.compared_candidate_id.lower() or c_query in c.compared_name.lower():
                    target_comp = c
                    break

        if not target_comp:
            target_comp = decision.candidate_comparisons[0]

        return {
            "title": f"Why '{decision.recommended_target_name}' was selected over '{target_comp.compared_name}'",
            "primary_choice": decision.recommended_target_name,
            "compared_choice": target_comp.compared_name,
            "suitability_difference": target_comp.suitability_delta,
            "risk_difference": target_comp.risk_delta,
            "distance_difference_km": target_comp.distance_delta_km,
            "advantages_of_selected": target_comp.advantages_of_primary,
            "disadvantages_of_selected": target_comp.disadvantages_of_primary,
            "tradeoff_summary": target_comp.tradeoff_summary,
            "rationale": target_comp.recommendation_rationale
        }

    def explain_risks_and_limitations(self, decision: DecisionObject) -> Dict[str, Any]:
        """
        Extracts operational hazards, negative factors, and data limitations.
        """
        return {
            "title": "Operational Risks & Evidence Limitations",
            "negative_factors": decision.negative_factors,
            "hard_safety_gates": decision.hard_safety_gates_triggered,
            "data_limitations": decision.data_limitations,
            "uncertainty_sources": decision.confidence.uncertainty_sources
        }

    def explain_sources_and_provenance(
        self,
        decision: DecisionObject,
        evidence_pkg: EvidencePackage
    ) -> Dict[str, Any]:
        """
        Returns verifiable sources, sensors, and observation timestamps without hallucinations.
        """
        provenance_records = []
        for ev in evidence_pkg.items:
            provenance_records.append({
                "parameter": ev.parameter_name,
                "value": ev.numeric_value if ev.numeric_value is not None else ev.string_value,
                "unit": ev.unit,
                "source": ev.source_name,
                "type": ev.source_type.value,
                "is_forecast": ev.is_forecast,
                "timestamp": ev.timestamp,
                "freshness": ev.freshness.value,
                "url": ev.provenance_url
            })

        return {
            "title": "Data Sources & Physical Observation Provenance",
            "sources_count": len(provenance_records),
            "records": provenance_records,
            "missing_variables": evidence_pkg.missing_variables,
            "stale_variables": evidence_pkg.stale_variables
        }

    def explain_reversibility_and_validity(self, decision: DecisionObject) -> Dict[str, Any]:
        """
        Details when the recommendation expires and what specific conditions would reverse it.
        """
        return {
            "title": "Decision Validity & Reversibility Criteria",
            "valid_until": decision.valid_until,
            "generated_at": decision.generated_at,
            "reversibility_triggers": decision.reversibility_conditions,
            "assumptions": decision.assumptions_made
        }

    def format_decision_markdown(
        self,
        decision: DecisionObject,
        evidence_pkg: EvidencePackage
    ) -> str:
        """
        Constructs a transparent, human-readable markdown brief of the complete decision package.
        """
        status_icon = "✅" if decision.decision_status == DecisionStatus.RECOMMENDED else (
            "⚠️" if decision.decision_status == DecisionStatus.CAUTION else (
                "🛑" if decision.decision_status == DecisionStatus.NO_GO else "ℹ️"
            )
        )

        md = []
        md.append(f"### {status_icon} ORCA Recommendation: {decision.recommendation_title}\n")
        md.append(f"**Decision Status:** `{decision.decision_status.value}` | **Confidence:** `{decision.confidence.overall_confidence*100:.0f}%` | **Objective:** `{decision.user_objective.value}`\n")

        # 1. Why Recommended
        if decision.supporting_factors:
            md.append("#### 🎯 Key Supporting Evidence")
            for sf in decision.supporting_factors:
                md.append(f"- {sf}")
            md.append("")

        # 2. Risks & Negative Factors (Never hidden!)
        if decision.negative_factors:
            md.append("#### ⚠️ Operational Risks & Negative Factors")
            for nf in decision.negative_factors:
                md.append(f"- {nf}")
            md.append("")

        # 3. Tradeoffs vs Alternatives
        if decision.candidate_comparisons:
            comp = decision.candidate_comparisons[0]
            md.append(f"#### ⚖️ Tradeoff vs Alternative ({comp.compared_name})")
            md.append(f"- {comp.tradeoff_summary}")
            if comp.advantages_of_primary:
                md.append(f"- **Advantages of Recommended:** {', '.join(comp.advantages_of_primary)}")
            if comp.disadvantages_of_primary:
                md.append(f"- **Tradeoff Considerations:** {', '.join(comp.disadvantages_of_primary)}")
            md.append("")

        # 4. Data Limitations & Uncertainties
        if decision.confidence.uncertainty_sources or decision.data_limitations:
            md.append("#### 🔬 Uncertainties & Data Limitations")
            for un in decision.confidence.uncertainty_sources:
                md.append(f"- {un}")
            md.append("")

        # 5. Provenance Citations
        md.append("#### 🛰️ Verified Data Provenance")
        for ev in evidence_pkg.items[:4]:
            tag = "Forecast" if ev.is_forecast else "Observation"
            val_str = f"{ev.numeric_value} {ev.unit}" if ev.numeric_value is not None else str(ev.string_value)
            md.append(f"- **{ev.parameter_name}**: {val_str} ({tag} via *{ev.source_name}*)")
        md.append("")

        # 6. Reversibility
        if decision.reversibility_conditions:
            md.append("#### 🔄 Reversibility Triggers")
            for rev in decision.reversibility_conditions[:2]:
                md.append(f"- {rev}")
            md.append("")

        md.append("---")
        md.append("*(Tactical decision-support only. Not certified for navigation. Vessel master retains ultimate command responsibility.)*")

        return "\n".join(md)
