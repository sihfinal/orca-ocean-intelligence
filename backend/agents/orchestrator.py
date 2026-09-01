"""
Supervisor / Master Orchestrator Agent for Blue Orbit / ORCA
ISRO SIH 2026 - Problem Statement 26176
True Agentic Architecture: Dynamic Planning, Task Decomposition, Tool Registry,
Multi-Agent Coordination, and Multi-Turn Conversational Temporal Memory (Phase 3).
"""

import time
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.agents.marine_data_agent import MarineDataAgent
from backend.agents.weather_hazard_agent import WeatherHazardAgent
from backend.agents.ocean_analytics_agent import OceanAnalyticsAgent
from backend.agents.geospatial_agent import GeospatialAgent
from backend.agents.multilingual_agent import MultilingualAgent
from backend.agents.explainability_agent import ExplainabilityAgent
from backend.agents.llm_engine import generate_llm_advisory

from backend.tools.registry import ToolRegistry
from backend.tools.marine_tools import (
    PointObservationTool,
    SatelliteTelemetryTool,
    WeatherObservationTool,
    CycloneWarningsTool,
    PFZHotspotsTool,
    GeofenceStatusTool,
    SafeRouteTool,
    PortResolverTool,
    SeaSurfaceTemperatureTool,
    WaveConditionsTool,
    WindConditionsTool,
    OceanCurrentsTool,
    TideConditionsTool,
    MarineAdvisoriesTool,
    SatelliteRasterTool,
    SatellitePointValueTool,
    SatelliteRegionStatisticsTool,
    SSTRasterTool,
    ChlorophyllRasterTool,
    RasterContoursTool,
    SpatialGradientTool,
    AvailableEOProductsTool
)
from backend.tools.pfz_tools import (
    AnalyzePFZTool,
    DetectOceanFrontsTool,
    CalculateOceanGradientsTool,
    GeneratePFZCandidatesTool,
    RankPFZCandidatesTool,
    EvaluatePFZEnvironmentTool,
    FindNearestPFZTool,
    FindPFZWithinRadiusTool
)
from backend.tools.geospatial_tools import (
    CheckGeofenceStatusTool,
    FindRestrictionsTool,
    AssessMarineRiskTool,
    ScoreCandidateSafetyTool,
    ComputeSafeRouteTool,
    ComputeAlternativeRoutesTool
)
from backend.tools.decision_tools import (
    CollectEvidenceTool,
    SynthesizeDecisionTool,
    CompareCandidatesTool,
    ExplainDecisionTool,
    VerifyDecisionClaimsTool
)
from backend.planning.models import ExecutionPlan, TaskStatus
from backend.planning.context import ORCAExecutionContext
from backend.planning.planner import SupervisorPlanner
from backend.planning.execution_graph import ExecutionEngine
from backend.planning.context_resolver import ContextResolver
from backend.memory.session_store import SessionStore
from backend.temporal.resolver import TemporalResolver
from backend.data.geodata import INDIAN_PORTS

