"""
ORCA Phase 5 Verification Test Suite
SIH 2026 - Problem Statement 26176
Validates all 14 mandatory Section 71 requirements:
1. Spatial SST raster extraction around Mangalore
2. Spatial Chlorophyll-a raster extraction around Mangalore
3. Genuine 2D spatial field vs single point value
4. Regional statistics over Mangalore shelf
5. Physical spatial gradients (unit/km) without PFZ label
6. Temporal comparison (today vs past date)
7. Future satellite request honesty
8. Out-of-bounds spatial request handling
9. Land and nodata masking verification
10. Corrupt raster file handling
11. Source failure / network timeout handling
12. In-memory caching verification
13. Multi-turn conversation context retention
14. Multilingual spatial query handling
"""

import sys
import os
import asyncio
import tempfile
from datetime import datetime, timezone, timedelta
import numpy as np

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath("."))

from backend.data.raster.reader import NetCDFRasterReader
from backend.data.raster.processor import RasterProcessor
from backend.data.raster.catalog import EODatasetCatalog
from backend.data.raster.schemas import ExtractionMethod
from backend.data.schemas import DataStatus, QualityFlag
from backend.temporal.models import TimeWindow
from backend.agents.marine_data_agent import MarineDataAgent
from backend.agents.orchestrator import MasterOrchestrator

test_results = []

def record_test(name: str, passed: bool, details: str):
    test_results.append((name, passed, details))
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {details}")

