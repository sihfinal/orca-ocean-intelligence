"""
Geospatial Safety, Geofencing & Route Optimization Schemas
ISRO SIH 2026 - Problem Statement 26176
Phase 7: Geofencing, Risk/Safety & Real Route Optimization
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class GeofenceType(str, Enum):
    """
    Categorization of spatial regulatory boundaries and maritime barriers.
    Section 4 requirement.
    """
    MARINE_PROTECTED_AREA = "MARINE_PROTECTED_AREA"
    NO_FISHING_ZONE = "NO_FISHING_ZONE"
    MILITARY_EXCLUSION_ZONE = "MILITARY_EXCLUSION_ZONE"
    SHIPPING_LANE = "SHIPPING_LANE"
    CYCLONE_EXCLUSION_ZONE = "CYCLONE_EXCLUSION_ZONE"
    INTERNATIONAL_BORDER_BUFFER = "INTERNATIONAL_BORDER_BUFFER"
    PORT_SECURITY_ZONE = "PORT_SECURITY_ZONE"
    RESEARCH_PROHIBITED_AREA = "RESEARCH_PROHIBITED_AREA"
    CUSTOM_OPERATIONAL_ZONE = "CUSTOM_OPERATIONAL_ZONE"

class GeofenceStatus(str, Enum):
    """
    Geofence restriction state.
    Section 8 requirement: UNKNOWN must never be converted to CLEAR.
    """
    CLEAR = "CLEAR"                         # Verified outside all known restrictions
    RESTRICTED = "RESTRICTED"               # Intersects or inside authoritative restricted area
    NEAR_RESTRICTION = "NEAR_RESTRICTION"   # Within configurable safety buffer corridor
    UNKNOWN = "UNKNOWN"                     # Boundary data unavailable; do NOT assume clear

class SafetyClassification(str, Enum):
    """
    Comprehensive operational safety classification.
    Section 3 requirement.
    """
    SAFE = "SAFE"                           # Verified safe sea state and unrestricted waters
    ACCEPTABLE = "ACCEPTABLE"               # Moderate conditions within vessel tolerance
    CAUTION = "CAUTION"                     # Moderate waves/wind or border buffer proximity
    HIGH_RISK = "HIGH_RISK"                 # Severe waves, gale winds, or cyclone proximity
    NO_GO = "NO_GO"                         # Extreme peril or authoritative closure
    RESTRICTED = "RESTRICTED"               # Legally prohibited / MPA violation
    UNKNOWN = "UNKNOWN"                     # Missing data prevents determination
    UNAVAILABLE = "UNAVAILABLE"             # Data services unreachable

class DecisionState(str, Enum):
    """
    Candidate Decision Matrix State.
    Section 14 requirement: Combines PFZ Suitability, Marine Risk, and Geofence status.
    """
    PREFERRED = "PREFERRED"                 # High PFZ + Low Risk + Clear Geofence
    HAZARDOUS = "HAZARDOUS"                 # High PFZ + High Risk (Not recommended due to danger)
    NO_GO = "NO_GO"                         # Overlaps restricted area or severe cyclone
    POSSIBLE = "POSSIBLE"                   # Moderate PFZ + Low Risk + Clear
    LOW_PRIORITY = "LOW_PRIORITY"           # Low PFZ score
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE" # Required data unknown or unavailable

class Geofence(BaseModel):
    """
    Canonical Vector Geofence Representation.
    Section 4 & 5 requirement.
    """
    id: str = Field(..., description="Deterministic identifier")
    name: str = Field(..., description="Authoritative name of area")
    type: GeofenceType = Field(..., description="Geofence category")
    geometry_type: str = Field("Polygon", description="Polygon, MultiPolygon, or LineString")
    coordinates: Any = Field(..., description="RFC 7946 GeoJSON coordinates [[lon, lat], ...]")
    jurisdiction: str = Field(..., description="Legal authority (e.g. Ministry of Environment, Forest & Climate Change, Indian Coast Guard)")
    effective_start: Optional[str] = Field(None, description="ISO timestamp for start of validity")
    effective_end: Optional[str] = Field(None, description="ISO timestamp for end of validity")
    status: str = Field("ACTIVE", description="ACTIVE, INACTIVE, SEASONAL_CLOSED, EXPIRED")
    restrictions: List[str] = Field(default_factory=list, description="Specific legal/regulatory prohibitions")
    description: str = Field("", description="Detailed narrative description")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Source provenance citations")
    source_url: Optional[str] = Field(None, description="Official citation URL or gazette reference")

class CandidateSafetyEvaluation(BaseModel):
    """
    Evaluates Phase 6 PFZ Candidates across Geofence and Risk dimensions.
    Section 9, 13 & 14 requirement: Separates PFZ score from Risk score.
    """
    candidate_id: str = Field(..., description="ID of the evaluated PFZ candidate")
    name: str = Field(..., description="Candidate region name")
    centroid_lat: float = Field(..., description="Centroid latitude")
    centroid_lon: float = Field(..., description="Centroid longitude")
    
    # Independent Metrics (Section 13)
    pfz_score: float = Field(..., description="Environmental suitability score [0.0 - 1.0]")
    risk_score: float = Field(..., description="Operational & maritime risk score [0.0 - 1.0]")
    safety_classification: SafetyClassification = Field(..., description="Operational safety rating")
    geofence_status: GeofenceStatus = Field(..., description="Regulatory boundary compliance status")
    
    # Boundary Proximity
    nearest_restriction_name: Optional[str] = Field(None, description="Closest restricted boundary")
    nearest_restriction_dist_km: Optional[float] = Field(None, description="Distance to nearest restriction in km")
    
    # Decision Matrix (Section 14)
    decision_state: DecisionState = Field(..., description="Decision matrix result")
    decision_rationale: str = Field(..., description="Transparent explanation of the recommendation")
    traceable_reasons: List[str] = Field(default_factory=list, description="Specific factual factors contributing to evaluation")
    
    temporal_validity: str = Field(..., description="Valid time interval")
    limitations: List[str] = Field(default_factory=list, description="Scientific caveats and data assumptions")

class RouteWaypoint(BaseModel):
    """
    Individual waypoint along the optimized navigable path.
    """
    waypoint_index: int = Field(...)
    lat: float = Field(...)
    lon: float = Field(...)
    distance_from_start_km: float = Field(...)
    distance_to_dest_km: float = Field(...)
    leg_distance_km: float = Field(...)
    bearing_deg: float = Field(...)
    cell_cost: float = Field(..., description="A* traversal cost weight for this grid cell")
    hazard_description: str = Field("Clear Waters", description="Sea state or environmental conditions at cell")
    safety_status: str = Field("SAFE", description="SAFE, CAUTION, or BUFFER")

class OptimizedRoute(BaseModel):
    """
    Least-cost, hazard-aware, border-compliant vessel route.
    Section 16, 17, 20 & 26 requirements.
    """
    route_id: str = Field(..., description="Unique deterministic route identifier")
    route_type: str = Field("LEAST_COST", description="LEAST_COST, SHORTEST_DISTANCE, or MAX_SAFETY_AVOIDANCE")
    origin: Dict[str, Any] = Field(..., description="Starting harbour or coordinate")
    destination: Dict[str, Any] = Field(..., description="Target PFZ candidate or destination coordinate")
    route_geometry: Dict[str, Any] = Field(..., description="RFC 7946 GeoJSON LineString geometry")
    waypoints: List[RouteWaypoint] = Field(default_factory=list, description="Sequential navigational waypoints")
    
    # Distance and Navigation Metrics
    direct_distance_km: float = Field(..., description="Great-circle baseline distance in km")
    routed_distance_km: float = Field(..., description="Actual optimized path distance in km")
    routed_distance_nm: float = Field(..., description="Distance in nautical miles")
    total_cost: float = Field(..., description="Cumulative cost integral from A* surface")
    
    # Practical Vessel Performance Assumptions
    cruising_speed_knots: float = Field(9.5, description="Labeled vessel speed assumption (typical Indian 40ft trawler)")
    estimated_transit_time_hours: float = Field(..., description="Transit time based strictly on labeled cruising speed")
    estimated_fuel_burn_litres: float = Field(..., description="Estimated diesel burn based on 14.5 L/hr average")
    
    # Safety and Explanations (Section 22)
    risk_classification: SafetyClassification = Field(SafetyClassification.SAFE)
    restrictions_avoided: List[str] = Field(default_factory=list, description="List of restricted polygons bypassed")
    hazard_segments: List[Dict[str, Any]] = Field(default_factory=list, description="Segments with elevated wave/wind conditions")
    deviation_explanations: List[str] = Field(default_factory=list, description="Explanations for why the route bent away from straight line")
    
    # Mandatory Decision Support Disclaimers (Section 26 & 43)
    decision_support_only: bool = Field(True, description="Strictly for advisory planning, not certified ECDIS navigation")
    navigation_certified: bool = Field(False, description="Not a SOLAS/IMO certified navigation chart")
    limitations: List[str] = Field(default_factory=list)

class RouteOptimizationResponse(BaseModel):
    """
    Standard response payload for route optimization inquiries.
    Section 38 requirement.
    """
    status: str = Field("OK", description="Status code: OK, NO_VALID_ROUTE, UNAVAILABLE")
    origin: Dict[str, Any] = Field(default_factory=dict)
    destination: Dict[str, Any] = Field(default_factory=dict)
    selected_route: Optional[OptimizedRoute] = Field(None)
    alternative_routes: List[OptimizedRoute] = Field(default_factory=list)
    cost_surface_metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: List[Dict[str, Any]] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    decision_support_only: bool = Field(True)
    navigation_certified: bool = Field(False)
