"""
Phase 8 Decision Engine, Explainability, Evidence & Provenance Tools
ISRO SIH 2026 - Problem Statement 26176
"""

from typing import Dict, Any, List, Optional
from backend.tools.base import BaseTool, ToolSchema, ToolParameter
from backend.decision.schemas import (
    UserObjective,
    DecisionType,
    DecisionObject,
    EvidencePackage
)
from backend.decision.evidence_collector import EvidenceCollector
from backend.decision.engine import ORCADecisionEngine
from backend.decision.explainability import ExplainabilityEngine
from backend.decision.claim_verifier import ClaimVerifier

class CollectEvidenceTool(BaseTool):
    name = "collect_evidence"
    description = "Harvests and normalizes multi-domain environmental, satellite, weather, and geofence observations into an auditable evidence package with data freshness metrics."
    purpose = "Data Provenance and Evidence Aggregation"

    def __init__(self, collector: Optional[EvidenceCollector] = None):
        self.collector = collector or EvidenceCollector()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "query": ToolParameter("query", "string", "User query string", required=False, default=""),
                "context_bundle": ToolParameter("context_bundle", "object", "Aggregated execution context", required=False, default={}),
                "session_id": ToolParameter("session_id", "string", "Active session identifier", required=False, default=None)
            },
            return_description="Structured EvidencePackage containing typed items, data freshness, and provenance DAG."
        )

    async def _run(self, query: str = "", context_bundle: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        pkg = self.collector.collect_evidence(query or "", context_bundle or {}, session_id=session_id)
        return pkg.model_dump()

class SynthesizeDecisionTool(BaseTool):
    name = "synthesize_decision"
    description = "Synthesizes an explicit, objective-driven operational recommendation by balancing candidate PFZs, multi-factor marine risks, and hard safety gates."
    purpose = "Operational Multi-Objective Decision Synthesis"

    def __init__(self, engine: Optional[ORCADecisionEngine] = None, collector: Optional[EvidenceCollector] = None):
        self.engine = engine or ORCADecisionEngine()
        self.collector = collector or EvidenceCollector()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "query": ToolParameter("query", "string", "User query string", required=False, default=""),
                "candidates": ToolParameter("candidates", "array", "List of candidate PFZ zones", required=False, default=[]),
                "weather": ToolParameter("weather", "object", "Marine weather telemetry", required=False, default={}),
                "geofence": ToolParameter("geofence", "object", "Geofence boundary status", required=False, default={}),
                "route": ToolParameter("route", "object", "Navigational route data", required=False, default={}),
                "safety_evaluations": ToolParameter("safety_evaluations", "array", "Safety evaluations from Phase 7", required=False, default=[]),
                "user_objective": ToolParameter("user_objective", "string", "Operational objective (e.g. MINIMIZE_RISK, BALANCE_SUITABILITY_AND_SAFETY)", required=False, default=None)
            },
            return_description="Complete DecisionObject with recommendation, confidence, negative factors, alternatives, and limitations."
        )

    async def _run(
        self,
        query: str = "",
        candidates: Optional[List[Dict[str, Any]]] = None,
        weather: Optional[Dict[str, Any]] = None,
        geofence: Optional[Dict[str, Any]] = None,
        route: Optional[Dict[str, Any]] = None,
        safety_evaluations: Optional[List[Dict[str, Any]]] = None,
        user_objective: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        cands = candidates or []
        w = weather or {}
        gf = geofence or {}
        r = route or {}
        evals = safety_evaluations or []

        # Build context bundle for evidence extraction
        bundle = {
            "weather": w,
            "geofence": gf,
            "route": r,
            "top_pfz": cands[0] if cands else None,
            "all_pfz": cands
        }
        ev_pkg = self.collector.collect_evidence(query or "", bundle)

        obj_enum = None
        if user_objective:
            try:
                obj_enum = UserObjective(user_objective)
            except Exception:
                pass

        dec = self.engine.synthesize_decision(
            query=query or "",
            evidence_pkg=ev_pkg,
            candidates=cands,
            weather=w,
            geofence=gf,
            route=r,
            safety_evals=evals,
            user_objective=obj_enum
        )
        return dec.model_dump()

class CompareCandidatesTool(BaseTool):
    name = "compare_candidates"
    description = "Compares multiple candidate fishing zones, calculating tradeoffs across suitability, risk, distance, and regulatory compliance."
    purpose = "Candidate Tradeoff Comparison"

    def __init__(self, engine: Optional[ORCADecisionEngine] = None):
        self.engine = engine or ORCADecisionEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "candidate_a": ToolParameter("candidate_a", "object", "First candidate zone", required=True),
                "candidate_b": ToolParameter("candidate_b", "object", "Second candidate zone", required=True)
            },
            return_description="CandidateComparison containing suitability delta, risk delta, and tradeoff summary."
        )

    async def _run(self, candidate_a: Dict[str, Any], candidate_b: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        s_a = float(candidate_a.get("suitability_score") or candidate_a.get("score") or 0.5)
        s_b = float(candidate_b.get("suitability_score") or candidate_b.get("score") or 0.5)
        r_a = float(candidate_a.get("risk_score", 0.25))
        r_b = float(candidate_b.get("risk_score", 0.25))
        d_a = float(candidate_a.get("distance_km", 50.0))
        d_b = float(candidate_b.get("distance_km", 50.0))

        s_delta = round(s_a - s_b, 3)
        r_delta = round(r_a - r_b, 3)
        d_delta = round(d_a - d_b, 1)

        name_a = candidate_a.get("name", "Candidate A")
        name_b = candidate_b.get("name", "Candidate B")

        return {
            "primary_candidate": name_a,
            "compared_candidate": name_b,
            "suitability_delta": s_delta,
            "risk_delta": r_delta,
            "distance_delta_km": d_delta,
            "tradeoff_summary": (
                f"{name_a} vs {name_b}: "
                f"Suitability diff {s_delta:+.2f}, Risk diff {r_delta:+.2f}, Distance diff {d_delta:+.1f} km."
            )
        }

class ExplainDecisionTool(BaseTool):
    name = "explain_decision"
    description = "Extracts transparent, auditable explanations from a stored decision object: why recommended, why not alternative, risks, and source provenance."
    purpose = "Decision Explainability and Transparent Reasoning"

    def __init__(self, explainability_engine: Optional[ExplainabilityEngine] = None):
        self.engine = explainability_engine or ExplainabilityEngine()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "decision": ToolParameter("decision", "object", "Serialized DecisionObject", required=True),
                "explanation_type": ToolParameter("explanation_type", "string", "Type of explanation (why, why_not, risks, sources, reversibility)", required=False, default="why")
            },
            return_description="Structured explanation payload."
        )

    async def _run(self, decision: Dict[str, Any], explanation_type: str = "why", **kwargs) -> Dict[str, Any]:
        try:
            dec_obj = DecisionObject.model_validate(decision)
        except Exception:
            return {"error": "Invalid decision object structure"}

        etype = (explanation_type or "why").lower()
        if etype == "why_not":
            return self.engine.explain_why_not_alternative(dec_obj)
        elif etype == "risks":
            return self.engine.explain_risks_and_limitations(dec_obj)
        elif etype == "reversibility":
            return self.engine.explain_reversibility_and_validity(dec_obj)
        else:
            return self.engine.explain_why_recommended(dec_obj)

class VerifyDecisionClaimsTool(BaseTool):
    name = "verify_decision_claims"
    description = "Guards the LLM trust boundary by verifying natural language text against structured decision and evidence data to prevent hallucinations."
    purpose = "Natural Language Claim Verification"

    def __init__(self, verifier: Optional[ClaimVerifier] = None):
        self.verifier = verifier or ClaimVerifier()
        super().__init__()

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={
                "text": ToolParameter("text", "string", "Generated natural language text", required=True),
                "decision": ToolParameter("decision", "object", "Serialized DecisionObject", required=True),
                "evidence_package": ToolParameter("evidence_package", "object", "Serialized EvidencePackage", required=True)
            },
            return_description="ClaimValidationResult containing is_valid, discrepancies, and safe fallback text."
        )

    async def _run(self, text: str, decision: Dict[str, Any], evidence_package: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        try:
            dec_obj = DecisionObject.model_validate(decision)
            ev_obj = EvidencePackage.model_validate(evidence_package)
        except Exception as e:
            return {"error": f"Validation parsing error: {e}"}

        result = self.verifier.verify_response_claims(text, dec_obj, ev_obj)
        return result.model_dump()
