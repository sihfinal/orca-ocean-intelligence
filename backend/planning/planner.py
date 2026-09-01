"""
Supervisor / Planner Agent for ORCA
ISRO SIH 2026 - Problem Statement 26176
Performs intent understanding, entity extraction, constraint classification,
and dynamic task decomposition into DAG execution plans.
"""

import re
from typing import Dict, Any, List, Optional
from backend.planning.models import Task, ExecutionPlan, TaskStatus
from backend.planning.context import ORCAExecutionContext
from backend.data.geodata import INDIAN_PORTS

class SupervisorPlanner:
    """
    Intelligent Planner for ORCA.
    Transforms arbitrary user queries into structured execution plans.
    Decides dynamically which agents and tools to invoke rather than blindly executing everything.
    """
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def understand_request(self, context: ORCAExecutionContext) -> Dict[str, Any]:
        """
        Parses intent, coastal entities, and explicit constraints from query text.
        Incorporates resolved multi-turn context and temporal windows.
        """
        q = (context.query or "").lower().strip()
        rc = getattr(context, "resolved_context", None)

        # 1. Intent Detection
        intent = "general_inquiry"
        complexity = "MEDIUM"

        # Greeting check
        if re.match(r'^(hi|hello|hey|greetings|vanakkam|namaskaram|namaste|good morning|good evening|good afternoon)(\s|!|\.|\?)*$', q):
            intent = "greeting"
            complexity = "LOW"
        # Radius-filtered / Geodesic Spatial PFZ query (Phase 6)
        elif any(k in q for k in ["within", "radius", "best fishing zone within", "pfzs within", "fishing zone within"]) and any(k in q for k in ["km", "radius", "pfz", "fishing", "zone", "fish"]):
            intent = "pfz_radius_search"
            complexity = "HIGH"
        # Dedicated safest PFZ candidate query (Phase 7)
        elif any(k in q for k in ["safest pfz", "which pfz is safest", "safest fishing zone", "which fishing zone is safest", "safest zone", "safest from"]):
            intent = "safest_pfz_advisory"
            complexity = "HIGH"
        # Decision Explanation follow-up (Phase 8)
        elif any(k in q for k in [
            "why not", "why did you choose", "why did you select", "why is this recommended",
            "why is this zone", "what makes it safer", "what makes it best", "explain your decision",
            "why not the other", "why not the second", "why not candidate"
        ]) or (q in ["why", "why?", "explain", "reason", "karan kya hai", "kyun", "yeke"]):
            intent = "decision_explanation"
            complexity = "LOW"
        # Evidence & Provenance inquiry (Phase 8)
        elif any(k in q for k in [
            "what data are you using", "what are your sources", "what sources", "data sources",
            "where did this come from", "what is uncertain", "what are the limitations",
            "show evidence", "what is missing", "uncertainties"
        ]):
            intent = "evidence_provenance_inquiry"
            complexity = "LOW"
        # Candidate Comparison inquiry (Phase 8)
        elif any(k in q for k in [
            "compare candidates", "compare zones", "compare the zones", "tradeoff between",
            "compare options", "difference between zones"
        ]):
            intent = "candidate_comparison"
            complexity = "LOW"
        # Follow-up comparative safety questions ("Which one is safest?")
        elif any(k in q for k in ["which one is safest", "which is safest", "which one is safe", "which is safe"]):
            intent = "sea_weather_safety"
            complexity = "MEDIUM"
        # Check composite / full mission queries
        elif (
            ("route" in q or "navigate" in q or "rasta" in q) and
            ("pfz" in q or "fishing" in q or "fish" in q or "machli" in q or "zone" in q)
        ) or (
            ("weather" in q or "mausam" in q or "safe" in q or "safety" in q or "condition" in q) and
            ("pfz" in q or "fishing" in q or "fish" in q or "machli" in q or "zone" in q)
        ) or "best fishing zone" in q:
            intent = "composite_marine_advisory"
            complexity = "HIGH"
        # Pure Route / Navigation query (including follow-up "give me the route there", "how do I reach it?")
        elif any(k in q for k in ["route", "navigate", "navigation", "waypoint", "heading", "bearing", "transit time", "fuel burn", "rasta", "route there", "route to it", "how do i reach", "how to reach", "how can i reach"]):
            intent = "safe_navigation_route"
            complexity = "MEDIUM"
        # Pure Weather / Sea Safety query (including follow-up "will it be safe tomorrow?")
        elif any(k in q for k in ["weather", "sea condition", "wave height", "wind", "cyclone", "storm", "safe to go", "safety index", "swell", "mausam", "hawa", "will it be safe", "is it safe", "safe tomorrow", "safe today"]):
            intent = "sea_weather_safety"
            complexity = "MEDIUM"
        # Pure PFZ / Fishery query (including follow-up "which is closest?")
        elif any(k in q for k in ["pfz", "fishing zone", "fish", "tuna", "sardine", "mackerel", "catch multiplier", "ocean front", "machli", "macchi", "closest", "nearest", "which is closest", "second zone", "first zone"]):
            intent = "pfz_advisory"
            complexity = "MEDIUM"
        elif any(k in q for k in ["geofence", "border", "imbl", "sri lanka", "pakistan", "mpa", "protected area", "seema"]):
            intent = "geofence_check"
            complexity = "MEDIUM"
        # Pure Spatial Earth Observation & Raster Analysis
        elif any(k in q for k in [
            "chlorophyll", "chl", "distribution", "spatial", "raster", "gradient", 
            "front", "contour", "sharp", "highest chlorophyll", "high chlorophyll",
            "sst distribution", "sst pattern", "chlorophyll pattern", "thermal front",
            "satellite image", "satellite raster", "satellite field", "eo product"
        ]):
            intent = "spatial_eo_raster"
            complexity = "MEDIUM"

        # 2. Extract Entities
        entities = {}
        # Port detection (respect explicit first, then resolved context)
        if rc and rc.resolved_port:
            entities["port_key"] = rc.resolved_port.get("port_key", "kochi")
            entities["port_name"] = rc.resolved_port.get("name", "Indian Port")
        else:
            for p_key, p_val in INDIAN_PORTS.items():
                if p_key in q or p_val["name"].lower() in q:
                    entities["port_key"] = p_key
                    entities["port_name"] = p_val["name"]
                    break

        # Species detection
        species_list = ["tuna", "oil sardine", "mackerel", "ribbonfish", "squid", "anchovy", "seer fish", "bombay duck"]
        for sp in species_list:
            if sp in q:
                entities["target_species"] = sp
                break

        # Distance / Radius extraction
        dist_match = re.search(r'(\d+)\s*(km|nautical miles|nm|kilometres|kilometers)', q)
        if dist_match:
            entities["distance_value"] = float(dist_match.group(1))
            entities["distance_unit"] = dist_match.group(2)

        # 3. Constraint Classification (Section 27, 17, 18 - Strict Honesty)
        supported_constraints = []
        unsupported_constraints = []

        if "port_key" in entities or context.reference_port_override:
            supported_constraints.append("reference_port_anchor")
        if context.user_lat is not None and context.user_lon is not None:
            supported_constraints.append("gps_coordinate_grounding")
        if rc and rc.resolved_destination:
            supported_constraints.append("context_resolved_destination")

        # Unsupported in current synthetic phase:
        if "distance_value" in entities:
            unsupported_constraints.append(f"radius_limit_{entities['distance_value']}_{entities['distance_unit']} (Spatial filtering deferred to Phase 6)")
        
        tw = getattr(context, "temporal_window", None) or (rc.resolved_time_window if rc else None)
        if tw and tw.is_future:
            unsupported_constraints.append(f"temporal_forecast_offset ({tw.label}) - Predictive forecast tools deferred to Phase 4")
            context.limitations.append(f"Temporal request '{tw.label}' understood. Baseline synthetic observations provided; numerical ocean state forecast models deferred to Phase 4.")

        if any(d in q for d in ["draft", "trawler depth", "boat length", "vessel size"]):
            unsupported_constraints.append("vessel_draft_constraint (Vessel physics deferred to Phase 7)")

        if rc and rc.is_ambiguous:
            context.limitations.append(f"Ambiguous reference: {rc.ambiguity_reason}")

        understanding = {
            "intent": intent,
            "complexity": complexity,
            "entities": entities,
            "supported_constraints": supported_constraints,
            "unsupported_constraints": unsupported_constraints
        }
        context.understanding = understanding
        context.intent = intent
        return understanding

    def create_plan(self, context: ORCAExecutionContext) -> ExecutionPlan:
        """
        Decomposes query into dynamically determined tasks and dependencies.
        """
        understanding = self.understand_request(context)
        intent = understanding["intent"]
        complexity = understanding["complexity"]

        effective_port_override = context.reference_port_override or (
            context.port_info.get("port_key") if context.port_info else None
        )

        tasks: List[Task] = []
        dependencies: Dict[str, List[str]] = {}

        # ----------------------------------------------------
        # SCENARIO 1: GREETING / LOW COMPLEXITY INTERACTION
        # ----------------------------------------------------
        if intent == "greeting":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Reference Coastal Anchor",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Identified conversational greeting. Resolving coastal anchor without executing heavy marine computations.",
                output_summary="Coastal anchor grounded for conversational session."
            )
            tasks = [t_port]
            dependencies = {}
            rationale = "Low-complexity greeting: strictly skipped marine observation, PFZ, and routing subtasks."

        # ----------------------------------------------------
        # SCENARIO 1B: DECISION EXPLANATION (PHASE 8)
        # ----------------------------------------------------
        elif intent == "decision_explanation":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Coastal Context",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Grounding explanation query to coastal context.",
                output_summary="Port context resolved."
            )
            t_explain = Task(
                task_id="task_explain_01",
                title="Explain Operational Recommendation",
                responsible_agent="ORCA Explainability Engine",
                selected_tool="explain_decision",
                input_parameters={
                    "explanation_type": "why_not" if "why not" in (context.query or "").lower() else "why"
                },
                dependencies=["task_port_01"],
                step_id="STEP_02_DECISION_EXPLANATION",
                thought="Extracting factual supporting reasons, candidate tradeoffs, and risks from decision memory.",
                output_summary="Explainable reasoning trace generated."
            )
            tasks = [t_port, t_explain]
            dependencies = {"task_explain_01": ["task_port_01"]}
            rationale = "Decision Explanation focus: leveraged structured decision memory and explainability engine without re-running expensive raster pipeline."

        # ----------------------------------------------------
        # SCENARIO 1C: EVIDENCE & PROVENANCE INQUIRY (PHASE 8)
        # ----------------------------------------------------
        elif intent == "evidence_provenance_inquiry":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Reference Coastal Region",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Grounding evidence query to coastal anchor.",
                output_summary="Port context resolved."
            )
            t_evidence = Task(
                task_id="task_evidence_01",
                title="Collect & Verify Data Provenance",
                responsible_agent="Evidence & Provenance Agent",
                selected_tool="collect_evidence",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_02_EVIDENCE_COLLECTION",
                thought="Compiling verifiable data sources, observations, forecasts, and freshness metrics.",
                output_summary="Auditable evidence package assembled."
            )
            tasks = [t_port, t_evidence]
            dependencies = {"task_evidence_01": ["task_port_01"]}
            rationale = "Evidence & Provenance focus: compiled source citations, sensor streams, and freshness metrics."

        # ----------------------------------------------------
        # SCENARIO 1D: CANDIDATE COMPARISON (PHASE 8)
        # ----------------------------------------------------
        elif intent == "candidate_comparison":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Reference Port",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Resolving reference port anchor.",
                output_summary="Port resolved."
            )
            t_pfz = Task(
                task_id="task_pfz_01",
                title="Retrieve Candidate Fishing Zones",
                responsible_agent="Ocean Analytics & PFZ Agent",
                selected_tool="generate_pfz_hotspots",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_02_PFZ_CANDIDATES",
                thought="Retrieving candidates for comparative tradeoff analysis.",
                output_summary="Candidate zones retrieved."
            )
            tasks = [t_port, t_pfz]
            dependencies = {"task_pfz_01": ["task_port_01"]}
            rationale = "Candidate Comparison focus: evaluated multiple zones for side-by-side tradeoff analysis."

        # ----------------------------------------------------
        # SCENARIO 2: SEA WEATHER & SAFETY INQUIRY
        # ----------------------------------------------------
        elif intent == "sea_weather_safety":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Reference Port & Coordinates",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Resolving coastal anchor coordinates for targeted meteocean weather query.",
                output_summary="Resolved base observation coordinates."
            )
            t_marine = Task(
                task_id="task_marine_obs_01",
                title="Retrieve Satellite Sea Temperature & Chlorophyll",
                responsible_agent="Marine Data Discovery Agent",
                selected_tool="get_point_observation",
                input_parameters={},  # Populated dynamically after t_port runs
                dependencies=["task_port_01"],
                step_id="STEP_02_MARINE_DATA_INGESTION",
                thought="Retrieving INSAT-3DR TIR and Oceansat-3 radiometry for sea surface temperature baseline.",
                output_summary="SST radiometry retrieved."
            )
            t_weather = Task(
                task_id="task_weather_01",
                title="Calculate Meteocean Hazard & Safety Index",
                responsible_agent="Weather & Marine Disaster Hazard Agent",
                selected_tool="get_weather_at_point",
                input_parameters={},  # Populated dynamically after t_port runs
                dependencies=["task_port_01"],
                step_id="STEP_03_WEATHER_HAZARD_EVALUATION",
                thought="Computing wave height, Beaufort wind scale, sea state, and fishermen safety score.",
                output_summary="Weather safety index calculated."
            )
            t_cyclone = Task(
                task_id="task_cyclone_01",
                title="Check Regional Cyclonic Storms & High-Wave Warnings",
                responsible_agent="Disaster Intelligence Agent",
                selected_tool="get_active_cyclones_and_warnings",
                input_parameters={},
                dependencies=[],
                step_id="STEP_03B_CYCLONE_HAZARD_SCAN",
                thought="Scanning North Indian Ocean basin for tropical depressions, cyclonic storms, and IMD advisories.",
                output_summary="Cyclone warning telemetry verified."
            )
            tasks = [t_port, t_marine, t_weather, t_cyclone]
            dependencies = {
                "task_marine_obs_01": ["task_port_01"],
                "task_weather_01": ["task_port_01"]
            }
            rationale = "Weather & Safety focus: bypassed PFZ analytics and navigational routing."

        # ----------------------------------------------------
        # SCENARIO 3: PFZ ADVISORY INQUIRY
        # ----------------------------------------------------
        elif intent == "pfz_advisory":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Reference Port",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Resolving departure port for PFZ distance and bearing calculations.",
                output_summary="Harbour resolved."
            )
            t_marine = Task(
                task_id="task_marine_obs_01",
                title="Satellite Radiometry Observation",
                responsible_agent="Marine Data Discovery Agent",
                selected_tool="get_point_observation",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_02_MARINE_DATA_INGESTION",
                thought="Retrieving Oceansat-3 OCM-3 Chlorophyll and INSAT-3DR Sea Surface Temperature.",
                output_summary="Satellite radiometry retrieved."
            )
            t_pfz = Task(
                task_id="task_pfz_01",
                title="Generate Potential Fishing Zone Hotspots",
                responsible_agent="Ocean Analytics & PFZ Agent",
                selected_tool="generate_pfz_hotspots",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_03_OCEAN_PFZ_ANALYTICS",
                thought="Computing thermal front gradient (|∇SST|) × chlorophyll gradient (|∇Chl-a|) across Indian EEZ.",
                output_summary="Ranked PFZ candidate hotspots generated."
            )
            t_geofence = Task(
                task_id="task_geofence_01",
                title="Verify Candidate PFZ Geofence Compliance",
                responsible_agent="Geospatial & Geofencing Agent",
                selected_tool="check_geofence_status",
                input_parameters={},
                dependencies=["task_pfz_01"],
                step_id="STEP_04_GEOFENCE_VERIFICATION",
                thought="Validating distance to IMBL and ensuring candidate PFZ does not violate Marine Protected Areas.",
                output_summary="Border safety verified for candidate zone."
            )
            tasks = [t_port, t_marine, t_pfz, t_geofence]
            dependencies = {
                "task_marine_obs_01": ["task_port_01"],
                "task_pfz_01": ["task_port_01"],
                "task_geofence_01": ["task_pfz_01"]
            }
            rationale = "PFZ focus: bypassed navigational routing calculations."

        # ----------------------------------------------------
        # SCENARIO 3C: SAFEST PFZ CANDIDATE ADVISORY (PHASE 7)
        # ----------------------------------------------------
        elif intent == "safest_pfz_advisory":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Departure Port",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Grounding coastal coordinates for candidate safety evaluation.",
                output_summary="Anchor port resolved."
            )
            t_weather = Task(
                task_id="task_weather_01",
                title="Ingest Marine Weather & Sea State",
                responsible_agent="Weather & Marine Hazard Agent",
                selected_tool="get_weather_at_point",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_02_WEATHER_HAZARD_INGESTION",
                thought="Ingesting real wave height, swell period, and wind speed for multi-factor risk assessment.",
                output_summary="Weather telemetry ingested."
            )
            t_cyclone = Task(
                task_id="task_cyclone_01",
                title="Check Active Tropical Cyclones",
                responsible_agent="Disaster Management Agent",
                selected_tool="get_active_cyclones_and_warnings",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_03_CYCLONE_CHECK",
                thought="Scanning North Indian Ocean basin for tropical depressions and gale warnings.",
                output_summary="Basin storm status verified."
            )
            t_pfz = Task(
                task_id="task_pfz_01",
                title="Discover Spatial PFZ Candidates",
                responsible_agent="Ocean Analytics & PFZ Agent",
                selected_tool="generate_pfz_hotspots",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_04_PFZ_GENERATION",
                thought="Retrieving candidate potential fishing zones from Earth Observation raster feeds.",
                output_summary="PFZ candidates generated."
            )
            t_geofence = Task(
                task_id="task_geofence_01",
                title="Verify Marine Protected Areas & Geofences",
                responsible_agent="Geospatial & Geofencing Agent",
                selected_tool="check_geofence_status",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_05_GEOFENCE_CHECK",
                thought="Verifying boundaries against Marine Protected Areas and international borders.",
                output_summary="Geofence baseline verified."
            )
            t_safety = Task(
                task_id="task_safety_01",
                title="Score Candidate Safety & Evaluate Decision Matrix",
                responsible_agent="Geospatial & Geofencing Agent",
                selected_tool="score_candidate_safety",
                input_parameters={},
                dependencies=["task_weather_01", "task_cyclone_01", "task_pfz_01", "task_geofence_01"],
                step_id="STEP_06_CANDIDATE_SAFETY_EVALUATION",
                thought="Evaluating Candidate Decision Matrix: separating PFZ suitability from operational risk to find safest zones.",
                output_summary="Candidate safety evaluated and ranked."
            )
            tasks = [t_port, t_weather, t_cyclone, t_pfz, t_geofence, t_safety]
            dependencies = {
                "task_weather_01": ["task_port_01"],
                "task_cyclone_01": ["task_port_01"],
                "task_pfz_01": ["task_port_01"],
                "task_geofence_01": ["task_port_01"],
                "task_safety_01": ["task_weather_01", "task_cyclone_01", "task_pfz_01", "task_geofence_01"]
            }
            rationale = "Safest PFZ focus: evaluated multi-factor marine risk and decision matrix across all candidates."

        # ----------------------------------------------------
        # SCENARIO 3B: SPATIAL PFZ RADIUS SEARCH (PHASE 6)
        # ----------------------------------------------------
        elif intent == "pfz_radius_search":
            dist_match = re.search(r'(\d+)\s*(?:km|nautical miles|nm|kilometres|kilometers)', context.query.lower())
            radius_km = float(dist_match.group(1)) if dist_match else 100.0
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Coastal Anchor",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Grounding coastal coordinates for geodesic radius filtering.",
                output_summary="Anchor port resolved."
            )
            t_weather = Task(
                task_id="task_weather_01",
                title="Ingest Marine Weather & Hazards",
                responsible_agent="Weather & Marine Hazard Agent",
                selected_tool="get_weather_at_point",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_02_WEATHER_HAZARD_INGESTION",
                thought="Ingesting wave height and wind speed for environmental hazard fusion.",
                output_summary="Weather telemetry ingested."
            )
            t_cyclone = Task(
                task_id="task_cyclone_01",
                title="Check Active Tropical Cyclones",
                responsible_agent="Disaster Management Agent",
                selected_tool="get_active_cyclones_and_warnings",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_03_CYCLONE_CHECK",
                thought="Scanning North Indian Ocean basin for active tropical depressions.",
                output_summary="Basin storm status verified."
            )
            t_spatial_pfz = Task(
                task_id="task_spatial_pfz_01",
                title=f"Search Spatial PFZ Candidates within {radius_km:.0f} km",
                responsible_agent="Ocean Analytics & PFZ Agent",
                selected_tool="find_pfz_within_radius",
                input_parameters={"radius_km": radius_km},
                dependencies=["task_port_01", "task_weather_01", "task_cyclone_01"],
                step_id="STEP_04_SPATIAL_PFZ_RADIUS_SEARCH",
                thought=f"Executing geodetic radius filtering ({radius_km:.0f} km) with multi-variable front clustering and hazard fusion.",
                output_summary="Spatial candidate regions discovered and ranked."
            )
            t_pfz_legacy = Task(
                task_id="task_pfz_01",
                title="Generate Standard PFZ Hotspots",
                responsible_agent="Ocean Analytics & PFZ Agent",
                selected_tool="generate_pfz_hotspots",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_05_LEGACY_PFZ_HOTSPOTS",
                thought="Generating standard EEZ PFZ hotspots for contract consistency.",
                output_summary="Standard PFZ hotspots generated."
            )
            tasks = [t_port, t_weather, t_cyclone, t_spatial_pfz, t_pfz_legacy]
            dependencies = {
                "task_weather_01": ["task_port_01"],
                "task_cyclone_01": ["task_port_01"],
                "task_spatial_pfz_01": ["task_port_01", "task_weather_01", "task_cyclone_01"],
                "task_pfz_01": ["task_port_01"]
            }
            rationale = f"Phase 6 spatial PFZ radius search ({radius_km:.0f} km) with multi-variable front clustering and hazard fusion."

        # ----------------------------------------------------
        # SCENARIO 4: ROUTE PLANNING INQUIRY
        # ----------------------------------------------------
        elif intent == "safe_navigation_route":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Departure Harbour",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Resolving vessel departure harbour for navigational routing.",
                output_summary="Departure harbour determined."
            )
            t_geofence = Task(
                task_id="task_geofence_01",
                title="Verify Port Geofence & Border Buffer",
                responsible_agent="Geospatial & Geofencing Agent",
                selected_tool="check_geofence_status",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_02_GEOFENCE_VERIFICATION",
                thought="Checking IMBL proximity at departure point.",
                output_summary="Geofence baseline verified."
            )
            t_route = Task(
                task_id="task_route_01",
                title="Compute Border-Safe Navigational Route",
                responsible_agent="Route Planning Agent",
                selected_tool="compute_safe_route",
                input_parameters={},
                dependencies=["task_port_01", "task_geofence_01"],
                step_id="STEP_03_SAFE_ROUTE_COMPUTATION",
                thought="Generating A* collision-avoiding maritime waypoints with fuel and transit time estimation.",
                output_summary="Safe navigational route computed."
            )
            tasks = [t_port, t_geofence, t_route]
            dependencies = {
                "task_geofence_01": ["task_port_01"],
                "task_route_01": ["task_port_01", "task_geofence_01"]
            }
            rationale = "Navigational Route focus: bypassed PFZ hotspot engine."

        # ----------------------------------------------------
        # SCENARIO 5: SPATIAL EARTH OBSERVATION & RASTER INQUIRY
        # ----------------------------------------------------
        elif intent == "spatial_eo_raster":
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Reference Coastal Region",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Grounding spatial query to reference coastal region and bounding box.",
                output_summary="Spatial bounding region resolved."
            )

            q_lower = (context.query or "").lower()
            tasks = [t_port]
            dep_dict = {}

            if "gradient" in q_lower or "sharp" in q_lower or "front" in q_lower:
                var_target = "sea_surface_temperature" if ("sst" in q_lower or "temp" in q_lower) else "chlorophyll_a"
                t_grad = Task(
                    task_id="task_eo_grad_01",
                    title="Compute Physical Horizontal Spatial Gradients",
                    responsible_agent="Marine Data Discovery Agent",
                    selected_tool="get_spatial_gradient",
                    input_parameters={"variable": var_target},
                    dependencies=["task_port_01"],
                    step_id="STEP_02_SPATIAL_GRADIENT_CALCULATION",
                    thought=f"Calculating geodetic spacing-aware horizontal derivatives for {var_target} to locate thermal/ocean color fronts.",
                    output_summary="Horizontal spatial gradients and frontal points calculated."
                )
                tasks.append(t_grad)
                dep_dict["task_eo_grad_01"] = ["task_port_01"]
            elif "contour" in q_lower:
                var_target = "chlorophyll_a" if ("chlorophyll" in q_lower or "chl" in q_lower) else "sea_surface_temperature"
                t_contours = Task(
                    task_id="task_eo_contour_01",
                    title="Generate Vector GeoJSON Contours",
                    responsible_agent="Marine Data Discovery Agent",
                    selected_tool="get_raster_contours",
                    input_parameters={"variable": var_target},
                    dependencies=["task_port_01"],
                    step_id="STEP_02_GEOJSON_CONTOUR_GENERATION",
                    thought=f"Extracting vector contour intervals for {var_target} from satellite raster field.",
                    output_summary="GeoJSON contour bands generated."
                )
                tasks.append(t_contours)
                dep_dict["task_eo_contour_01"] = ["task_port_01"]
            elif "chlorophyll" in q_lower or "chl" in q_lower:
                t_chl = Task(
                    task_id="task_eo_chl_01",
                    title="Retrieve Oceansat-3 OCM-3 Chlorophyll-a Spatial Raster",
                    responsible_agent="Marine Data Discovery Agent",
                    selected_tool="get_chlorophyll_raster",
                    input_parameters={},
                    dependencies=["task_port_01"],
                    step_id="STEP_02_CHLOROPHYLL_RASTER_INGESTION",
                    thought="Retrieving Level-3 gridded Chlorophyll-a field from ISRO Oceansat-3 (EOS-06) OCM-3 sensor.",
                    output_summary="Chlorophyll-a spatial field retrieved."
                )
                t_stats = Task(
                    task_id="task_eo_stats_01",
                    title="Compute Zonal Chlorophyll Statistics",
                    responsible_agent="Marine Data Discovery Agent",
                    selected_tool="get_satellite_region_statistics",
                    input_parameters={"variable": "chlorophyll_a"},
                    dependencies=["task_port_01"],
                    step_id="STEP_03_REGIONAL_STATISTICS",
                    thought="Calculating regional mean, median, min, max, and valid ocean pixel percentage.",
                    output_summary="Zonal statistics computed over valid ocean pixels."
                )
                tasks.extend([t_chl, t_stats])
                dep_dict["task_eo_chl_01"] = ["task_port_01"]
                dep_dict["task_eo_stats_01"] = ["task_port_01"]
            else:
                # Default SST spatial raster
                t_sst = Task(
                    task_id="task_eo_sst_01",
                    title="Retrieve INSAT-3DR / SLSTR Sea Surface Temperature Raster",
                    responsible_agent="Marine Data Discovery Agent",
                    selected_tool="get_sst_raster",
                    input_parameters={},
                    dependencies=["task_port_01"],
                    step_id="STEP_02_SST_RASTER_INGESTION",
                    thought="Retrieving Level-3 Sea Surface Temperature spatial field from ISRO INSAT-3DR Imager.",
                    output_summary="SST spatial field retrieved."
                )
                t_stats = Task(
                    task_id="task_eo_stats_01",
                    title="Compute Zonal SST Statistics",
                    responsible_agent="Marine Data Discovery Agent",
                    selected_tool="get_satellite_region_statistics",
                    input_parameters={"variable": "sea_surface_temperature"},
                    dependencies=["task_port_01"],
                    step_id="STEP_03_REGIONAL_STATISTICS",
                    thought="Calculating regional SST mean, median, min, max, and valid ocean pixel percentage.",
                    output_summary="Zonal SST statistics computed over valid ocean pixels."
                )
                tasks.extend([t_sst, t_stats])
                dep_dict["task_eo_sst_01"] = ["task_port_01"]
                dep_dict["task_eo_stats_01"] = ["task_port_01"]

            dependencies = dep_dict
            rationale = "Spatial Earth Observation focus: activated scientific satellite raster extraction and geodetic analysis. Bypassed PFZ ML prediction and vessel routing."

        # ----------------------------------------------------
        # SCENARIO 6: COMPOSITE MISSION / FULL ADVISORY
        # ----------------------------------------------------
        else:
            t_port = Task(
                task_id="task_port_01",
                title="Resolve Reference Port & Spatial Anchor",
                responsible_agent="Geospatial Grounding Agent",
                selected_tool="resolve_reference_port",
                input_parameters={
                    "query": context.query,
                    "user_lat": context.user_lat,
                    "user_lon": context.user_lon,
                    "reference_port_override": effective_port_override
                },
                step_id="STEP_01_PORT_GROUNDING",
                thought="Grounding user query to nearest reference fishing harbour and geographical anchor.",
                output_summary="Anchor port resolved."
            )
            t_marine = Task(
                task_id="task_marine_obs_01",
                title="Retrieve Satellite Earth Observation Telemetry",
                responsible_agent="Marine Data Discovery Agent",
                selected_tool="get_point_observation",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_02_MARINE_DATA_INGESTION",
                thought="Retrieving Oceansat-3 OCM-3 and INSAT-3DR oceanographic radiometry.",
                output_summary="Radiometric satellite telemetry ingested."
            )
            t_weather = Task(
                task_id="task_weather_01",
                title="Evaluate Meteocean Hazard & Sea Safety",
                responsible_agent="Weather & Marine Disaster Hazard Agent",
                selected_tool="get_weather_at_point",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_03_WEATHER_HAZARD_EVALUATION",
                thought="Computing wave height, Beaufort sea-state, and coastal safety score.",
                output_summary="Meteocean hazard analysis completed."
            )
            t_cyclone = Task(
                task_id="task_cyclone_01",
                title="Scan Regional Cyclone Warnings",
                responsible_agent="Disaster Intelligence Agent",
                selected_tool="get_active_cyclones_and_warnings",
                input_parameters={},
                dependencies=[],
                step_id="STEP_03B_CYCLONE_HAZARD_SCAN",
                thought="Scanning for active cyclones and heavy swell alerts across the basin.",
                output_summary="Cyclone intelligence verified."
            )
            t_pfz = Task(
                task_id="task_pfz_01",
                title="Compute Potential Fishing Zone Hotspots",
                responsible_agent="Ocean Analytics & PFZ Agent",
                selected_tool="generate_pfz_hotspots",
                input_parameters={},
                dependencies=["task_port_01"],
                step_id="STEP_04_OCEAN_PFZ_ANALYTICS",
                thought="Computing thermal-chlorophyll front gradient coincidence (|∇SST| × |∇Chl-a|).",
                output_summary="Candidate PFZ zones ranked."
            )
            t_geofence = Task(
                task_id="task_geofence_01",
                title="Verify IMBL Geofencing & Marine Protected Areas",
                responsible_agent="Geospatial & Geofencing Agent",
                selected_tool="check_geofence_status",
                input_parameters={},
                dependencies=["task_pfz_01"],
                step_id="STEP_05_GEOFENCE_VERIFICATION",
                thought="Verifying distance to International Maritime Boundary Line and MPA compliance.",
                output_summary="Geofence compliance verified."
            )
            t_route = Task(
                task_id="task_route_01",
                title="Compute Safe Navigational Route",
                responsible_agent="Route Planning Agent",
                selected_tool="compute_safe_route",
                input_parameters={},
                dependencies=["task_port_01", "task_pfz_01", "task_geofence_01"],
                step_id="STEP_06_SAFE_ROUTE_COMPUTATION",
                thought="Generating border-safe route from port to top PFZ candidate with fuel and ETA metrics.",
                output_summary="Safe navigational route generated."
            )
            tasks = [t_port, t_marine, t_weather, t_cyclone, t_pfz, t_geofence, t_route]
            dependencies = {
                "task_marine_obs_01": ["task_port_01"],
                "task_weather_01": ["task_port_01"],
                "task_pfz_01": ["task_port_01"],
                "task_geofence_01": ["task_pfz_01"],
                "task_route_01": ["task_port_01", "task_pfz_01", "task_geofence_01"]
            }
            rationale = "Composite mission: executed full multi-agent dependency DAG."

        plan = ExecutionPlan(
            user_goal=context.query,
            intent=intent,
            complexity=complexity,
            tasks=tasks,
            dependencies=dependencies,
            rationale=rationale
        )
        context.plan = plan
        return plan
