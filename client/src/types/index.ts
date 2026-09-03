export interface SatelliteTelemetry {
  id: string;
  name: string;
  sensors: string[];
  status: string;
  orbit: string;
  last_pass: string;
  next_pass: string;
  data_latency: string;
  health_score: number;
}

export interface PFZHotspot {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  recommended_depth_m: number;
  sst_celsius: number;
  chlorophyll_a_mg_m3: number;
  thermal_gradient_c_per_10km: number;
  chlorophyll_gradient_per_10km: number;
  front_coincidence_index: number;
  confidence_score_percent: number;
  dominant_species: string;
  species_suitability_indices: Record<string, number>;
  catch_enhancement_multiplier: string;
  nearest_port: string;
  distance_from_port_km: number | null;
  distance_from_port_nm: number | null;
  bearing_from_port: string | null;
  validity: string;
  recommended_gear: string;
}

export interface WeatherObservation {
  latitude: number;
  longitude: number;
  wind_speed_knots: number;
  wind_speed_kmph: number;
  wind_direction_degrees: number;
  significant_wave_height_m: number;
  swell_period_seconds: number;
  beaufort_scale: number;
  sea_state: string;
  lightning_probability_percent: number;
  visibility_km: number;
  safety_index: number;
  safety_status: 'SAFE_FOR_VENTURE' | 'EXERCISE_CAUTION' | 'HAZARDOUS_NO_VENTURE';
  safety_badge_color: string;
  actionable_advice: string;
  cyclone_influence: {
    active_cyclone: string | null;
    distance_km: number | null;
    intensity: string | null;
  };
  timestamp: string;
}

export interface GeofenceStatus {
  latitude: number;
  longitude: number;
  nearest_imbl: {
    border_name: string;
    distance_km: number;
    distance_nautical_miles: number;
    threat_level: string;
    status_code: string;
    alert_message: string;
  };
  marine_protected_area_status: {
    is_inside_mpa: boolean;
    violation_details: any;
    compliance_note: string;
  };
}

export interface RouteWaypoint {
  waypoint_index: number;
  latitude: number;
  longitude: number;
  leg_name: string;
  distance_to_imbl_nm: number;
  waypoint_safety: string;
}

export interface NavigationRoute {
  origin: {
    port_key: string;
    name: string;
    latitude: number;
    longitude: number;
  };
  destination: {
    name: string;
    latitude: number;
    longitude: number;
  };
  route_metrics: {
    direct_distance_km: number;
    routed_distance_km: number;
    routed_distance_nm: number;
    cruising_speed_knots: number;
    estimated_transit_time_hours: number;
    estimated_fuel_burn_litres: number;
    coastal_safety_index: number;
    route_status: string;
  };
  waypoints: RouteWaypoint[];
}

export interface AgentExecutionStep {
  step_id: string;
  agent: string;
  status: string;
  duration_ms: number;
  thought: string;
  output_summary: string;
}

export interface OfficialBulletin {
  bulletin_id: string;
  issuing_authority: string;
  department: string;
  issue_date: string;
  validity_period: string;
  coastal_sector: string;
  sea_venture_verdict: string;
  safety_index_score: number;
  recommended_pfz_count: number;
  top_pfz_advisories: PFZHotspot[];
  meteorological_summary: {
    wave_height_m: number;
    wind_speed_knots: number;
    sea_state: string;
    squall_lightning_risk: string;
  };
  geofence_advisory: string;
  emergency_contact: string;
  qr_verification_token: string;
}

