"""
Deterministic Claim Verifier for ORCA Responses
ISRO SIH 2026 - Problem Statement 26176
Phase 8: Decision Engine, Explainability, Evidence & Provenance
"""

import re
from typing import Dict, Any, List, Optional
from backend.decision.schemas import (
    DecisionObject,
    EvidencePackage,
    ClaimValidationResult,
    DecisionStatus
)

class ClaimVerifier:
    """
    Deterministic guardian of the LLM trust boundary.
    Validates natural-language response text against structured evidence to prevent:
    - Unsupported numeric claims (e.g. fabricating 1.5m waves when evidence says 3.4m)
    - Fabricated source names or citations
    - Statements contradicting structured safety/geofence classifications
    """

    KNOWN_VALID_SOURCES = [
        "isro", "oceansat", "insat", "mosdac", "incois", "imd", "open-meteo",
        "gdacs", "copernicus", "eumetsat", "sentinel", "nrsc", "ministry",
        "orca", "indian navy", "coast guard", "wildlife institute"
    ]

    HALLUCINATION_PATTERNS = [
        (r"nasa marine weather", "NASA Marine Weather"),
        (r"us oceanic command", "US Oceanic Command"),
        (r"global sea intelligence", "Global Sea Intelligence"),
        (r"pacific ocean fleet", "Pacific Ocean Fleet"),
        (r"noaa south asian marine division", "NOAA South Asian Marine Division")
    ]

    def __init__(self):
        pass

    def verify_response_claims(
        self,
        text: str,
        decision: DecisionObject,
        evidence_pkg: EvidencePackage
    ) -> ClaimValidationResult:
        """
        Scans natural-language text for factual consistency against the evidence package.
        """
        text_lower = text.lower()
        unsupported_nums: List[str] = []
        unsupported_sources: List[str] = []
        contradictions: List[str] = []
        fabricated_cites: List[str] = []

        # ---------------------------------------------------------------------
        # 1. Numeric Claim Verification
        # ---------------------------------------------------------------------
        # Look for wave height claims like "X.X m" or "X.X meters"
        wave_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:m|meters|metre)\b", text_lower)
        actual_wave = None
        for ev in evidence_pkg.items:
            if ev.parameter_name == "significant_wave_height" and ev.numeric_value is not None:
                actual_wave = ev.numeric_value
                break

        if actual_wave is not None and wave_matches:
            # Check if any stated wave value contradicts actual wave by > 0.5m
            for wm in wave_matches:
                try:
                    val = float(wm)
                    # Ignore numbers that might be distance, time, etc. unless close or wave-related
                    # If text explicitly says "wave ... val m" or "val m wave"
                    if ("wave" in text_lower or "lahar" in text_lower or "sea" in text_lower):
                        if abs(val - actual_wave) > 0.6 and (val < 10.0):  # Waves under 10m
                            # Check if the number appears adjacent to "wave" or "height"
                            pattern = rf"(?:wave|waves|height|swells?)[^.]{{0,30}}{val}\s*(?:m|meters)"
                            rev_pattern = rf"{val}\s*(?:m|meters)[^.]{{0,30}}(?:wave|waves|height|swells?)"
                            if re.search(pattern, text_lower) or re.search(rev_pattern, text_lower):
                                unsupported_nums.append(
                                    f"Text claims wave height {val}m, which contradicts structured evidence of {actual_wave}m."
                                )
                except Exception:
                    pass

        # ---------------------------------------------------------------------
        # 2. Source Name & Citation Verification (Prevent Hallucinations)
        # ---------------------------------------------------------------------
        for pattern, label in self.HALLUCINATION_PATTERNS:
            if re.search(pattern, text_lower):
                unsupported_sources.append(
                    f"Text cites non-existent/fabricated source: '{label}'."
                )

        # Check for citation URLs in text
        url_matches = re.findall(r"https?://[^\s)\]]+", text)
        for u in url_matches:
            # Ensure URL belongs to one of our verified sources
            is_valid_url = any(
                domain in u.lower() for domain in [
                    "open-meteo.com", "mosdac.gov.in", "incois.gov.in",
                    "gdacs.org", "imd.gov.in", "nrsc.gov.in", "isro.gov.in"
                ]
            )
            if not is_valid_url:
                fabricated_cites.append(f"Unverified or fabricated external URL: {u}")

        # ---------------------------------------------------------------------
        # 3. Contradiction Detection Against Safety Classification
        # ---------------------------------------------------------------------
        if decision.decision_status in [DecisionStatus.NO_GO, DecisionStatus.NOT_RECOMMENDED]:
            # The text must NOT claim operations are safe or permitted
            safe_phrases = [
                "completely safe", "safe to venture", "safe for venture",
                "normal fishing permitted", "safe route available", "no danger"
            ]
            for sp in safe_phrases:
                if sp in text_lower:
                    contradictions.append(
                        f"Text claims '{sp}' while structured decision engine determined {decision.decision_status.value}."
                    )

        if any("RESTRICTED" in g for g in decision.hard_safety_gates_triggered):
            if "permitted to fish" in text_lower or "allowed to fish" in text_lower:
                contradictions.append(
                    "Text claims fishing is permitted in an active restricted/exclusion zone."
                )

        is_valid = (
            len(unsupported_nums) == 0 and
            len(unsupported_sources) == 0 and
            len(contradictions) == 0 and
            len(fabricated_cites) == 0
        )

        safe_fallback: Optional[str] = None
        if not is_valid:
            # Generate deterministic truthful fallback text
            from backend.decision.explainability import ExplainabilityEngine
            safe_fallback = ExplainabilityEngine().format_decision_markdown(decision, evidence_pkg)

        return ClaimValidationResult(
            is_valid=is_valid,
            unsupported_numeric_claims=unsupported_nums,
            unsupported_source_claims=unsupported_sources,
            contradictions_detected=contradictions,
            fabricated_citations=fabricated_cites,
            validation_status="VERIFIED_ACCURATE" if is_valid else "FLAGGED_FABRICATION",
            safe_fallback_text=safe_fallback
        )