class MasterOrchestrator:
    """
    Genuine Agentic Coordinator for ORCA.
    Manages multi-turn conversation sessions, resolves temporal windows,
    plans task graphs, and orchestrates tool execution.
    """
    def __init__(self):
        # 1. Specialized Domain Agents
        self.marine_agent = MarineDataAgent()
        self.weather_agent = WeatherHazardAgent()
        self.ocean_agent = OceanAnalyticsAgent(self.marine_agent)
        self.geo_agent = GeospatialAgent()
        self.lang_agent = MultilingualAgent()
        self.explain_agent = ExplainabilityAgent()

        # 2. Central Tool Registry
        self.tool_registry = ToolRegistry()
        self._register_tools()

        # 3. Autonomous Supervisor Planner and Execution Engine
        self.planner = SupervisorPlanner(self.tool_registry)
        self.execution_engine = ExecutionEngine(self.tool_registry)

        # 4. Multi-Turn Session Memory & Temporal Reasoning (Phase 3)
        self.session_store = SessionStore()
        self.temporal_resolver = TemporalResolver()
        self.context_resolver = ContextResolver(self.temporal_resolver)

    def _register_tools(self) -> None:
        """Populates the central tool catalog with available domain capabilities."""
        self.tool_registry.register(PointObservationTool(self.marine_agent))
        self.tool_registry.register(SatelliteTelemetryTool(self.marine_agent))
        self.tool_registry.register(WeatherObservationTool(self.weather_agent))
        self.tool_registry.register(CycloneWarningsTool(self.weather_agent))
        self.tool_registry.register(PFZHotspotsTool(self.ocean_agent))
        self.tool_registry.register(GeofenceStatusTool(self.geo_agent))
        self.tool_registry.register(SafeRouteTool(self.geo_agent))
        self.tool_registry.register(PortResolverTool())
        # Phase 4 Specialized Real-Data Tools
        self.tool_registry.register(SeaSurfaceTemperatureTool(self.marine_agent))
        self.tool_registry.register(WaveConditionsTool(self.weather_agent))
        self.tool_registry.register(WindConditionsTool(self.weather_agent))
        self.tool_registry.register(OceanCurrentsTool(self.marine_agent))
        self.tool_registry.register(TideConditionsTool(self.marine_agent))
        self.tool_registry.register(MarineAdvisoriesTool(self.weather_agent))
        # Phase 5 Earth Observation & Spatial Raster Tools
        self.tool_registry.register(SatelliteRasterTool(self.marine_agent))
        self.tool_registry.register(SatellitePointValueTool(self.marine_agent))
        self.tool_registry.register(SatelliteRegionStatisticsTool(self.marine_agent))
        self.tool_registry.register(SSTRasterTool(self.marine_agent))
        self.tool_registry.register(ChlorophyllRasterTool(self.marine_agent))
        self.tool_registry.register(RasterContoursTool(self.marine_agent))
        self.tool_registry.register(SpatialGradientTool(self.marine_agent))
        self.tool_registry.register(AvailableEOProductsTool(self.marine_agent))
        # Phase 6 PFZ Intelligence & Ocean Analytics Tools
        self.tool_registry.register(AnalyzePFZTool(self.ocean_agent.pfz_engine))
        self.tool_registry.register(DetectOceanFrontsTool(self.ocean_agent.pfz_engine))
        self.tool_registry.register(CalculateOceanGradientsTool(self.ocean_agent.pfz_engine))
        self.tool_registry.register(GeneratePFZCandidatesTool(self.ocean_agent.pfz_engine))
        self.tool_registry.register(RankPFZCandidatesTool(self.ocean_agent.pfz_engine))
        self.tool_registry.register(EvaluatePFZEnvironmentTool(self.ocean_agent.pfz_engine))
        self.tool_registry.register(FindNearestPFZTool(self.ocean_agent.pfz_engine))
        self.tool_registry.register(FindPFZWithinRadiusTool(self.ocean_agent.pfz_engine))
        # Phase 7 Geospatial, Geofencing, Risk Assessment & Route Optimization Tools
        self.tool_registry.register(CheckGeofenceStatusTool(self.geo_agent.geofence_service))
        self.tool_registry.register(FindRestrictionsTool(self.geo_agent.geofence_service))
        self.tool_registry.register(AssessMarineRiskTool(self.geo_agent.risk_engine))
        self.tool_registry.register(ScoreCandidateSafetyTool(self.geo_agent.risk_engine))
        self.tool_registry.register(ComputeSafeRouteTool(self.geo_agent.route_optimizer))
        self.tool_registry.register(ComputeAlternativeRoutesTool(self.geo_agent.route_optimizer))
        # Phase 8 Decision Engine, Explainability & Verification Tools
        self.tool_registry.register(CollectEvidenceTool(self.explain_agent.evidence_collector))
        self.tool_registry.register(SynthesizeDecisionTool(self.explain_agent.decision_engine, self.explain_agent.evidence_collector))
        self.tool_registry.register(CompareCandidatesTool(self.explain_agent.decision_engine))
        self.tool_registry.register(ExplainDecisionTool(self.explain_agent.explainability_engine))
        self.tool_registry.register(VerifyDecisionClaimsTool(self.explain_agent.claim_verifier))

    def find_nearest_port(self, lat: float, lon: float) -> str:
        """Finds closest Indian fishing port key to given coordinates."""
        closest_key = "kochi"
        min_dist_sq = float('inf')
        for key, p in INDIAN_PORTS.items():
            d_sq = (p["lat"] - lat) ** 2 + (p["lon"] - lon) ** 2
            if d_sq < min_dist_sq:
                min_dist_sq = d_sq
                closest_key = key
        return closest_key

    def identify_port_from_query(self, query: str, user_lat: Optional[float] = None, user_lon: Optional[float] = None) -> str:
        """Resolves port key from text query or coordinates."""
        tool = self.tool_registry.get("resolve_reference_port")
        if tool:
            res = tool._run(query=query, user_lat=user_lat, user_lon=user_lon)
            return res.get("port_key", "kochi")
        return "kochi"

    def classify_intent(self, query: str) -> str:
        """Determines primary objective through the planner's request understanding module."""
        ctx = ORCAExecutionContext(query=query)
        understanding = self.planner.understand_request(ctx)
        return understanding["intent"]

    async def execute_query_pipeline(
        self,
        query: str,
        requested_lang: Optional[str] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        reference_port_override: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a plan-driven multi-agent query pipeline with multi-turn session memory.
        Resolves pronouns, deictic references, and temporal expressions across turns.
        """
        start_time = time.time()

        # 1. Retrieve or Initialize Isolated Multi-Turn Session (Section 5 & 29)
        session = self.session_store.get_or_create_session(session_id)

        # 2. Regional Language Detection (Current turn language determines response, Section 24 & 25)
        detected_lang = requested_lang or self.lang_agent.detect_language(query)
        lang_info = self.lang_agent.supported_languages.get(detected_lang, self.lang_agent.supported_languages["en"])
        session.add_user_message(query, lang_code=detected_lang)

        # 3. Context & Temporal Resolution (Pre-Planning Stage, Section 11 & 14)
        resolve_start = time.time()
        resolved_context = self.context_resolver.resolve_context(
            query=query,
            session=session,
            user_lat=user_lat,
            user_lon=user_lon,
            reference_port_override=reference_port_override
        )
        resolve_duration = round((time.time() - resolve_start) * 1000, 2)

        # 4. Initialize Request Execution Context
        context = ORCAExecutionContext(
            query=query,
            requested_lang=detected_lang,
            user_lat=user_lat,
            user_lon=user_lon,
            reference_port_override=reference_port_override,
            session_id=session.session_id
        )
        context.session = session
        context.resolved_context = resolved_context
        context.temporal_window = resolved_context.resolved_time_window

        if resolved_context.resolved_port:
            context.port_info = resolved_context.resolved_port

        if resolved_context.resolved_destination and any(k in query.lower() for k in ["closest", "nearest", "second", "first"]):
            context.top_pfz = resolved_context.resolved_destination

        # Real initial trace event for Context Resolution
        temporal_label = context.temporal_window.label if context.temporal_window else "realtime_current"
        context.add_trace_step({
            "step_id": "STEP_00_CONTEXT_RESOLUTION",
            "agent": "ORCA Multi-Turn Context & Temporal Resolver",
            "status": "COMPLETED",
            "duration_ms": resolve_duration,
            "thought": f"Session '{session.session_id}' (Turn {session.turn_count}). Grounded port: '{context.port_info.get('name', 'Resolved')}', Temporal: '{temporal_label}'. Resolved references: {len(resolved_context.reference_resolutions)}.",
            "output_summary": f"Context grounded for Turn {session.turn_count} (Anchor: {context.port_info.get('name', 'Resolved')})."
        })

        # 5. Dynamic Planning & Task Decomposition (SupervisorPlanner)
        plan_start = time.time()
        plan = self.planner.create_plan(context)
        plan_duration = round((time.time() - plan_start) * 1000, 2)

        # Real trace event for Planner
        context.add_trace_step({
            "step_id": "STEP_01_SUPERVISOR_PLANNING",
            "agent": "ORCA Master Supervisor & Autonomous Planner",
            "status": "COMPLETED",
            "duration_ms": plan_duration,
            "thought": f"Analyzed query intent: '{context.intent}' (Complexity: {plan.complexity}). Formulated plan '{plan.plan_id}' with {len(plan.tasks)} subtasks. {plan.rationale}",
            "output_summary": f"Decomposed into {len(plan.tasks)} goal-directed subtasks."
        })

        # 6. Dependency-Aware DAG Execution
        await self.execution_engine.execute_plan(context)

        # 7. Cognitive Synthesis (LLM or Multilingual Rule-Engine Fallback)
        synth_start = time.time()
        context_bundle = context.build_context_bundle()

        llm_response_text = await generate_llm_advisory(
            user_query=query,
            context_data=context_bundle,
            language_name=lang_info["name"],
            language_code=detected_lang
        )

        if llm_response_text:
            tts_clean = re.sub(r'[*#•🛰️🛡️🛑🧭🐟\n]+', ' ', llm_response_text).strip()
            tts_clean = re.sub(r'\s+', ' ', tts_clean)
            final_markdown = llm_response_text
            model_used_name = "Blue Orbit Neural LLM Engine"
        else:
            localized_result = self.lang_agent.synthesize_localized_response(
                intent=context.intent,
                context_data=context_bundle,
                lang_code=detected_lang,
                user_query=query
            )
            final_markdown = localized_result["formatted_markdown"]
            tts_clean = localized_result["tts_speech_text"]
            model_used_name = "Blue Orbit Autonomous Marine Reasoning Engine"

        synth_duration = round((time.time() - synth_start) * 1000, 2)
        step_num = len(context.execution_trace) + 1
        context.add_trace_step({
            "step_id": f"STEP_{step_num:02d}_COGNITIVE_SYNTHESIS",
            "agent": f"Cognitive Synthesis Agent ({model_used_name})",
            "status": "COMPLETED",
            "duration_ms": synth_duration,
            "thought": f"Synthesized grounded natural language advisory using {model_used_name} in '{lang_info['name']}'. Incorporated findings across {context.completed_tasks_count} completed subtasks.",
            "output_summary": "Grounded natural language advisory synthesized."
        })

        # 8. Post-Execution Memory Update (Section 21 & 22)
        session.add_assistant_message(final_markdown, lang_code=detected_lang)
        if context.port_info:
            session.structured.active_port = context.port_info
        if context.all_pfz:
            session.structured.candidate_pfz_list = context.all_pfz
        if context.top_pfz:
            session.structured.selected_pfz = context.top_pfz
        if context.weather:
            session.structured.active_weather = context.weather
        if context.safe_route:
            session.structured.active_route = context.safe_route
        if context.geofence:
            session.structured.active_geofence = context.geofence
        session.structured.last_intent = context.intent
        session.structured.last_plan_id = plan.plan_id
        session.structured.last_status = "FAILED" if context.failed_tasks_count > 0 else "COMPLETED"
        if context.temporal_window:
            session.structured.temporal_context = context.temporal_window.to_dict()
        session.structured.limitations = context.limitations

        # 9. Phase 8 Decision Engine, Evidence Package & Marine Bulletin
        ev_pkg_typed = self.explain_agent.collect_evidence_package(query, context_bundle, session_id=session.session_id)
        dec_obj = self.explain_agent.synthesize_decision(
            query=query,
            evidence_pkg=ev_pkg_typed,
            candidates=context.pfz_candidates or context.all_pfz,
            weather=context.weather,
            geofence=context.geofence,
            route=context.safe_route,
            safety_evals=context.safety_evaluations
        )

        # Multi-turn explanation resolution from stored decision memory
        if context.intent == "decision_explanation" and session.structured.last_decision:
            from backend.decision.schemas import DecisionObject as DecObj
            try:
                prev_dec = DecObj.model_validate(session.structured.last_decision)
                if "why not" in query.lower():
                    why_not_data = self.explain_agent.explainability_engine.explain_why_not_alternative(prev_dec)
                    final_markdown = (
                        f"### ⚖️ Tradeoff Explanation: {why_not_data['title']}\n\n"
                        f"- **Selected:** {why_not_data['primary_choice']}\n"
                        f"- **Compared Alternative:** {why_not_data['compared_choice']}\n"
                        f"- **Suitability Difference:** {why_not_data['suitability_difference']:+.2f}\n"
                        f"- **Risk Difference:** {why_not_data['risk_difference']:+.2f}\n"
                        f"- **Distance Difference:** {why_not_data['distance_difference_km']:+.1f} km\n"
                        f"- **Tradeoff Summary:** {why_not_data['tradeoff_summary']}"
                    )
                else:
                    why_data = self.explain_agent.explainability_engine.explain_why_recommended(prev_dec)
                    final_markdown = (
                        f"### 🎯 Decision Explanation: {why_data['title']}\n\n"
                        f"**Decision Status:** `{why_data['decision_status']}` | **Confidence:** `{why_data['confidence_percent']}%`\n\n"
                        f"**Key Supporting Factors:**\n" + "\n".join(f"- {f}" for f in why_data['supporting_factors'])
                    )
            except Exception:
                pass

        # Deterministic claim verification guarding LLM trust boundary
        claim_validation = self.explain_agent.verify_response(final_markdown, dec_obj, ev_pkg_typed)
        if not claim_validation.is_valid and claim_validation.safe_fallback_text:
            final_markdown = claim_validation.safe_fallback_text

        # Record decision into structured session memory
        session.structured.last_decision = dec_obj.model_dump()
        session.structured.decision_history.append(dec_obj.model_dump())
        if len(session.structured.decision_history) > 10:
            session.structured.decision_history = session.structured.decision_history[-10:]
        session.structured.evidence_package = ev_pkg_typed.model_dump()
        self.session_store.save_session(session)

        # Legacy-compatible evidence package and bulletin
        evidence_pkg = self.explain_agent.generate_evidence_package(query, context.execution_trace, context_bundle)
        bulletin = self.explain_agent.generate_official_marine_bulletin(
            context.port_info.get("name", "Indian Coastal Port"),
            context.all_pfz,
            context.weather,
            context.geofence
        )

        total_latency_ms = round((time.time() - start_time) * 1000, 2)
        context.total_latency_ms = total_latency_ms

        distinct_agents = len(set(s.get("agent") for s in context.execution_trace))

        # 10. Assemble Complete Backward-Compatible Response Contract
        return {
            "query": query,
            "session_id": session.session_id,
            "detected_intent": context.intent,
            "language": {
                "code": detected_lang,
                "name": lang_info["name"],
                "native": lang_info["native"],
                "voice_code": lang_info["voice_code"]
            },
            "reference_port": context.port_info,
            "message": final_markdown,
            "response": {
                "markdown": final_markdown,
                "tts_speech_text": tts_clean,
                "model_engine": model_used_name
            },
            "decision": dec_obj.model_dump(),
            "recommendation": dec_obj.recommendation_title,
            "decision_status": dec_obj.decision_status.value,
            "supporting_factors": dec_obj.supporting_factors,
            "negative_factors": dec_obj.negative_factors,
            "operational_risks": dec_obj.operational_risks,
            "data_limitations": dec_obj.data_limitations,
            "claim_validation": claim_validation.model_dump(),
            "evidence_package": ev_pkg_typed.model_dump(),
            "satellite_raster": context.satellite_raster,
            "top_pfz": context.top_pfz,
            "all_pfz_hotspots": context.all_pfz,
            "pfz_candidates": context.pfz_candidates,
            "pfz_analysis": context.pfz_analysis,
            "weather_and_safety": context.weather,
            "geofence_status": context.geofence,
            "safe_navigation_route": context.safe_route,
            "safety_evaluations": getattr(context, "safety_evaluations", None),
            "decision_support_only": True,
            "navigation_certified": False,
            "satellite_telemetry": context.satellite_telemetry or self.marine_agent.get_satellite_telemetry(),
            "official_bulletin": bulletin,
            "evidence_and_provenance": evidence_pkg,
            "temporal_context": context.temporal_window.to_dict() if context.temporal_window else None,
            "resolved_context": {
                "is_ambiguous": resolved_context.is_ambiguous,
                "ambiguity_reason": resolved_context.ambiguity_reason,
                "reference_resolutions": resolved_context.reference_resolutions
            },
            "execution_metadata": {
                "plan_id": plan.plan_id,
                "session_id": session.session_id,
                "turn_count": session.turn_count,
                "total_agents_involved": distinct_agents,
                "total_tasks_planned": len(plan.tasks),
                "completed_tasks": context.completed_tasks_count,
                "failed_tasks": context.failed_tasks_count,
                "complexity": plan.complexity,
                "llm_engine": model_used_name,
                "total_latency_ms": total_latency_ms,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
