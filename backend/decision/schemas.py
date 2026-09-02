"""
Phase 8 Decision Engine, Explainability, Evidence & Provenance Schemas
ISRO SIH 2026 - Problem Statement 26176
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class SourceType(str, Enum):
    OFFICIAL = "OFFICIAL"                      # Authoritative national agency (e.g. INCOIS, IMD, Navy)
    OBSERVATION = "OBSERVATION"                # Physical in-situ or satellite measurement
    FORECAST = "FORECAST"                      # Numerical weather/ocean forecast model
    DERIVED = "DERIVED"                        # Computed by ORCA mathematical models
    MODEL_PREDICTION = "MODEL_PREDICTION"      # Statistical/ML classification or prediction
    USER_PROVIDED = "USER_PROVIDED"            # Ingested from user query or preference
    TEST = "TEST"                              # Synthetic deterministic test fixture (never real evidence)

class FreshnessState(str, Enum):
    FRESH = "FRESH"                            # Within configured valid freshness window
    STALE = "STALE"                            # Exceeds freshness window, caution advised
    EXPIRED = "EXPIRED"                        # Past operational validity threshold

class UserObjective(str, Enum):
    BALANCE_SUITABILITY_AND_SAFETY = "BALANCE_SUITABILITY_AND_SAFETY"
    MAXIMIZE_SUITABILITY = "MAXIMIZE_SUITABILITY"
    MINIMIZE_RISK = "MINIMIZE_RISK"
    MINIMIZE_DISTANCE = "MINIMIZE_DISTANCE"
    AVOID_RESTRICTIONS = "AVOID_RESTRICTIONS"

class DecisionType(str, Enum):
    PFZ_RECOMMENDATION = "PFZ_RECOMMENDATION"
    SAFETY_RECOMMENDATION = "SAFETY_RECOMMENDATION"
    ROUTE_RECOMMENDATION = "ROUTE_RECOMMENDATION"
    ALTERNATIVE_COMPARISON = "ALTERNATIVE_COMPARISON"
    DATA_AVAILABILITY_DECISION = "DATA_AVAILABILITY_DECISION"
    ADVISORY_INTERPRETATION = "ADVISORY_INTERPRETATION"

class DecisionStatus(str, Enum):
    RECOMMENDED = "RECOMMENDED"                # Operationally sound, favorable suitability, safe
    ACCEPTABLE = "ACCEPTABLE"                  # Favorable, but requires standard watch
    CAUTION = "CAUTION"                        # Moderate risk or approaching buffer corridor
    NOT_RECOMMENDED = "NOT_RECOMMENDED"        # Unfavorable biology, excessive risk, or poor data
    NO_GO = "NO_GO"                            # Prohibited entry, severe storm, or critical hazard
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE" # Missing critical variables; no false SAFE claim
    UNAVAILABLE = "UNAVAILABLE"                # Out of coverage, offline feeds, or future timestamps
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE" # Disagreeing indicators require heightened caution

class EvidenceItem(BaseModel):
    """
    Structured atomic unit of evidence supporting or qualifying a decision.
    """
    evidence_id: str
    parameter_name: str
    claim: str
    numeric_value: Optional[float] = None
    string_value: Optional[str] = None
    unit: str = ""
    timestamp: str
    source_name: str
    source_type: SourceType
    is_forecast: bool = False
    target_time_window: Optional[str] = None
    spatial_coverage: Optional[str] = None
    freshness: FreshnessState = FreshnessState.FRESH
    age_hours: float = 0.0
    quality_confidence: float = 1.0            # [0.0 - 1.0]
    processing_step: str = "RAW_INGESTION"     # Step in the provenance chain
    relationship_to_decision: str = "SUPPORTING" # "SUPPORTING", "NEGATIVE_FACTOR", "CONSTRAINT", "NEUTRAL"
    provenance_url: Optional[str] = None

class ConfidenceDecomposition(BaseModel):
    """
    Inspectable breakdown of the recommendation confidence score.
    """
    overall_confidence: float                  # [0.0 - 1.0]
    data_coverage_score: float                 # [0.0 - 1.0]
    source_quality_score: float                # [0.0 - 1.0]
    variable_agreement_score: float            # [0.0 - 1.0]
    temporal_relevance_score: float            # [0.0 - 1.0]
    forecast_certainty_score: float            # [0.0 - 1.0]
    uncertainty_sources: List[str] = Field(default_factory=list)
    confidence_rationale: str = ""

class CandidateComparison(BaseModel):
    """
    Structured side-by-side comparison of multiple candidate zones or trajectories.
    """
    primary_candidate_id: str
    primary_name: str
    compared_candidate_id: str
    compared_name: str
    suitability_delta: float                   # Primary PFZ score minus compared PFZ score
    risk_delta: float                          # Primary risk minus compared risk
    distance_delta_km: float                   # Primary distance minus compared distance
    tradeoff_summary: str
    advantages_of_primary: List[str] = Field(default_factory=list)
    disadvantages_of_primary: List[str] = Field(default_factory=list)
    recommendation_rationale: str

class DecisionObject(BaseModel):
    """
    Complete, auditable, and traceable decision object produced by ORCADecisionEngine.
    """
    decision_id: str
    decision_type: DecisionType
    user_objective: UserObjective = UserObjective.BALANCE_SUITABILITY_AND_SAFETY
    recommendation_title: str
    recommended_target_id: Optional[str] = None
    recommended_target_name: Optional[str] = None
    decision_status: DecisionStatus
    confidence: ConfidenceDecomposition
    supporting_factors: List[str] = Field(default_factory=list)
    negative_factors: List[str] = Field(default_factory=list)    # Never hide risks
    hard_safety_gates_triggered: List[str] = Field(default_factory=list)
    alternative_options: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_comparisons: List[CandidateComparison] = Field(default_factory=list)
    operational_risks: List[str] = Field(default_factory=list)
    data_limitations: List[str] = Field(default_factory=list)
    assumptions_made: List[str] = Field(default_factory=list)
    reversibility_conditions: List[str] = Field(default_factory=list) # What would change the decision
    evidence_ids: List[str] = Field(default_factory=list)
    evidence_summary: List[Dict[str, Any]] = Field(default_factory=list)
    provenance_graph: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    valid_until: Optional[str] = None
    decision_support_only: bool = True
    navigation_certified: bool = False

class EvidencePackage(BaseModel):
    """
    Complete evidence package bundling atomic evidence items, DAG provenance, and limits.
    """
    query: str
    session_id: Optional[str] = None
    collected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    items: List[EvidenceItem] = Field(default_factory=list)
    data_freshness_summary: Dict[str, str] = Field(default_factory=dict)
    provenance_chain: List[Dict[str, Any]] = Field(default_factory=list)
    missing_variables: List[str] = Field(default_factory=list)
    stale_variables: List[str] = Field(default_factory=list)
    conflicting_indicators: List[str] = Field(default_factory=list)
    official_advisories_present: bool = False

class ClaimValidationResult(BaseModel):
    """
    Deterministic verification record ensuring natural language text does not contradict evidence.
    """
    is_valid: bool
    unsupported_numeric_claims: List[str] = Field(default_factory=list)
    unsupported_source_claims: List[str] = Field(default_factory=list)
    contradictions_detected: List[str] = Field(default_factory=list)
    fabricated_citations: List[str] = Field(default_factory=list)
    validation_status: str = "VERIFIED_ACCURATE" # or "FLAGGED_FABRICATION"
    safe_fallback_text: Optional[str] = None
