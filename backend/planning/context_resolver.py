"""
Context & Reference Resolution Engine for Multi-Turn ORCA Conversations
ISRO SIH 2026 - Problem Statement 26176
Resolves pronouns, deictic references, ordinals, and explicit overrides against ConversationState.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from backend.memory.models import ConversationState
from backend.temporal.resolver import TemporalResolver
from backend.temporal.models import TimeWindow
from backend.data.geodata import INDIAN_PORTS

class ResolvedQueryContext:
    """
    Structured outcome of the context resolution stage.
    Carries resolved coastal anchors, candidate references, and temporal windows into the planner.
    """
    def __init__(
        self,
        raw_query: str,
        resolved_port: Optional[Dict[str, Any]] = None,
        resolved_destination: Optional[Dict[str, Any]] = None,
        resolved_time_window: Optional[TimeWindow] = None,
        reference_resolutions: Optional[List[Dict[str, Any]]] = None,
        is_ambiguous: bool = False,
        ambiguity_reason: Optional[str] = None
    ):
        self.raw_query = raw_query
        self.resolved_port = resolved_port
        self.resolved_destination = resolved_destination
        self.resolved_time_window = resolved_time_window
        self.reference_resolutions = reference_resolutions or []
        self.is_ambiguous = is_ambiguous
        self.ambiguity_reason = ambiguity_reason

class ContextResolver:
    """
    Resolves an incoming user turn using prior conversation memory and temporal context.
    Enforces strict precedence: Explicit input > Recent structured state > Fallback.
    """
    def __init__(self, temporal_resolver: Optional[TemporalResolver] = None):
        self.temporal_resolver = temporal_resolver or TemporalResolver()

    def resolve_context(
        self,
        query: str,
        session: Optional[ConversationState] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        reference_port_override: Optional[str] = None
    ) -> ResolvedQueryContext:
        q = (query or "").lower().strip()
        resolutions: List[Dict[str, Any]] = []

        # ----------------------------------------------------
        # 1. Temporal Resolution
        # ----------------------------------------------------
        time_window = self.temporal_resolver.resolve(query)
        if time_window:
            resolutions.append({
                "type": "TEMPORAL",
                "label": time_window.label,
                "start": time_window.start_datetime.isoformat(),
                "end": time_window.end_datetime.isoformat(),
                "is_future": time_window.is_future
            })

        # ----------------------------------------------------
        # 2. Location Precedence: Explicit query > Session memory > GPS > Fallback
        # ----------------------------------------------------
        explicit_port_key = None
        if reference_port_override and reference_port_override in INDIAN_PORTS:
            explicit_port_key = reference_port_override
        else:
            for p_key, p_data in INDIAN_PORTS.items():
                if p_key in q or p_data["name"].lower() in q:
                    explicit_port_key = p_key
                    break

        resolved_port = None
        if explicit_port_key:
            # Explicit location stated in current turn ALWAYS wins (Section 35)
            resolved_port = {"port_key": explicit_port_key, **INDIAN_PORTS[explicit_port_key]}
            resolutions.append({"type": "LOCATION_EXPLICIT", "port": explicit_port_key})
        elif session and session.structured and session.structured.active_port:
            # Carry forward remembered location from prior turns (Section 6 & 12)
            resolved_port = session.structured.active_port
            resolutions.append({"type": "LOCATION_CONTINUITY", "port": resolved_port.get("port_key")})
        elif user_lat is not None and user_lon is not None and abs(user_lat) > 0.1:
            # Fall back to GPS
            closest_k = "kochi"
            min_d_sq = float("inf")
            for k, p in INDIAN_PORTS.items():
                d_sq = (p["lat"] - user_lat) ** 2 + (p["lon"] - user_lon) ** 2
                if d_sq < min_d_sq:
                    min_d_sq = d_sq
                    closest_k = k
            resolved_port = {"port_key": closest_k, **INDIAN_PORTS[closest_k]}
            resolutions.append({"type": "LOCATION_GPS", "port": closest_k})
        else:
            # Default fallback
            resolved_port = {"port_key": "kochi", **INDIAN_PORTS["kochi"]}

        # ----------------------------------------------------
        # 3. Follow-up Reference Resolution: "closest", "safest", ordinals, pronouns
        # ----------------------------------------------------
        resolved_dest = None
        is_ambiguous = False
        ambiguity_reason = None

        candidates = session.structured.candidate_pfz_list if (session and session.structured) else []
        selected_pfz = session.structured.selected_pfz if (session and session.structured) else None

        # A. "Which is closest?" / "nearest" / Multilingual (Kannada, Hindi, Tamil, Malayalam)
        is_closest_query = any(k in q for k in [
            "closest", "nearest", "which is closer", "most nearby", "pass", "nazdeek", "najdik",
            "ಹತ್ತಿರ", "ಅತ್ತಿರ", "அருகில்", "அருகிலுள்ள", "അടുത്തത്", "ഏറ്റവും അടുത്തത്"
        ])

        if is_closest_query:
            if candidates:
                # Sort candidates by distance from port
                sorted_by_dist = sorted(
                    candidates,
                    key=lambda x: x.get("distance_from_port_km") if x.get("distance_from_port_km") is not None else 999.0
                )
                resolved_dest = sorted_by_dist[0]
                resolutions.append({
                    "type": "CANDIDATE_SELECTION",
                    "criterion": "closest",
                    "resolved_zone": resolved_dest.get("name")
                })
            else:
                is_ambiguous = True
                ambiguity_reason = "Asked for closest zone, but no candidate fishing zones exist in recent conversation history."

        # B. Ordinal selection: "first one", "second zone", "third option"
        elif any(k in q for k in ["second one", "second zone", "second option", "zone 2", "2nd"]):
            if len(candidates) >= 2:
                resolved_dest = candidates[1]
                resolutions.append({
                    "type": "ORDINAL_SELECTION",
                    "index": 2,
                    "resolved_zone": resolved_dest.get("name")
                })
            elif len(candidates) == 1:
                is_ambiguous = True
                ambiguity_reason = "Requested second zone, but only 1 candidate zone was identified in the previous turn."
            else:
                is_ambiguous = True
                ambiguity_reason = "Requested second zone, but no candidate list exists in conversation history."

        elif any(k in q for k in ["first one", "first zone", "first option", "zone 1", "1st"]):
            if len(candidates) >= 1:
                resolved_dest = candidates[0]
                resolutions.append({
                    "type": "ORDINAL_SELECTION",
                    "index": 1,
                    "resolved_zone": resolved_dest.get("name")
                })
            else:
                is_ambiguous = True
                ambiguity_reason = "Requested first zone, but no candidate list exists in conversation history."

        # C. Pronoun / Deictic reference: "it", "there", "that zone", "that location", "that area"
        elif any(k in q for k in ["route there", "route to it", "navigate there", "way there", "go there", "will it be safe", "is it safe", "how far is it", "is that area restricted"]):
            if selected_pfz:
                resolved_dest = selected_pfz
                resolutions.append({
                    "type": "PRONOUN_RESOLUTION",
                    "reference": "it/there",
                    "resolved_to": selected_pfz.get("name")
                })
            elif candidates:
                resolved_dest = candidates[0]
                resolutions.append({
                    "type": "PRONOUN_RESOLUTION",
                    "reference": "it/there",
                    "resolved_to": candidates[0].get("name")
                })
            elif session and session.structured and session.structured.active_port:
                resolutions.append({
                    "type": "PRONOUN_RESOLUTION",
                    "reference": "there",
                    "resolved_to": session.structured.active_port.get("name")
                })

        return ResolvedQueryContext(
            raw_query=query,
            resolved_port=resolved_port,
            resolved_destination=resolved_dest,
            resolved_time_window=time_window,
            reference_resolutions=resolutions,
            is_ambiguous=is_ambiguous,
            ambiguity_reason=ambiguity_reason
        )