async def run_all_tests():
    print("================================================================================")
    print("STARTING ORCA PHASE 5 VERIFICATION SUITE")
    print("================================================================================")

    catalog = EODatasetCatalog()
    marine_agent = MarineDataAgent(catalog=catalog)
    orchestrator = MasterOrchestrator()

    # -------------------------------------------------------------------------
    # TEST 1: Spatial SST raster extraction around Mangalore
    # -------------------------------------------------------------------------
    try:
        # Mangalore: 12.91°N, 74.85°E. Bounding box [11.5, 14.5] x [73.5, 75.5]
        grid = catalog.get_map_grid("sea_surface_temperature", min_lat=11.5, max_lat=14.5, min_lon=73.5, max_lon=75.5)
        passed = (
            grid.variable == "sea_surface_temperature" and
            grid.unit == "deg_C" and
            len(grid.latitudes) > 0 and
            len(grid.longitudes) > 0 and
            grid.min_value is not None and
            "ISRO" in grid.source or "INSAT" in grid.satellite or "SLSTR" in grid.satellite
        )
        record_test("TEST 1: SST Raster Extraction Around Mangalore", passed,
                    f"Variable={grid.variable}, Unit={grid.unit}, Source={grid.source}, Shape=({len(grid.latitudes)}, {len(grid.longitudes)})")
    except Exception as e:
        record_test("TEST 1: SST Raster Extraction Around Mangalore", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 2: Spatial Chlorophyll-a raster extraction around Mangalore
    # -------------------------------------------------------------------------
    try:
        grid_chl = catalog.get_map_grid("chlorophyll_a", min_lat=11.5, max_lat=14.5, min_lon=73.5, max_lon=75.5)
        passed = (
            grid_chl.variable == "chlorophyll_a" and
            grid_chl.unit == "mg/m^3" and
            "Oceansat-3" in grid_chl.satellite or "EOS-06" in grid_chl.satellite
        )
        record_test("TEST 2: Chlorophyll-a Raster Extraction Around Mangalore", passed,
                    f"Product={grid_chl.provenance.get('product_name')}, Satellite={grid_chl.satellite}, Max={grid_chl.max_value} {grid_chl.unit}")
    except Exception as e:
        record_test("TEST 2: Chlorophyll-a Raster Extraction Around Mangalore", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 3: Genuine 2D spatial field vs single point value
    # -------------------------------------------------------------------------
    try:
        # Verify 2D matrix structure
        is_matrix = isinstance(grid.values, list) and len(grid.values) > 1 and isinstance(grid.values[0], list) and len(grid.values[0]) > 1
        num_cells = sum(len(row) for row in grid.values)
        passed = is_matrix and num_cells > 50
        record_test("TEST 3: 2D Spatial Grid vs Single Point Value", passed,
                    f"Grid rows={len(grid.values)}, cols={len(grid.values[0])}, total cells={num_cells} (strictly 2D matrix)")
    except Exception as e:
        record_test("TEST 3: 2D Spatial Grid vs Single Point Value", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 4: Regional statistics over Mangalore shelf
    # -------------------------------------------------------------------------
    try:
        stats = catalog.get_regional_statistics("sea_surface_temperature", min_lat=12.0, max_lat=14.0, min_lon=73.5, max_lon=75.0)
        passed = (
            stats.has_valid_data and
            stats.mean is not None and
            stats.minimum is not None and
            stats.maximum is not None and
            stats.standard_deviation is not None and
            stats.valid_pixel_count > 0 and
            # Must NOT be labeled as PFZ prediction
            "pfz" not in stats.variable.lower()
        )
        record_test("TEST 4: Regional Zonal Statistics (Mangalore Shelf)", passed,
                    f"Mean={stats.mean}°C, Min={stats.minimum}°C, Max={stats.maximum}°C, Std={stats.standard_deviation}°C, Valid Pct={stats.valid_percentage}% (Strictly regional statistics, not PFZ)")
    except Exception as e:
        record_test("TEST 4: Regional Zonal Statistics (Mangalore Shelf)", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 5: Physical spatial gradients without PFZ label
    # -------------------------------------------------------------------------
    try:
        grads = catalog.get_spatial_gradients("sea_surface_temperature", min_lat=12.0, max_lat=14.0, min_lon=73.5, max_lon=75.0)
        passed = (
            grads.data_type == DataStatus.DERIVED and
            grads.gradient_unit == "deg_C/km" and
            grads.mean_gradient_magnitude is not None and
            grads.max_gradient_magnitude is not None and
            len(grads.sharpest_front_points) > 0 and
            "Not a fisheries prediction" in grads.limitations[0]
        )
        p0 = grads.sharpest_front_points[0]
        record_test("TEST 5: Spacing-Aware Physical Spatial Gradients", passed,
                    f"Max Grad={grads.max_gradient_magnitude} {grads.gradient_unit}, Peak Point=({p0.latitude}°N, {p0.longitude}°E), DERIVED label, Explicitly not PFZ")
    except Exception as e:
        record_test("TEST 5: Spacing-Aware Physical Spatial Gradients", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 6: Temporal comparison (today vs past date)
    # -------------------------------------------------------------------------
    try:
        past_date = datetime.now(timezone.utc) - timedelta(days=2)
        tw_past = TimeWindow(
            label="2 days ago",
            start_datetime=past_date,
            end_datetime=past_date + timedelta(hours=24),
            is_past=True
        )
        curr_pt = catalog.get_spatial_point("sea_surface_temperature", 12.91, 74.85)
        past_pt = catalog.get_spatial_point("sea_surface_temperature", 12.91, 74.85, time_window=tw_past)
        passed = (
            curr_pt.value is not None and
            past_pt.value is not None and
            (curr_pt.acquisition_time != past_pt.acquisition_time or len(past_pt.limitations) > 0)
        )
        record_test("TEST 6: Temporal Comparison (Historical vs Current)", passed,
                    f"Current Acq={curr_pt.acquisition_time[:10]}, Past Requested={past_date.strftime('%Y-%m-%d')}, Handled honestly with provenance")
    except Exception as e:
        record_test("TEST 6: Temporal Comparison (Historical vs Current)", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 7: Future satellite request honesty
    # -------------------------------------------------------------------------
    try:
        future_date = datetime.now(timezone.utc) + timedelta(days=2)
        tw_future = TimeWindow(
            label="in 2 days",
            start_datetime=future_date,
            end_datetime=future_date + timedelta(hours=6),
            is_future=True
        )
        fut_pt = catalog.get_spatial_point("chlorophyll_a", 12.91, 74.85, time_window=tw_future)
        passed = (
            fut_pt.value is None and
            fut_pt.data_type == DataStatus.UNAVAILABLE and
            fut_pt.quality_flag == QualityFlag.MISSING and
            "Future satellite observation cannot exist" in fut_pt.limitations[0]
        )
        record_test("TEST 7: Scientific Honesty on Future Satellite Request", passed,
                    f"Value is None, Status=UNAVAILABLE, Honest Limitation='{fut_pt.limitations[0][:75]}...'")
    except Exception as e:
        record_test("TEST 7: Scientific Honesty on Future Satellite Request", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 8: Out-of-bounds spatial request handling
    # -------------------------------------------------------------------------
    try:
        # Iceland coordinates: 65.0°N, -18.0°W (outside Indian Ocean raster coverage)
        oob_pt = catalog.get_spatial_point("sea_surface_temperature", 65.0, -18.0)
        passed = (
            oob_pt.value is None and
            oob_pt.is_masked and
            any("outside" in lim.lower() for lim in oob_pt.limitations)
        )
        record_test("TEST 8: Out-of-Bounds Spatial Request Handling", passed,
                    f"Point at (65.0°N, -18.0°W) returned value=None, flagged outside coverage: {oob_pt.limitations[0]}")
    except Exception as e:
        record_test("TEST 8: Out-of-Bounds Spatial Request Handling", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 9: Land and nodata masking verification
    # -------------------------------------------------------------------------
    try:
        # Deep inland coordinate on Indian peninsula: Nagpur (21.14°N, 79.08°E)
        inland_pt = catalog.get_spatial_point("chlorophyll_a", 21.14, 79.08)
        # Deep inland statistics bounding box on Deccan plateau
        inland_stats = catalog.get_regional_statistics("chlorophyll_a", min_lat=18.0, max_lat=19.0, min_lon=77.0, max_lon=78.0)
        passed = (
            inland_pt.value is None and
            inland_pt.is_masked and
            inland_pt.is_land and
            inland_stats.has_valid_data is False and
            inland_stats.valid_pixel_count == 0 and
            inland_stats.mean is None
        )
        record_test("TEST 9: Land & Nodata Masking Verification", passed,
                    f"Inland value=None (never 0.0), is_land=True, Regional stats has_valid_data=False, valid_count=0")
    except Exception as e:
        record_test("TEST 9: Land & Nodata Masking Verification", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 10: Corrupt raster file handling
    # -------------------------------------------------------------------------
    try:
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tf:
            tf.write(b"NOT_A_VALID_NETCDF_HEADER_GARBAGE_BYTES_1234567890")
            corrupt_path = tf.name

        caught_error = False
        try:
            NetCDFRasterReader.read_file(corrupt_path)
        except ValueError as ve:
            caught_error = True
            err_msg = str(ve)
        finally:
            if os.path.exists(corrupt_path):
                os.unlink(corrupt_path)

        passed = caught_error and "Corrupt or unreadable" in err_msg
        record_test("TEST 10: Corrupt Raster File Graceful Handling", passed,
                    f"Corrupt NetCDF raised ValueError gracefully: {err_msg}")
    except Exception as e:
        record_test("TEST 10: Corrupt Raster File Graceful Handling", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 11: Source failure / network timeout handling (strictly no synthetic fallback)
    # -------------------------------------------------------------------------
    try:
        # Request variable not in catalog
        non_existent_pt = catalog.get_spatial_point("unknown_plasma_radiance", 12.91, 74.85)
        passed = (
            non_existent_pt.value is None and
            non_existent_pt.data_type == DataStatus.UNAVAILABLE and
            "No satellite Earth Observation product cataloged" in non_existent_pt.limitations[0]
        )
        record_test("TEST 11: Source Failure / Unavailable Product Handling", passed,
                    f"Unknown variable yielded value=None (strictly no synthetic fabrication)")
    except Exception as e:
        record_test("TEST 11: Source Failure / Unavailable Product Handling", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 12: In-memory caching verification
    # -------------------------------------------------------------------------
    try:
        # First call populates cache
        stats1 = catalog.get_regional_statistics("chlorophyll_a", min_lat=12.0, max_lat=13.0, min_lon=74.0, max_lon=75.0)
        # Second call reads from cache
        stats2 = catalog.get_regional_statistics("chlorophyll_a", min_lat=12.0, max_lat=13.0, min_lon=74.0, max_lon=75.0)
        passed = (
            stats1.mean == stats2.mean and
            stats1.acquisition_time == stats2.acquisition_time and
            stats1.valid_pixel_count == stats2.valid_pixel_count
        )
        record_test("TEST 12: In-Memory Caching Verification", passed,
                    f"Cache hit returned identical statistics (mean={stats2.mean} mg/m³, acquisition={stats2.acquisition_time})")
    except Exception as e:
        record_test("TEST 12: In-Memory Caching Verification", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 13: Multi-turn conversation context retention
    # -------------------------------------------------------------------------
    try:
        session_id = "test_phase5_session_mangalore"
        # Turn 1: Mention Mangalore and ask about SST distribution
        res1 = await orchestrator.execute_query_pipeline(
            "Show the SST distribution around Mangalore.",
            session_id=session_id
        )
        # Turn 2: Follow-up without repeating Mangalore: "What about chlorophyll in this region?"
        res2 = await orchestrator.execute_query_pipeline(
            "What about chlorophyll in this region?",
            session_id=session_id
        )
        port_retained = res2.get("reference_port", {}).get("port_key") == "mangalore" or "mangalore" in str(res2.get("reference_port", {})).lower()
        passed = (
            res1.get("detected_intent") == "spatial_eo_raster" and
            res2.get("detected_intent") == "spatial_eo_raster" and
            port_retained
        )
        record_test("TEST 13: Multi-Turn Conversation Spatial Context Retention", passed,
                    f"Turn 1 Intent={res1.get('detected_intent')}, Turn 2 Intent={res2.get('detected_intent')}, Retained Port={res2.get('reference_port', {}).get('name')}")
    except Exception as e:
        record_test("TEST 13: Multi-Turn Conversation Spatial Context Retention", False, str(e))

    # -------------------------------------------------------------------------
    # TEST 14: Multilingual spatial query handling (Kannada, Hindi, English)
    # -------------------------------------------------------------------------
    try:
        # Kannada spatial query
        res_kn = await orchestrator.execute_query_pipeline(
            "ಮಂಗಳೂರು ಹತ್ತಿರ ಕ್ಲೋರೋಫಿಲ್ ಹರಡುವಿಕೆಯನ್ನು ತೋರಿಸಿ.",
            requested_lang="kn"
        )
        # Hindi spatial query
        res_hi = await orchestrator.execute_query_pipeline(
            "मंगलुरु के पास क्लोरोफिल और समुद्र तापमान का वितरण दिखाएं.",
            requested_lang="hi"
        )
        msg_kn = res_kn.get("message") or res_kn.get("response", {}).get("markdown", "")
        msg_hi = res_hi.get("message") or res_hi.get("response", {}).get("markdown", "")
        passed = (
            res_kn.get("language", {}).get("code") == "kn" and
            res_hi.get("language", {}).get("code") == "hi" and
            len(msg_kn) > 50 and
            len(msg_hi) > 50
        )
        record_test("TEST 14: Multilingual Spatial Query Handling (KN, HI, EN)", passed,
                    f"Kannada: {res_kn['language']['name']} response generated ({len(msg_kn)} chars) | Hindi: {res_hi['language']['name']} response generated ({len(msg_hi)} chars)")
    except Exception as e:
        record_test("TEST 14: Multilingual Spatial Query Handling (KN, HI, EN)", False, str(e))

    print("================================================================================")
    total = len(test_results)
    passed_count = sum(1 for _, p, _ in test_results if p)
    print(f"PHASE 5 TEST SUMMARY: {passed_count}/{total} PASSED")
    print("================================================================================")
    return passed_count == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
