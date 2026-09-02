"""
Marine Risk Assessment Engine & Candidate Decision Matrix
ISRO SIH 2026 - Problem Statement 26176
Phase 7: Geofencing, Risk/Safety & Real Route Optimization

Implements an explicit, multi-factor marine risk model combining:
- Significant wave height & swell
- Sustained wind speed & gusts
- Active tropical cyclone tracking
- Spatial restriction / geofence compliance
Maintains strict separation between PFZ suitability score and Marine Risk score (Section 13).
Evaluates structured Candidate Decision Matrix (Section 14).
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple

from backend.geospatial.schemas import (
    SafetyClassification,
    GeofenceStatus,
    DecisionState,
    CandidateSafetyEvaluation
)
from backend.geospatial.geofence_service import GeofenceService

logger = logging.getLogger("orca.geospatial.risk")

class MarineRiskEngine:
    """
    Scientific marine risk model for vessel transit and PFZ candidate safety.
    """

    # Configurable Component Weights (Section 12)
    WEIGHT_WAVE = 0.35
    WEIGHT_WIND = 0.25
    WEIGHT_CYCLONE = 0.25
    WEIGHT_GEOFENCE = 0.15

    # Thresholds for 36-45ft Indian Mechanized Trawler
    WAVE_CALM_M = 1.2
    WAVE_MODERATE_M = 2.0
    WAVE_SEVERE_M = 2.8
    WAVE_EXTREME_M = 4.0

    WIND_CALM_KTS = 12.0
    WIND_MODERATE_KTS = 20.0
    WIND_GALE_KTS = 28.0

    CYCLONE_PROXIMITY_PERIL_KM = 150.0
    CYCLONE_WARNING_BUFFER_KM = 350.0

    def __init__(self, geofence_service: Optional[GeofenceService] = None):
        self.geofence_service = geofence_service or GeofenceService()

    def evaluate_weather_risk(self, weather_telemetry: Optional[Dict[str, Any]]) -> Tuple[float, List[str], bool]:
        """
        Calculates weather and sea-state risk component [0.0 - 1.0].
        Returns (risk_component, list_of_factors, is_complete).
        """
        if not weather_telemetry:
            return 0.5, ["Weather telemetry unavailable; assuming moderate precautionary risk."], False

        factors = []
        wave_risk = 0.1
        wind_risk = 0.1

        # Wave height assessment
        sig_wave = weather_telemetry.get("significant_wave_height_m")
        if sig_wave is not None:
            if sig_wave <= self.WAVE_CALM_M:
                wave_risk = 0.05
                factors.append(f"Calm seas: wave height {sig_wave}m within safe limits.")
            elif sig_wave <= self.WAVE_MODERATE_M:
                wave_risk = 0.30
                factors.append(f"Moderate seas: wave height {sig_wave}m requires standard vigilance.")
            elif sig_wave <= self.WAVE_SEVERE_M:
                wave_risk = 0.70
                factors.append(f"Rough seas: wave height {sig_wave}m exceeds recommended threshold.")
            else:
                wave_risk = 1.0
                factors.append(f"Extreme seas: wave height {sig_wave}m presents capsizing peril.")
        else:
            factors.append("Wave telemetry unavailable in feed.")

        # Wind speed assessment
        wind_kts = weather_telemetry.get("wind_speed_knots")
        if wind_kts is not None:
            if wind_kts <= self.WIND_CALM_KTS:
                wind_risk = 0.05
                factors.append(f"Gentle breeze: wind {wind_kts} kts.")
            elif wind_kts <= self.WIND_MODERATE_KTS:
                wind_risk = 0.35
                factors.append(f"Moderate breeze: wind {wind_kts} kts.")
            elif wind_kts <= self.WIND_GALE_KTS:
                wind_risk = 0.75
                factors.append(f"Strong breeze / near-gale: wind {wind_kts} kts.")
            else:
                wind_risk = 1.0
                factors.append(f"Gale force winds: {wind_kts} kts dangerous for coastal craft.")
        else:
            factors.append("Wind telemetry unavailable in feed.")

        combined_weather_risk = 0.6 * wave_risk + 0.4 * wind_risk
        return combined_weather_risk, factors, True

    def evaluate_cyclone_risk(
        self,
        lat: float,
        lon: float,
        cyclone_info: Optional[Dict[str, Any]]
    ) -> Tuple[float, List[str]]:
        """
        Calculates cyclone and tropical depression proximity peril [0.0 - 1.0].
        Section 31 requirement: uses real distance from eye/track without fabricating track.
        """
        if not cyclone_info:
            return 0.0, ["No active tropical cyclones reported in basin."]

        active_storms = cyclone_info.get("active_storms", [])
        if not active_storms and not cyclone_info.get("is_active"):
            return 0.0, ["North Indian Ocean basin clear of tropical cyclones."]

        min_cyclone_dist = 999999.0
        closest_storm_name = "Tropical System"

        # Check explicit active cyclone structure
        c_lat = cyclone_info.get("current_lat")
        c_lon = cyclone_info.get("current_lon")
        if c_lat is not None and c_lon is not None:
            d = self.geofence_service._haversine_km(lat, lon, c_lat, c_lon)
            min_cyclone_dist = min(min_cyclone_dist, d)
            closest_storm_name = cyclone_info.get("name", "Active Cyclone")

        for storm in active_storms:
            s_lat = storm.get("latitude")
            s_lon = storm.get("longitude")
            if s_lat is not None and s_lon is not None:
                d = self.geofence_service._haversine_km(lat, lon, s_lat, s_lon)
                if d < min_cyclone_dist:
                    min_cyclone_dist = d
                    closest_storm_name = storm.get("name", "Cyclone")

        if min_cyclone_dist <= self.CYCLONE_PROXIMITY_PERIL_KM:
            return 1.0, [f"CRITICAL: Active storm '{closest_storm_name}' within {round(min_cyclone_dist, 1)} km. Severe maritime peril."]
        elif min_cyclone_dist <= self.CYCLONE_WARNING_BUFFER_KM:
            fraction = 1.0 - (min_cyclone_dist - self.CYCLONE_PROXIMITY_PERIL_KM) / (self.CYCLONE_WARNING_BUFFER_KM - self.CYCLONE_PROXIMITY_PERIL_KM)
            risk = 0.5 + 0.4 * fraction
            return round(risk, 2), [f"WARNING: Storm '{closest_storm_name}' within outer buffer ({round(min_cyclone_dist, 1)} km away)."]
        else:
            return 0.0, [f"Safe distance from nearest storm '{closest_storm_name}' ({round(min_cyclone_dist, 1)} km away)."]

    def evaluate_point_risk(
        self,
        lat: float,
        lon: float,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        cyclone_info: Optional[Dict[str, Any]] = None,
        time_window: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Calculates holistic marine risk score and safety rating for a given coordinate.
        """
        # 1. Geofence evaluation
        geofence_res = self.geofence_service.check_point(lat, lon, time_window=time_window)
        gf_status = geofence_res["geofence_status"]
        
        if gf_status == GeofenceStatus.RESTRICTED:
            gf_risk = 1.0
        elif gf_status == GeofenceStatus.NEAR_RESTRICTION:
            gf_risk = 0.5
        elif gf_status == GeofenceStatus.CLEAR:
            gf_risk = 0.0
        else:
            gf_risk = 0.5  # UNKNOWN

        # 2. Weather evaluation
        weather_risk, weather_factors, weather_complete = self.evaluate_weather_risk(weather_telemetry)

        # 3. Cyclone evaluation
        cyclone_risk, cyclone_factors = self.evaluate_cyclone_risk(lat, lon, cyclone_info)

        # Weighted aggregate risk score [0.0 - 1.0]
        aggregate_risk = (
            self.WEIGHT_WAVE * weather_risk +
            self.WEIGHT_WIND * weather_risk +
            self.WEIGHT_CYCLONE * cyclone_risk +
            self.WEIGHT_GEOFENCE * gf_risk
        )
        aggregate_risk = round(min(1.0, max(0.0, aggregate_risk)), 3)

        # Traceable reasons
        traceable_reasons = weather_factors + cyclone_factors
        if geofence_res.get("restrictions"):
            traceable_reasons.extend(geofence_res["restrictions"])

        # Determine Safety Classification (Section 3)
        if gf_status == GeofenceStatus.UNKNOWN and not weather_complete:
            classification = SafetyClassification.UNKNOWN
        elif gf_status == GeofenceStatus.RESTRICTED:
            classification = SafetyClassification.RESTRICTED
        elif cyclone_risk >= 0.9 or (weather_telemetry and weather_telemetry.get("significant_wave_height_m", 0) > self.WAVE_EXTREME_M):
            classification = SafetyClassification.NO_GO
        elif aggregate_risk >= 0.60:
            classification = SafetyClassification.HIGH_RISK
        elif aggregate_risk >= 0.35 or gf_status == GeofenceStatus.NEAR_RESTRICTION:
            classification = SafetyClassification.CAUTION
        elif aggregate_risk >= 0.20:
            classification = SafetyClassification.ACCEPTABLE
        else:
            classification = SafetyClassification.SAFE

        return {
            "latitude": lat,
            "longitude": lon,
            "aggregate_risk_score": aggregate_risk,
            "safety_classification": classification,
            "geofence_status": gf_status,
            "matched_geofence": geofence_res.get("matched_geofence"),
            "distance_to_nearest_geofence_km": geofence_res.get("distance_to_nearest_km"),
            "weather_risk": round(weather_risk, 3),
            "cyclone_risk": round(cyclone_risk, 3),
            "geofence_risk": round(gf_risk, 3),
            "traceable_reasons": traceable_reasons,
            "limitations": geofence_res.get("limitations", [])
        }

    def score_candidate_safety(
        self,
        candidate: Any,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        cyclone_info: Optional[Dict[str, Any]] = None,
        time_window: Optional[Any] = None
    ) -> CandidateSafetyEvaluation:
        """
        Evaluates a Phase 6 PFZ Candidate through the Candidate Decision Matrix (Section 14).
        Preserves independent PFZ Suitability Score vs Marine Risk Score (Section 13).
        """
        c_id = getattr(candidate, "candidate_id", "ORCA-CANDIDATE-01")
        name = getattr(candidate, "name", "Coastal PFZ Candidate")
        c_lat = getattr(candidate, "centroid_lat", 10.0)
        c_lon = getattr(candidate, "centroid_lon", 75.0)
        
        # Get raw PFZ score
        raw_pfz_score = getattr(candidate, "composite_suitability_score", 0.65)
        # Check candidate polygon coordinates if available
        cand_poly_obj = getattr(candidate, "polygon_geometry", None)
        poly_coords = None
        if cand_poly_obj and hasattr(cand_poly_obj, "coordinates"):
            poly_coords = cand_poly_obj.coordinates[0]

        # 1. Geofence evaluation (point or polygon)
        if poly_coords and len(poly_coords) >= 3:
            gf_res = self.geofence_service.check_candidate_polygon(poly_coords, time_window=time_window)
        else:
            gf_res = self.geofence_service.check_point(c_lat, c_lon, time_window=time_window)

        gf_status = gf_res["geofence_status"]

        # 2. Risk evaluation at centroid
        risk_res = self.evaluate_point_risk(
            c_lat, c_lon,
            weather_telemetry=weather_telemetry,
            cyclone_info=cyclone_info,
            time_window=time_window
        )
        risk_score = risk_res["aggregate_risk_score"]
        safety_class = risk_res["safety_classification"]

        # 3. Decision Matrix Evaluation (Section 14)
        if gf_status == GeofenceStatus.UNKNOWN:
            decision_state = DecisionState.INSUFFICIENT_EVIDENCE
            rationale = "Regulatory boundary data unavailable. Cannot verify zone legality."
        elif gf_status == GeofenceStatus.RESTRICTED:
            decision_state = DecisionState.NO_GO
            rationale = f"Candidate overlaps prohibited marine boundary ({gf_res.get('nearest_geofence') or 'Restricted Zone'}). Legal fishing ban enforced."
        elif safety_class in [SafetyClassification.NO_GO, SafetyClassification.HIGH_RISK]:
            decision_state = DecisionState.HAZARDOUS
            rationale = f"High oceanographic suitability ({raw_pfz_score:.2f}), but NOT RECOMMENDED due to hazardous maritime peril (Risk: {risk_score:.2f})."
        elif raw_pfz_score >= 0.60 and risk_score < 0.40 and gf_status == GeofenceStatus.CLEAR:
            decision_state = DecisionState.PREFERRED
            rationale = f"High environmental suitability ({raw_pfz_score:.2f}), low maritime risk ({risk_score:.2f}), and clear of all known restrictions."
        elif raw_pfz_score >= 0.45 and risk_score < 0.50:
            decision_state = DecisionState.POSSIBLE
            rationale = f"Moderate suitability ({raw_pfz_score:.2f}) with acceptable operating risk ({risk_score:.2f})."
        else:
            decision_state = DecisionState.LOW_PRIORITY
            rationale = f"Marginal thermal/chlorophyll frontal gradient strength ({raw_pfz_score:.2f}). Low operational priority."

        # Compile limitations
        limits = list(risk_res.get("limitations", []))
        if getattr(candidate, "limitations", None):
            limits.extend(candidate.limitations)

        return CandidateSafetyEvaluation(
            candidate_id=c_id,
            name=name,
            centroid_lat=c_lat,
            centroid_lon=c_lon,
            pfz_score=round(raw_pfz_score, 3),
            risk_score=round(risk_score, 3),
            safety_classification=safety_class,
            geofence_status=gf_status,
            nearest_restriction_name=gf_res.get("nearest_geofence") or gf_res.get("matched_geofence", {}).get("name") if isinstance(gf_res.get("matched_geofence"), dict) else None,
            nearest_restriction_dist_km=gf_res.get("distance_to_nearest_km"),
            decision_state=decision_state,
            decision_rationale=rationale,
            traceable_reasons=risk_res.get("traceable_reasons", []),
            temporal_validity=getattr(time_window, "label", "current_operational_cycle") if time_window else "current_operational_cycle",
            limitations=limits
        )

    def rank_candidates_by_safety(
        self,
        candidates: List[Any],
        weather_telemetry: Optional[Dict[str, Any]] = None,
        cyclone_info: Optional[Dict[str, Any]] = None,
        time_window: Optional[Any] = None
    ) -> List[CandidateSafetyEvaluation]:
        """
        Evaluates and ranks candidate zones so safest, highly favorable zones appear first.
        """
        evals = [
            self.score_candidate_safety(c, weather_telemetry, cyclone_info, time_window)
            for c in candidates
        ]

        # Sorting logic: PREFERRED first, then POSSIBLE, then HAZARDOUS, then LOW_PRIORITY, then NO_GO
        priority_map = {
            DecisionState.PREFERRED: 0,
            DecisionState.POSSIBLE: 1,
            DecisionState.LOW_PRIORITY: 2,
            DecisionState.HAZARDOUS: 3,
            DecisionState.NO_GO: 4,
            DecisionState.INSUFFICIENT_EVIDENCE: 5
        }

        # Sort by priority ascending, then by risk_score ascending, then by pfz_score descending
        evals.sort(key=lambda x: (priority_map.get(x.decision_state, 9), x.risk_score, -x.pfz_score))
        return evals
