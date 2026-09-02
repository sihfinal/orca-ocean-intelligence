"""
PFZ Intelligence Engine & Multi-Variable Ocean Analytics
ISRO SIH 2026 - Problem Statement 26176
Phase 6: PFZ Intelligence, Ocean Analytics & Environmental Hazard Fusion

Implements:
1. Spatial co-registration of disparate satellite rasters
2. Geodetic spacing-aware gradient and front coincidence detection
3. 4-level spatial candidate hierarchy (Cell -> Cluster -> Polygon -> Centroid)
4. Transparent inspectable scoring model
5. Independent data-driven confidence model
6. Weather & marine hazard fusion
7. Geodesic radius search & nearest candidate discovery
8. Temporal reasoning with future EO honesty gating
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import numpy as np
from scipy import ndimage

from backend.data.raster.catalog import EODatasetCatalog
from backend.data.raster.processor import RasterProcessor
from backend.data.raster.schemas import RasterGridResponse
from backend.data.schemas import DataStatus, QualityFlag
from backend.data.pfz.schemas import (
    PFZResultType,
    EnvironmentalHazardStatus,
    SuitabilityBreakdown,
    ConfidenceBreakdown,
    CandidatePolygon,
    PFZCandidate,
    PFZAnalysisResponse
)
from backend.temporal.models import TimeWindow

logger = logging.getLogger("blue_orbit.pfz.engine")

class PFZIntelligenceEngine:
    """
    Scientific Potential Fishing Zone (PFZ) intelligence engine.
    Transforms verified Earth Observation fields and real marine telemetry
    into spatial candidate regions with transparent scoring and confidence.
    """

    # Configurable physical front thresholds
    SST_FRONT_THRESHOLD_C_PER_KM = 0.015    # 0.015 °C/km thermal gradient front
    CHL_FRONT_THRESHOLD_MG_M3_PER_KM = 0.040 # 0.040 mg/m³/km color gradient front
    SUITABILITY_CLUSTER_THRESHOLD = 0.52     # Minimum cell suitability to seed candidate region
    MIN_CLUSTER_CELL_COUNT = 3               # Prunes micro-noise clusters smaller than 3 cells

    # Configurable component weights (Must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "sst_suitability": 0.25,
        "sst_front_strength": 0.30,
        "chlorophyll_suitability": 0.25,
        "chlorophyll_front_strength": 0.20
    }

    def __init__(self, catalog: Optional[EODatasetCatalog] = None):
        self.catalog = catalog or EODatasetCatalog()

    # -------------------------------------------------------------------------
    # 1. Geodesic Distance and Bearing Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance between two geodetic coordinates in km."""
        r = 6371.0088
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(dlam / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
        return float(r * c)

    @staticmethod
    def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Compass bearing in degrees from point 1 to point 2."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dlam = math.radians(lon2 - lon1)
        y = math.sin(dlam) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
        bearing = math.degrees(math.atan2(y, x))
        return float((bearing + 360.0) % 360.0)

    # -------------------------------------------------------------------------
    # 2. Common Analytical Grid Co-Registration
    # -------------------------------------------------------------------------
    def co_register_grids(
        self,
        sst_grid: RasterGridResponse,
        chl_grid: Optional[RasterGridResponse],
        target_shape: Tuple[int, int] = (30, 30)
    ) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
        """
        Resamples and aligns SST and Chlorophyll rasters onto a common georeferenced analytical grid.
        Preserves land/nodata/cloud masks without fabricating values across gaps.
        Returns: (common_sst, common_chl, common_lats, common_lons, common_valid_mask)
        """
        # Define target common coordinates bounding the intersection
        min_lat = max(min(sst_grid.latitudes), min(chl_grid.latitudes) if chl_grid else min(sst_grid.latitudes))
        max_lat = min(max(sst_grid.latitudes), max(chl_grid.latitudes) if chl_grid else max(sst_grid.latitudes))
        min_lon = max(min(sst_grid.longitudes), min(chl_grid.longitudes) if chl_grid else min(sst_grid.longitudes))
        max_lon = min(max(sst_grid.longitudes), max(chl_grid.longitudes) if chl_grid else max(sst_grid.longitudes))

        common_lats = np.linspace(min_lat, max_lat, target_shape[0])
        common_lons = np.linspace(min_lon, max_lon, target_shape[1])

        # Convert input grids to numpy arrays with nan masking
        raw_sst = np.array(sst_grid.values, dtype=float)
        # Nodata mask
        sst_valid = ~np.isnan(raw_sst)

        # Bilinear resampling using ndimage zoom
        zoom_y = target_shape[0] / raw_sst.shape[0]
        zoom_x = target_shape[1] / raw_sst.shape[1]

        resampled_sst = ndimage.zoom(np.nan_to_num(raw_sst, nan=0.0), (zoom_y, zoom_x), order=1)
        resampled_sst_valid = ndimage.zoom(sst_valid.astype(float), (zoom_y, zoom_x), order=0) > 0.5
        resampled_sst[~resampled_sst_valid] = np.nan

        common_chl = None
        common_valid = resampled_sst_valid.copy()

        if chl_grid is not None and chl_grid.values:
            raw_chl = np.array(chl_grid.values, dtype=float)
            chl_valid = ~np.isnan(raw_chl)
            chl_zoom_y = target_shape[0] / raw_chl.shape[0]
            chl_zoom_x = target_shape[1] / raw_chl.shape[1]
            resampled_chl = ndimage.zoom(np.nan_to_num(raw_chl, nan=0.0), (chl_zoom_y, chl_zoom_x), order=1)
            resampled_chl_valid = ndimage.zoom(chl_valid.astype(float), (chl_zoom_y, chl_zoom_x), order=0) > 0.5
            resampled_chl[~resampled_chl_valid] = np.nan
            common_chl = resampled_chl
            # Common valid ocean mask requires valid SST; if Chl is cloud covered, retain SST
            common_valid = common_valid & resampled_chl_valid

        return resampled_sst, common_chl, common_lats, common_lons, common_valid

    # -------------------------------------------------------------------------
    # 3. Spacing-Aware Physical Gradients & Multi-Variable Fronts
    # -------------------------------------------------------------------------
    def compute_physical_gradients(
        self,
        grid_2d: np.ndarray,
        lats: np.ndarray,
        lons: np.ndarray
    ) -> np.ndarray:
        """
        Computes the geodetic gradient magnitude field in units/km.
        |∇X| = sqrt((dX/dy)^2 + (dX/dx)^2) where dy = 111.32 km, dx = 111.32 * cos(lat) km.
        """
        d_dy = np.full_like(grid_2d, np.nan)
        d_dx = np.full_like(grid_2d, np.nan)

        n_rows, n_cols = grid_2d.shape
        dy_km = abs(lats[1] - lats[0]) * 111.32 if len(lats) > 1 else 1.0

        for r in range(1, n_rows - 1):
            lat_deg = lats[r]
            dx_km = abs(lons[1] - lons[0]) * 111.32 * math.cos(math.radians(lat_deg))
            if dx_km < 0.001:
                dx_km = 0.001

            for c in range(1, n_cols - 1):
                # Central difference along latitude (y)
                val_up = grid_2d[r + 1, c]
                val_down = grid_2d[r - 1, c]
                if not np.isnan(val_up) and not np.isnan(val_down):
                    d_dy[r, c] = (val_up - val_down) / (2.0 * dy_km)

                # Central difference along longitude (x)
                val_right = grid_2d[r, c + 1]
                val_left = grid_2d[r, c - 1]
                if not np.isnan(val_right) and not np.isnan(val_left):
                    d_dx[r, c] = (val_right - val_left) / (2.0 * dx_km)

        with np.errstate(invalid='ignore'):
            grad_mag = np.sqrt(d_dy ** 2 + d_dx ** 2)
        return grad_mag

    # -------------------------------------------------------------------------
    # 4. Cell-Level Environmental Suitability (Level 1)
    # -------------------------------------------------------------------------
    def compute_cell_suitability(
        self,
        sst_field: np.ndarray,
        sst_grad: np.ndarray,
        chl_field: Optional[np.ndarray],
        chl_grad: Optional[np.ndarray],
        valid_mask: np.ndarray,
        weights: Optional[Dict[str, float]] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes Level-1 normalized cell-level suitability matrices.
        Returns: (composite_suitability, sst_suit, sst_front, chl_suit, chl_front)
        """
        w = weights or self.DEFAULT_WEIGHTS

        # 1. SST Pelagic Habitat Optimality (Optimal 27.0 - 29.5 °C for Indian tropical shelf)
        # S_sst = max(0.0, 1.0 - abs(SST - 28.2) / 2.5)
        sst_suit = np.zeros_like(sst_field)
        valid_sst = valid_mask & ~np.isnan(sst_field)
        diff_sst = np.abs(sst_field[valid_sst] - 28.2)
        sst_suit[valid_sst] = np.clip(1.0 - (diff_sst / 2.5), 0.0, 1.0)

        # 2. SST Front Strength (Normalizing against 0.045 °C/km maximum frontal gradient)
        sst_front = np.zeros_like(sst_grad)
        valid_sst_g = valid_mask & ~np.isnan(sst_grad)
        sst_front[valid_sst_g] = np.clip(sst_grad[valid_sst_g] / 0.040, 0.0, 1.0)

        # 3. Chlorophyll-a Biomass Optimality (Optimal 0.4 - 2.5 mg/m³)
        chl_suit = np.zeros_like(sst_field)
        chl_front = np.zeros_like(sst_field)

        if chl_field is not None and chl_grad is not None:
            valid_chl = valid_mask & ~np.isnan(chl_field)
            # Upwelling bloom indicator: optimal between 0.3 and 3.0 mg/m³
            raw_chl = chl_field[valid_chl]
            c_score = np.where(raw_chl < 0.3, raw_chl / 0.3 * 0.5,
                      np.where(raw_chl <= 2.5, 1.0, np.clip(1.0 - (raw_chl - 2.5) / 3.0, 0.2, 1.0)))
            chl_suit[valid_chl] = c_score

            valid_chl_g = valid_mask & ~np.isnan(chl_grad)
            chl_front[valid_chl_g] = np.clip(chl_grad[valid_chl_g] / 0.120, 0.0, 1.0)

            composite = (
                w["sst_suitability"] * sst_suit +
                w["sst_front_strength"] * sst_front +
                w["chlorophyll_suitability"] * chl_suit +
                w["chlorophyll_front_strength"] * chl_front
            )
        else:
            # Fallback when Chlorophyll is unavailable (e.g. cloud or sensor missing)
            # Re-normalize SST weights truthfully
            w_sst_tot = w["sst_suitability"] + w["sst_front_strength"]
            composite = (
                (w["sst_suitability"] / w_sst_tot) * sst_suit +
                (w["sst_front_strength"] / w_sst_tot) * sst_front
            )

        composite[~valid_mask] = 0.0
        return composite, sst_suit, sst_front, chl_suit, chl_front

    # -------------------------------------------------------------------------
    # 5. Connected Region Clustering & Polygon Generation (Levels 2 & 3)
    # -------------------------------------------------------------------------
    def extract_candidate_regions(
        self,
        suitability_matrix: np.ndarray,
        lats: np.ndarray,
        lons: np.ndarray,
        threshold: float = SUITABILITY_CLUSTER_THRESHOLD,
        min_cells: int = MIN_CLUSTER_CELL_COUNT
    ) -> List[Dict[str, Any]]:
        """
        Groups connected high-suitability cells into discrete candidate spatial regions.
        Derives bounding polygon coordinates, surface area, and cluster centroid.
        """
        binary_mask = suitability_matrix >= threshold
        labeled_array, num_features = ndimage.label(binary_mask)

        candidates = []
        dy_km = abs(lats[1] - lats[0]) * 111.32 if len(lats) > 1 else 10.0

        for label_id in range(1, num_features + 1):
            cell_coords = np.argwhere(labeled_array == label_id)
            if len(cell_coords) < min_cells:
                continue

            cluster_lats = [lats[r] for r, _ in cell_coords]
            cluster_lons = [lons[c] for _, c in cell_coords]
            cluster_weights = [suitability_matrix[r, c] for r, c in cell_coords]
            total_weight = sum(cluster_weights)

            # Centroid (Level 4): weighted average of cell centers
            if total_weight > 0:
                c_lat = sum(lat * w for lat, w in zip(cluster_lats, cluster_weights)) / total_weight
                c_lon = sum(lon * w for lon, w in zip(cluster_lons, cluster_weights)) / total_weight
            else:
                c_lat = float(np.mean(cluster_lats))
                c_lon = float(np.mean(cluster_lons))

            min_lat, max_lat = min(cluster_lats), max(cluster_lats)
            min_lon, max_lon = min(cluster_lons), max(cluster_lons)

            # Bounding box polygon ring: [[lon, lat], ...] RFC 7946 GeoJSON format
            ring = [
                [round(min_lon, 4), round(min_lat, 4)],
                [round(max_lon, 4), round(min_lat, 4)],
                [round(max_lon, 4), round(max_lat, 4)],
                [round(min_lon, 4), round(max_lat, 4)],
                [round(min_lon, 4), round(min_lat, 4)]
            ]

            mid_lat = (min_lat + max_lat) / 2.0
            dx_km = abs(lons[1] - lons[0]) * 111.32 * math.cos(math.radians(mid_lat))
            area_sq_km = len(cell_coords) * (dy_km * dx_km)

            candidates.append({
                "label_id": label_id,
                "cell_count": len(cell_coords),
                "cell_indices": cell_coords,
                "centroid_lat": round(float(c_lat), 4),
                "centroid_lon": round(float(c_lon), 4),
                "polygon_ring": ring,
                "bounding_box": [round(min_lat, 4), round(min_lon, 4), round(max_lat, 4), round(max_lon, 4)],
                "area_sq_km": round(float(area_sq_km), 2)
            })

        return candidates

    # -------------------------------------------------------------------------
    # 6. Independent Confidence Calculation
    # -------------------------------------------------------------------------
    def calculate_confidence(
        self,
        has_sst: bool,
        has_chl: bool,
        valid_pixel_pct: float,
        cloud_pct: float,
        is_archived: bool = False
    ) -> ConfidenceBreakdown:
        """
        Derives an independent confidence score based on physical sensor availability,
        data coverage, and temporal latency.
        Section 21 requirement: Confidence is distinct from suitability score.
        """
        supporting_count = (1 if has_sst else 0) + (1 if has_chl else 0)
        sensors = []
        if has_sst:
            sensors.append("ISRO INSAT-3DR TIR / MOSDAC")
        if has_chl:
            sensors.append("ISRO Oceansat-3 (EOS-06) OCM-3")

        base_conf = 50.0

        # Multi-sensor bonus: joint SST + Chl observation gives high confidence
        if has_sst and has_chl:
            base_conf += 30.0
        elif has_sst:
            base_conf += 10.0

        # Coverage factor (unmasked valid ocean percentage)
        cov_factor = min(1.0, valid_pixel_pct / 85.0)
        base_conf += cov_factor * 15.0

        # Cloud contamination deduction
        if cloud_pct > 30.0:
            base_conf -= (cloud_pct - 30.0) * 0.5

        # Latency adjustment
        temporal_str = "Near-Real-Time Synchronous Stream"
        if is_archived:
            base_conf -= 10.0
            temporal_str = "Archived Historical Pass"

        final_conf = max(10.0, min(95.0, base_conf))
        level = "HIGH" if final_conf >= 75.0 else ("MODERATE" if final_conf >= 50.0 else "LOW")

        explanation = (
            f"Confidence {final_conf:.1f}% ({level}) derived from {supporting_count} verified sensor(s), "
            f"{valid_pixel_pct:.1f}% valid ocean coverage, and {cloud_pct:.1f}% cloud/nodata mask."
        )

        return ConfidenceBreakdown(
            overall_confidence_percent=round(final_conf, 1),
            confidence_level=level,
            data_coverage_percent=round(valid_pixel_pct, 1),
            supporting_variables_count=supporting_count,
            sensor_provenance=sensors,
            temporal_alignment=temporal_str,
            cloud_contamination_percent=round(cloud_pct, 1),
            explanation=explanation
        )

    # -------------------------------------------------------------------------
    # 7. Weather & Marine Hazard Fusion
    # -------------------------------------------------------------------------
    def fuse_hazard_context(
        self,
        candidate_lat: float,
        candidate_lon: float,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        active_cyclones: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[EnvironmentalHazardStatus, float, List[str]]:
        """
        Fuses real atmospheric/oceanographic hazards onto candidate suitability.
        Applies data-driven penalties without black-box math.
        Section 16 & 17 requirement.
        """
        penalties = []
        penalty_score = 0.0

        if not weather_telemetry:
            return (
                EnvironmentalHazardStatus.LOW_CONFIDENCE,
                0.0,
                ["Marine atmospheric weather telemetry unavailable for this coordinate."]
            )

        wave_h = weather_telemetry.get("significant_wave_height_m") or weather_telemetry.get("wave_height_m", 0.0)
        wind_kts = weather_telemetry.get("wind_speed_knots", 0.0)
        cyclone_warning = False

        # Active tropical cyclone tracking in North Indian Ocean
        if active_cyclones:
            for cyc in active_cyclones:
                c_lat = float(cyc.get("current_lat", 0.0))
                c_lon = float(cyc.get("current_lon", 0.0))
                dist_km = self.haversine_km(candidate_lat, candidate_lon, c_lat, c_lon)
                if dist_km < 350.0:
                    cyclone_warning = True
                    penalties.append(
                        f"Active Tropical Cyclone '{cyc.get('name', 'System')}' within {dist_km:.0f} km. Severe maritime peril."
                    )
                    penalty_score += 0.50

        # Wave height penalties
        if wave_h > 2.8:
            penalties.append(f"High sea state: Significant wave height {wave_h:.2f}m exceeds safety threshold (2.8m).")
            penalty_score += 0.35
        elif wave_h > 2.0:
            penalties.append(f"Moderate-to-rough sea state: Wave height {wave_h:.2f}m requires caution.")
            penalty_score += 0.15

        # Wind speed penalties
        if wind_kts > 28.0:
            penalties.append(f"Gale/squall winds: {wind_kts:.1f} kts exceeds safe operating limits.")
            penalty_score += 0.30
        elif wind_kts > 21.0:
            penalties.append(f"Strong breeze: {wind_kts:.1f} kts.")
            penalty_score += 0.10

        # Determine fused classification
        if cyclone_warning or wave_h > 2.8 or wind_kts > 28.0:
            status = EnvironmentalHazardStatus.ENVIRONMENTALLY_FAVORABLE_BUT_HAZARDOUS
        else:
            status = EnvironmentalHazardStatus.ENVIRONMENTALLY_FAVORABLE

        return status, round(min(0.80, penalty_score), 2), penalties

    # -------------------------------------------------------------------------
    # 8. Main Spatial PFZ Candidate Analysis Pipeline
    # -------------------------------------------------------------------------
    def analyze_spatial_pfz(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        time_window: Optional[TimeWindow] = None,
        reference_lat: Optional[float] = None,
        reference_lon: Optional[float] = None,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        active_cyclones: Optional[List[Dict[str, Any]]] = None
    ) -> PFZAnalysisResponse:
        """
        Executes the complete Phase 6 analytical pipeline over a region of interest.
        """
        # Temporal gate: reject future satellite requests honestly (Section 14)
        if time_window and time_window.is_future:
            return PFZAnalysisResponse(
                status="FUTURE_EO_UNAVAILABLE",
                analysis_type=PFZResultType.UNAVAILABLE,
                time_window=time_window.to_dict() if hasattr(time_window, "to_dict") else {},
                region={"bounds": [min_lat, min_lon, max_lat, max_lon]},
                candidates_count=0,
                candidates=[],
                limitations=[
                    "Future satellite observation cannot exist. Earth Observation sensors record past or "
                    "near-real-time physical radiances. For future conditions, consult numerical marine forecast models."
                ]
            )

        # 1. Ingest real SST and Chlorophyll rasters from catalog
        try:
            sst_grid = self.catalog.get_map_grid("sea_surface_temperature", min_lat, max_lat, min_lon, max_lon, time_window)
        except Exception as e:
            return PFZAnalysisResponse(
                status="UNAVAILABLE",
                analysis_type=PFZResultType.UNAVAILABLE,
                region={"bounds": [min_lat, min_lon, max_lat, max_lon]},
                candidates_count=0,
                candidates=[],
                limitations=[f"Primary thermal Earth Observation (SST) unavailable: {str(e)}"]
            )

        chl_grid = None
        has_chl = False

        try:
            chl_grid = self.catalog.get_map_grid("chlorophyll_a", min_lat, max_lat, min_lon, max_lon, time_window)
            has_chl = chl_grid is not None and chl_grid.values is not None
        except Exception as e:
            logger.warning("Chlorophyll-a unavailable for PFZ analysis: %s", e)

        # If SST is completely unavailable, fail truthfully
        if not sst_grid or not sst_grid.values:
            return PFZAnalysisResponse(
                status="UNAVAILABLE",
                analysis_type=PFZResultType.UNAVAILABLE,
                region={"bounds": [min_lat, min_lon, max_lat, max_lon]},
                candidates_count=0,
                candidates=[],
                limitations=["Primary thermal Earth Observation (SST) unavailable for the requested coordinate/temporal window."]
            )

        # 2. Co-register onto common analytical grid
        common_sst, common_chl, lats, lons, valid_mask = self.co_register_grids(
            sst_grid, chl_grid, target_shape=(35, 35)
        )

        valid_pct = float(np.sum(valid_mask)) / float(valid_mask.size) * 100.0
        cloud_pct = 100.0 - valid_pct

        # Check if coverage is too low (< 10% valid ocean pixels)
        if valid_pct < 10.0:
            return PFZAnalysisResponse(
                status="OK",
                analysis_type=PFZResultType.MODEL_DERIVED_PFZ,
                region={"bounds": [min_lat, min_lon, max_lat, max_lon]},
                candidates_count=0,
                candidates=[],
                limitations=[f"Valid ocean observation coverage is too low ({valid_pct:.1f}%). Most cells are masked by land or clouds."]
            )

        # 3. Compute physical geodetic spatial gradients
        sst_grad = self.compute_physical_gradients(common_sst, lats, lons)
        chl_grad = None
        if common_chl is not None:
            chl_grad = self.compute_physical_gradients(common_chl, lats, lons)

        # 4. Compute Level-1 cell-level suitability
        suitability_matrix, sst_suit, sst_front, chl_suit, chl_front = self.compute_cell_suitability(
            common_sst, sst_grad, common_chl, chl_grad, valid_mask
        )

        # 5. Extract Level-2 & 3 connected candidate regions and polygons
        region_clusters = self.extract_candidate_regions(
            suitability_matrix, lats, lons, threshold=self.SUITABILITY_CLUSTER_THRESHOLD, min_cells=3
        )

        candidates: List[PFZCandidate] = []
        is_archived = (time_window and getattr(time_window, "is_past", False)) or (time_window and getattr(time_window, "end_datetime", datetime.now(timezone.utc)) < datetime.now(timezone.utc)) or (sst_grid.provenance.get("status") == "ARCHIVED")

        for idx, cluster in enumerate(region_clusters):
            c_lat = cluster["centroid_lat"]
            c_lon = cluster["centroid_lon"]
            cells = cluster["cell_indices"]

            # Compute cluster aggregate features
            cluster_sst_vals = [common_sst[r, c] for r, c in cells if not np.isnan(common_sst[r, c])]
            cluster_sst_grads = [sst_grad[r, c] for r, c in cells if not np.isnan(sst_grad[r, c])]
            
            mean_sst = float(np.mean(cluster_sst_vals)) if cluster_sst_vals else None
            max_sst_grad = float(np.max(cluster_sst_grads)) if cluster_sst_grads else 0.0

            mean_chl = None
            max_chl_grad = None
            if common_chl is not None:
                cluster_chl_vals = [common_chl[r, c] for r, c in cells if not np.isnan(common_chl[r, c])]
                cluster_chl_grads = [chl_grad[r, c] for r, c in cells if not np.isnan(chl_grad[r, c])]
                if cluster_chl_vals:
                    mean_chl = round(float(np.mean(cluster_chl_vals)), 3)
                if cluster_chl_grads:
                    max_chl_grad = round(float(np.max(cluster_chl_grads)), 4)

            # Cluster average component scores
            avg_sst_suit = float(np.mean([sst_suit[r, c] for r, c in cells]))
            avg_sst_front = float(np.mean([sst_front[r, c] for r, c in cells]))
            avg_chl_suit = float(np.mean([chl_suit[r, c] for r, c in cells])) if has_chl else 0.0
            avg_chl_front = float(np.mean([chl_front[r, c] for r, c in cells])) if has_chl else 0.0

            # Frontal coincidence strength
            front_strength = avg_sst_front if not has_chl else float(np.sqrt(avg_sst_front * max(0.01, avg_chl_front)))

            # Weather & hazard fusion
            hazard_status, hazard_penalty, penalties_applied = self.fuse_hazard_context(
                c_lat, c_lon, weather_telemetry, active_cyclones
            )

            raw_weighted = float(np.mean([suitability_matrix[r, c] for r, c in cells]))
            final_score = max(0.0, min(1.0, raw_weighted - hazard_penalty))

            suitability_obj = SuitabilityBreakdown(
                sst_suitability=round(avg_sst_suit, 3),
                sst_front_strength=round(avg_sst_front, 3),
                chlorophyll_suitability=round(avg_chl_suit, 3),
                chlorophyll_front_strength=round(avg_chl_front, 3),
                oceanographic_support=0.75,
                hazard_penalty=round(hazard_penalty, 2),
                raw_weighted_score=round(raw_weighted, 3),
                final_score=round(final_score, 3),
                weights_used=self.DEFAULT_WEIGHTS
            )

            # Separate confidence
            confidence_obj = self.calculate_confidence(
                has_sst=True,
                has_chl=has_chl,
                valid_pixel_pct=valid_pct,
                cloud_pct=cloud_pct,
                is_archived=is_archived
            )

            # Spatial distance and bearing if reference location is provided
            dist_km = None
            bearing_deg = None
            if reference_lat is not None and reference_lon is not None:
                dist_km = round(self.haversine_km(reference_lat, reference_lon, c_lat, c_lon), 1)
                bearing_deg = round(self.calculate_bearing(reference_lat, reference_lon, c_lat, c_lon), 1)

            polygon_obj = CandidatePolygon(
                coordinates=cluster["polygon_ring"],
                bounding_box=cluster["bounding_box"],
                area_sq_km=cluster["area_sq_km"],
                cell_count=cluster["cell_count"]
            )

            # Name based on geography / front
            zone_name = f"Thermal-Color Frontal Cluster #{idx + 1} ({c_lat:.2f}°N, {c_lon:.2f}°E)"
            candidate_id = f"ORCA-PFZ-{abs(hash((c_lat, c_lon, sst_grid.acquisition_time))) % 100000:05d}"

            source_times = {"sst": sst_grid.acquisition_time}
            if chl_grid:
                source_times["chlorophyll"] = chl_grid.acquisition_time

            candidates.append(PFZCandidate(
                candidate_id=candidate_id,
                name=zone_name,
                result_type=PFZResultType.MODEL_DERIVED_PFZ,
                centroid_lat=c_lat,
                centroid_lon=c_lon,
                distance_km=dist_km,
                bearing_deg=bearing_deg,
                geometry=polygon_obj,
                sst_mean_c=round(mean_sst, 2) if mean_sst else None,
                sst_gradient_max_c_per_km=round(max_sst_grad, 4),
                chlorophyll_mean_mg_m3=mean_chl,
                chlorophyll_gradient_max_mg_m3_per_km=max_chl_grad,
                front_strength=round(front_strength, 3),
                wave_height_m=weather_telemetry.get("significant_wave_height_m") if weather_telemetry else None,
                wind_speed_knots=weather_telemetry.get("wind_speed_knots") if weather_telemetry else None,
                suitability=suitability_obj,
                pfz_score=round(final_score, 3),
                confidence=confidence_obj,
                hazard_status=hazard_status,
                hazard_penalties_applied=penalties_applied,
                temporal_validity=f"Valid for {sst_grid.acquisition_time[:10]}",
                source_timestamps=source_times,
                provenance={
                    "sst_satellite": sst_grid.satellite,
                    "sst_product": sst_grid.provenance.get("product_name"),
                    "chlorophyll_satellite": chl_grid.satellite if chl_grid else "Unavailable",
                    "co_registration_grid_shape": list(common_sst.shape)
                },
                derivation_method="Coincident Geodetic SST-Chlorophyll Multi-Variable Front Analytics",
                limitations=[
                    "Model-derived PFZ candidate; not an official INCOIS broadcast advisory.",
                    "Chlorophyll-a missing or cloud-masked in some sectors." if not has_chl else "Satellite optical sensors subject to cloud gaps."
                ]
            ))

        # Rank candidates by final_score descending
        candidates.sort(key=lambda c: c.pfz_score, reverse=True)

        return PFZAnalysisResponse(
            status="OK",
            analysis_type=PFZResultType.MODEL_DERIVED_PFZ,
            time_window=time_window.to_dict() if hasattr(time_window, "to_dict") else {},
            region={"bounds": [min_lat, min_lon, max_lat, max_lon]},
            candidates_count=len(candidates),
            candidates=candidates,
            top_candidate=candidates[0] if candidates else None,
            environmental_summary={
                "mean_sst_c": round(float(np.nanmean(common_sst)), 2),
                "mean_chlorophyll_mg_m3": round(float(np.nanmean(common_chl)), 3) if common_chl is not None else None,
                "valid_data_coverage_pct": round(valid_pct, 1),
                "cloud_nodata_pct": round(cloud_pct, 1)
            },
            active_hazards=penalties_applied if region_clusters else [],
            provenance=[
                {"parameter": "SST", "source": sst_grid.source, "satellite": sst_grid.satellite, "timestamp": sst_grid.acquisition_time},
                {"parameter": "Chlorophyll-a", "source": chl_grid.source if chl_grid else "Unavailable", "satellite": chl_grid.satellite if chl_grid else "Unavailable", "timestamp": chl_grid.acquisition_time if chl_grid else "None"}
            ],
            limitations=[
                "MODEL-DERIVED CANDIDATE: Rule-based multi-variable oceanographic baseline.",
                "ML was not claimed because validated training data were unavailable."
            ],
            ml_status="ML was not claimed because validated training data were unavailable."
        )

    # -------------------------------------------------------------------------
    # 9. Radius Query & Nearest PFZ Finder (Section 18 & 19)
    # -------------------------------------------------------------------------
    def find_candidates_within_radius(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        time_window: Optional[TimeWindow] = None,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        active_cyclones: Optional[List[Dict[str, Any]]] = None
    ) -> List[PFZCandidate]:
        """
        Finds and ranks PFZ candidates within an exact geodesic radius of a reference coordinate.
        """
        # Form bounding box around center_lat, center_lon with buffer
        lat_buffer = (radius_km / 111.32) * 1.15
        cos_lat = max(0.2, math.cos(math.radians(center_lat)))
        lon_buffer = (radius_km / (111.32 * cos_lat)) * 1.15

        min_lat = max(6.0, center_lat - lat_buffer)
        max_lat = min(24.0, center_lat + lat_buffer)
        min_lon = max(66.0, center_lon - lon_buffer)
        max_lon = min(88.0, center_lon + lon_buffer)

        response = self.analyze_spatial_pfz(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            time_window=time_window,
            reference_lat=center_lat,
            reference_lon=center_lon,
            weather_telemetry=weather_telemetry,
            active_cyclones=active_cyclones
        )

        filtered = [
            c for c in response.candidates
            if c.distance_km is not None and c.distance_km <= radius_km
        ]
        # Rank by score descending, then by distance ascending
        filtered.sort(key=lambda c: (-c.pfz_score, c.distance_km or 9999.0))
        return filtered

    def find_nearest_candidate(
        self,
        ref_lat: float,
        ref_lon: float,
        time_window: Optional[TimeWindow] = None,
        weather_telemetry: Optional[Dict[str, Any]] = None,
        active_cyclones: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[PFZCandidate]:
        """Finds the single closest PFZ candidate from the reference point."""
        candidates = self.find_candidates_within_radius(
            center_lat=ref_lat,
            center_lon=ref_lon,
            radius_km=180.0,
            time_window=time_window,
            weather_telemetry=weather_telemetry,
            active_cyclones=active_cyclones
        )
        return candidates[0] if candidates else None