export interface ChatResponsePayload {
  query: string;
  detected_intent: string;
  language: {
    code: string;
    name: string;
    native: string;
    voice_code: string;
  };
  reference_port: {
    name: string;
    state: string;
    lat: number;
    lon: number;
    region: string;
    primary_catch: string[];
  };
  response: {
    markdown: string;
    tts_speech_text: string;
    model_engine?: string;
  };
  top_pfz: PFZHotspot;
  all_pfz_hotspots: PFZHotspot[];
  weather_and_safety: WeatherObservation;
  geofence_status: GeofenceStatus;
  safe_navigation_route: NavigationRoute;
  satellite_telemetry: SatelliteTelemetry[];
  official_bulletin: OfficialBulletin;
  evidence_and_provenance: {
    query: string;
    overall_confidence_percent: number;
    execution_steps_count: number;
    execution_trace: AgentExecutionStep[];
    data_provenance_citations: Array<{
      source: string;
      parameter: string;
      spatial_resolution: string;
      temporal_latency: string;
      validation: string;
    }>;
    verification_status: string;
    generated_at: string;
  };
    execution_metadata: {
    total_agents_involved: number;
    total_latency_ms: number;
    llm_engine?: string;
    timestamp: string;
  };
  // Phase 8 & 9 Decision, Evidence & Spatial Intelligence Fields
  decision?: DecisionObject;
  recommendation?: string;
  decision_status?: DecisionStatusType;
  supporting_factors?: string[];
  negative_factors?: string[];
  operational_risks?: string[];
  data_limitations?: string[];
  claim_validation?: ClaimValidationResult;
  evidence_package?: EvidencePackage;
  pfz_candidates?: SpatialPFZCandidate[];
}

export type DecisionStatusType = 
  | 'RECOMMENDED'
  | 'ACCEPTABLE'
  | 'CAUTION'
  | 'NOT_RECOMMENDED'
  | 'NO_GO'
  | 'INSUFFICIENT_EVIDENCE'
  | 'UNAVAILABLE'
  | 'CONFLICTING_EVIDENCE';

export interface ConfidenceDecomposition {
  overall_confidence: number;
  source_quality_score: number;
  spatial_resolution_score: number;
  temporal_relevance_score: number;
  front_sharpness_score: number;
  geofence_reliability_score: number;
  uncertainty_sources: string[];
}

export interface CandidateComparison {
  candidate_id: string;
  name: string;
  suitability_delta: number;
  risk_delta: number;
  distance_delta_km: number;
  preference_reason: string;
}

export interface DecisionObject {
  decision_id: string;
  decision_status: DecisionStatusType;
  recommendation_title: string;
  recommended_target_id?: string;
  recommended_target_name?: string;
  supporting_factors: string[];
  negative_factors: string[];
  operational_risks: string[];
  confidence: ConfidenceDecomposition;
  data_limitations: string[];
  reversibility_triggers: string[];
  candidate_tradeoffs: CandidateComparison[];
  provenance_graph: Array<{
    stage: string;
    parameter: string;
    source: string;
    type: string;
    evidence_id?: string;
  }>;
}

export interface EvidenceItem {
  evidence_id: string;
  parameter_name: string;
  claim: string;
  numeric_value?: number | null;
  unit?: string;
  timestamp: string;
  source_name: string;
  source_type: string;
  is_forecast: boolean;
  freshness: 'FRESH' | 'STALE' | 'EXPIRED';
  age_hours: number;
  processing_step: string;
  relationship_to_decision: string;
  provenance_url?: string;
}

export interface EvidencePackage {
  query: string;
  items: EvidenceItem[];
  missing_variables: string[];
  stale_variables: string[];
  data_freshness_summary: Record<string, string>;
  conflicting_indicators: string[];
}

export interface ClaimValidationResult {
  is_valid: boolean;
  validation_status: string;
  unsupported_numeric_claims: string[];
  unsupported_source_claims: string[];
  contradicted_safety_claims: string[];
  safe_fallback_text?: string;
}

export interface SpatialPFZCandidate {
  candidate_id: string;
  name: string;
  centroid: {
    lat: number;
    lon: number;
  };
  area_km2: number;
  polygon_coordinates: [number, number][];
  suitability_score: number;
  risk_score: number;
  geofence_status: 'CLEAR' | 'RESTRICTED' | 'BUFFER_PROXIMITY' | 'UNKNOWN';
  distance_km?: number;
  confidence_percent?: number;
}

export interface OperationalAlert {
  alert_id: string;
  type: 'CYCLONE' | 'EXTREME_SEA' | 'IMBL_BREACH' | 'RESTRICTED_MPA' | 'STALE_DATA' | 'ADVISORY';
  severity: 'CRITICAL' | 'WARNING' | 'ADVISORY' | 'INFO';
  title: string;
  message: string;
  timestamp: string;
  affected_zone?: string;
  source: string;
  acknowledged: boolean;
}

export interface TemporalSelection {
  mode: 'OBSERVATION' | 'FORECAST';
  target_datetime: string;
  time_label: string;
  is_mismatch?: boolean;
  mismatch_message?: string;
}

