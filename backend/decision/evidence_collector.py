"""
Evidence Collector & Provenance Tracking Engine
ISRO SIH 2026 - Problem Statement 26176
Phase 8: Decision Engine, Explainability, Evidence & Provenance
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from backend.decision.schemas import (
    SourceType,
    FreshnessState,
    EvidenceItem,
    EvidencePackage
)

class EvidenceCollector:
    """
    Harvests deterministic facts from context, evaluates variable-specific freshness,
    distinguishes physical observations from forecasts, and constructs the provenance graph.
    """

    # Variable-specific freshness thresholds in hours (Section 21)
    FRESHNESS_THRESHOLDS_HOURS = {
        "sea_surface_temperature": {"fresh": 48.0, "expired": 120.0},
        "chlorophyll_a": {"fresh": 48.0, "expired": 120.0},
        "significant_wave_height": {"fresh": 6.0, "expired": 24.0},
        "wind_speed": {"fresh": 6.0, "expired": 24.0},
        "tropical_cyclone": {"fresh": 3.0, "expired": 12.0},
        "official_advisory": {"fresh": 24.0, "expired": 48.0},
        "geofence_boundary": {"fresh": 720.0, "expired": 2160.0}, # 30 - 90 days
        "route_traversal": {"fresh": 2.0, "expired": 12.0}
    }

    def __init__(self):
        pass

    def _evaluate_freshness(self, timestamp_str: Optional[str], var_key: str) -> Tuple[FreshnessState, float]:
        """
        Determines freshness state (FRESH, STALE, EXPIRED) and age in hours based on variable type.
        """
        if not timestamp_str:
            return FreshnessState.STALE, 999.0

        try:
            # Handle ISO formats
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age_hours = max(0.0, (now - ts).total_seconds() / 3600.0)
        except Exception:
            return FreshnessState.STALE, 999.0

        thresholds = self.FRESHNESS_THRESHOLDS_HOURS.get(
            var_key, {"fresh": 24.0, "expired": 72.0}
        )

        if age_hours <= thresholds["fresh"]:
            return FreshnessState.FRESH, round(age_hours, 2)
        elif age_hours <= thresholds["expired"]:
            return FreshnessState.STALE, round(age_hours, 2)
        else:
            return FreshnessState.EXPIRED, round(age_hours, 2)

    def collect_evidence(
        self,
        query: str,
        context_bundle: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> EvidencePackage:
        """
        Transforms raw, normalized, and derived context data into an auditable EvidencePackage.
        """
        evidence_items: List[EvidenceItem] = []
        provenance_chain: List[Dict[str, Any]] = []
        missing_vars: List[str] = []
        stale_vars: List[str] = []
        conflicting_indicators: List[str] = []
        freshness_summary: Dict[str, str] = {}
        has_official_advisories = False

        now_utc = datetime.now(timezone.utc).isoformat()

        # ---------------------------------------------------------------------
        # 1. Weather: Wave Height & Sea State
        # ---------------------------------------------------------------------
        weather = context_bundle.get("weather") or {}
        if weather and "significant_wave_height_m" in weather:
            hs = weather.get("significant_wave_height_m")
            w_ts = weather.get("timestamp") or weather.get("time") or now_utc
            is_fc = weather.get("data_type") == "FORECAST" or weather.get("is_forecast", False)
            src_name = weather.get("source_name") or weather.get("source") or "Open-Meteo Marine API"
            src_type = SourceType.FORECAST if is_fc else SourceType.OBSERVATION
            freshness, age = self._evaluate_freshness(w_ts, "significant_wave_height")
            freshness_summary["wave_height"] = freshness.value
            if freshness in [FreshnessState.STALE, FreshnessState.EXPIRED]:
                stale_vars.append("wave_height")

            relationship = "NEGATIVE_FACTOR" if (hs is not None and hs >= 2.5) else "SUPPORTING"

            item_hs = EvidenceItem(
                evidence_id=f"EV-WAVE-{uuid.uuid4().hex[:6]}",
                parameter_name="significant_wave_height",
                claim=f"Significant wave height is {hs} m ({'Forecast' if is_fc else 'Observation'}).",
                numeric_value=float(hs) if hs is not None else None,
                unit="m",
                timestamp=str(w_ts),
                source_name=str(src_name),
                source_type=src_type,
                is_forecast=is_fc,
                freshness=freshness,
                age_hours=age,
                processing_step="WEATHER_INGESTION",
                relationship_to_decision=relationship,
                provenance_url="https://marine-api.open-meteo.com"
            )
            evidence_items.append(item_hs)
            provenance_chain.append({
                "stage": "RAW_FEED",
                "parameter": "wave_height",
                "source": src_name,
                "type": src_type.value,
                "evidence_id": item_hs.evidence_id
            })
        else:
            missing_vars.append("significant_wave_height")

        # ---------------------------------------------------------------------
        # 2. Weather: Wind Speed & Gusts
        # ---------------------------------------------------------------------
        if weather and "wind_speed_knots" in weather:
            wind = weather.get("wind_speed_knots")
            w_ts = weather.get("timestamp") or weather.get("time") or now_utc
            is_fc = weather.get("data_type") == "FORECAST" or weather.get("is_forecast", False)
            src_name = weather.get("source_name") or weather.get("source") or "Open-Meteo Weather API"
            src_type = SourceType.FORECAST if is_fc else SourceType.OBSERVATION
            freshness, age = self._evaluate_freshness(w_ts, "wind_speed")
            freshness_summary["wind_speed"] = freshness.value

            relationship = "NEGATIVE_FACTOR" if (wind is not None and wind >= 25.0) else "SUPPORTING"

            item_wind = EvidenceItem(
                evidence_id=f"EV-WIND-{uuid.uuid4().hex[:6]}",
                parameter_name="wind_speed",
                claim=f"Sustained 10m wind speed is {wind} knots ({'Forecast' if is_fc else 'Observation'}).",
                numeric_value=float(wind) if wind is not None else None,
                unit="kts",
                timestamp=str(w_ts),
                source_name=str(src_name),
                source_type=src_type,
                is_forecast=is_fc,
                freshness=freshness,
                age_hours=age,
                processing_step="WEATHER_INGESTION",
                relationship_to_decision=relationship,
                provenance_url="https://api.open-meteo.com"
            )
            evidence_items.append(item_wind)
            provenance_chain.append({
                "stage": "WEATHER_TELEMETRY",
                "parameter": "wind_speed",
                "source": src_name,
                "type": src_type.value,
                "evidence_id": item_wind.evidence_id
            })
        else:
            missing_vars.append("wind_speed")

        # ---------------------------------------------------------------------
        # 3. Cyclones & Marine Warnings
        # ---------------------------------------------------------------------
        cyclones = context_bundle.get("cyclones") or {}
        if cyclones:
            c_name = cyclones.get("name") or "North Indian Ocean Basin Status"
            c_active = cyclones.get("is_active", False)
            c_storms = cyclones.get("active_storms", [])
            c_src = cyclones.get("source") or "GDACS & IMD RSMC Tropical Cyclone Feed"
            freshness, age = self._evaluate_freshness(cyclones.get("timestamp") or now_utc, "tropical_cyclone")
            freshness_summary["cyclone"] = freshness.value
            has_official_advisories = True

            rel = "NEGATIVE_FACTOR" if (c_active or len(c_storms) > 0) else "SUPPORTING"
            claim_text = (
                f"Active cyclonic system: {c_name} in progress."
                if (c_active or len(c_storms) > 0)
                else "No active cyclonic storms or tropical depressions tracked in basin."
            )

            item_cyclone = EvidenceItem(
                evidence_id=f"EV-CYCLONE-{uuid.uuid4().hex[:6]}",
                parameter_name="tropical_cyclone",
                claim=claim_text,
                numeric_value=1.0 if (c_active or len(c_storms) > 0) else 0.0,
                unit="status",
                timestamp=str(cyclones.get("timestamp") or now_utc),
                source_name=str(c_src),
                source_type=SourceType.OFFICIAL,
                is_forecast=False,
                freshness=freshness,
                age_hours=age,
                processing_step="DISASTER_ALERT_INGESTION",
                relationship_to_decision=rel,
                provenance_url="https://www.gdacs.org"
            )
            evidence_items.append(item_cyclone)
            provenance_chain.append({
                "stage": "OFFICIAL_ADVISORY",
                "parameter": "cyclone",
                "source": c_src,
                "type": SourceType.OFFICIAL.value,
                "evidence_id": item_cyclone.evidence_id
            })

        # ---------------------------------------------------------------------
        # 4. Satellite Earth Observation: SST & Thermal Fronts
        # ---------------------------------------------------------------------
        raster = context_bundle.get("satellite_raster") or {}
        pfz_analysis = context_bundle.get("pfz_analysis") or {}

        sst_val = raster.get("mean") if raster.get("variable") == "sea_surface_temperature" else None
        if sst_val is not None and isinstance(sst_val, (int, float)):
            sst_src = raster.get("source") or "ISRO MOSDAC / IMD New Delhi"
            sst_acq = raster.get("acquisition_time") or now_utc
            freshness, age = self._evaluate_freshness(sst_acq, "sea_surface_temperature")
            freshness_summary["sea_surface_temperature"] = freshness.value
            if freshness in [FreshnessState.STALE, FreshnessState.EXPIRED]:
                stale_vars.append("sea_surface_temperature")

            item_sst = EvidenceItem(
                evidence_id=f"EV-SST-{uuid.uuid4().hex[:6]}",
                parameter_name="sea_surface_temperature",
                claim=f"Regional mean Sea Surface Temperature is {sst_val:.2f}°C (Satellite Observation).",
                numeric_value=float(sst_val),
                unit="deg_C",
                timestamp=str(sst_acq),
                source_name=str(sst_src),
                source_type=SourceType.OBSERVATION,
                is_forecast=False,
                freshness=freshness,
                age_hours=age,
                processing_step="L3_RASTER_OBSERVATION",
                relationship_to_decision="SUPPORTING",
                provenance_url="https://mosdac.gov.in"
            )
            evidence_items.append(item_sst)
            provenance_chain.append({
                "stage": "SATELLITE_EO",
                "parameter": "sea_surface_temperature",
                "source": sst_src,
                "type": SourceType.OBSERVATION.value,
                "evidence_id": item_sst.evidence_id
            })

        # ---------------------------------------------------------------------
        # 5. Geofence & Protected Areas
        # ---------------------------------------------------------------------
        geofence = context_bundle.get("geofence") or {}
        if geofence:
            gf_status = geofence.get("geofence_status") or "CLEAR"
            gf_name = geofence.get("matched_geofence", {}).get("name") if geofence.get("matched_geofence") else None
            gf_dist = geofence.get("distance_to_nearest_geofence_km") or geofence.get("distance_to_nearest_km")

            rel = "NEGATIVE_FACTOR" if gf_status in ["RESTRICTED", "NEAR_RESTRICTION"] else "SUPPORTING"
            claim_text = (
                f"Vessel coordinate is inside RESTRICTED boundary: {gf_name}."
                if gf_status == "RESTRICTED"
                else (
                    f"Vessel coordinate is NEAR RESTRICTION boundary: {gf_name} ({gf_dist:.1f} km buffer)."
                    if gf_status == "NEAR_RESTRICTION"
                    else f"Clear of known Marine Protected Areas and international borders."
                )
            )

            item_gf = EvidenceItem(
                evidence_id=f"EV-GF-{uuid.uuid4().hex[:6]}",
                parameter_name="geofence_status",
                claim=claim_text,
                string_value=str(gf_status),
                numeric_value=float(gf_dist) if gf_dist is not None else None,
                unit="km" if gf_dist is not None else "",
                timestamp=now_utc,
                source_name="Ministry of External Affairs & Wildlife Institute of India",
                source_type=SourceType.OFFICIAL,
                is_forecast=False,
                freshness=FreshnessState.FRESH,
                age_hours=0.0,
                processing_step="GEOFENCE_VERIFICATION",
                relationship_to_decision=rel,
                provenance_url="https://wii.gov.in"
            )
            evidence_items.append(item_gf)
            provenance_chain.append({
                "stage": "GEOFENCE_SAFETY",
                "parameter": "geofence_status",
                "source": item_gf.source_name,
                "type": SourceType.OFFICIAL.value,
                "evidence_id": item_gf.evidence_id
            })

        # ---------------------------------------------------------------------
        # 6. Route Navigation Feasibility (Phase 7)
        # ---------------------------------------------------------------------
        route = context_bundle.get("route") or {}
        if route:
            r_status = route.get("status") or "OK"
            sel_route = route.get("selected_route") or {}
            r_dist = sel_route.get("routed_distance_nm") or route.get("total_distance_nm")

            rel = "NEGATIVE_FACTOR" if r_status == "NO_VALID_ROUTE" else "SUPPORTING"
            claim_text = (
                f"Navigational route resolved: {r_dist} NM ({sel_route.get('estimated_transit_time_hours', 0)} hrs transit at 9.5 kts)."
                if r_status == "OK"
                else f"No valid collision-free maritime route found: destination or path obstructed."
            )

            item_route = EvidenceItem(
                evidence_id=f"EV-ROUTE-{uuid.uuid4().hex[:6]}",
                parameter_name="route_traversal",
                claim=claim_text,
                numeric_value=float(r_dist) if r_dist is not None else None,
                string_value=str(r_status),
                unit="NM",
                timestamp=now_utc,
                source_name="ORCA A* Maritime Least-Cost Route Optimizer",
                source_type=SourceType.DERIVED,
                is_forecast=False,
                freshness=FreshnessState.FRESH,
                age_hours=0.0,
                processing_step="A_STAR_ROUTE_OPTIMIZATION",
                relationship_to_decision=rel
            )
            evidence_items.append(item_route)
            provenance_chain.append({
                "stage": "ROUTE_OPTIMIZATION",
                "parameter": "route_traversal",
                "source": item_route.source_name,
                "type": SourceType.DERIVED.value,
                "evidence_id": item_route.evidence_id
            })

        # ---------------------------------------------------------------------
        # 7. Check Conflicting Indicators (e.g. high PFZ vs hazardous sea)
        # ---------------------------------------------------------------------
        top_pfz = context_bundle.get("top_pfz") or {}
        pfz_score = top_pfz.get("score") or top_pfz.get("suitability_score") or 0.0
        wave_val = weather.get("significant_wave_height_m", 0.0) if weather else 0.0

        if pfz_score >= 0.70 and wave_val >= 2.8:
            conflicting_indicators.append(
                f"Environmental suitability is highly favorable ({pfz_score:.2f}/1.0), but wave height ({wave_val:.1f}m) exceeds safe operational threshold for coastal craft."
            )

        return EvidencePackage(
            query=query,
            session_id=session_id,
            collected_at=now_utc,
            items=evidence_items,
            data_freshness_summary=freshness_summary,
            provenance_chain=provenance_chain,
            missing_variables=missing_vars,
            stale_variables=stale_vars,
            conflicting_indicators=conflicting_indicators,
            official_advisories_present=has_official_advisories
        )
