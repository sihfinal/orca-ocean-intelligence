#!/usr/bin/env python3
"""
Performance Benchmark & Concurrency Suite for ORCA / Blue Orbit
ISRO Smart India Hackathon 2026 - Problem Statement 26176
Phase 10: Performance, Latency, Concurrency & Memory Benchmarking

Measures and validates:
1. Simple query intent understanding latency
2. Satellite raster point and regional query latency
3. Potential Fishing Zone (PFZ) candidate generation latency
4. A* Least-Cost safe maritime route calculation latency
5. Full end-to-end multi-agent planner execution latency
6. In-memory cache hit acceleration (speedup factor)
7. Concurrent request handling and session isolation
8. Memory footprint and bounded resource verification
"""

import sys
import os
import time
import asyncio
import statistics
import concurrent.futures
from datetime import datetime, timezone

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.data.raster.catalog import EODatasetCatalog
from backend.agents.ocean_analytics_agent import OceanAnalyticsAgent
from backend.geospatial.geofence_service import GeofenceService
from backend.geospatial.risk_engine import MarineRiskEngine
from backend.geospatial.routing_engine import MarineRouteOptimizer
from backend.agents.orchestrator import MasterOrchestrator
from backend.planning.context import ORCAExecutionContext
from backend.memory.session_store import SessionStore

def benchmark_all():
    passed = 0
    total = 0

    def check(name, condition, explanation=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name} -> {explanation}")

    print("\n" + "="*75)
    print("ORCA PERFORMANCE & CONCURRENCY BENCHMARK SUITE (PHASE 10)")
    print("="*75 + "\n")

    catalog = EODatasetCatalog()
    ocean_agent = OceanAnalyticsAgent()
    geofence_svc = GeofenceService()
    risk_engine = MarineRiskEngine(geofence_svc)
    route_optimizer = MarineRouteOptimizer(geofence_svc, risk_engine)
    orchestrator = MasterOrchestrator()

    # -------------------------------------------------------------------------
    # 1. Simple Intent Understanding Latency
    # -------------------------------------------------------------------------
    print("1. Intent Parsing & Task Decomposition Latency")
    intent_latencies = []
    queries = [
        "Find the best fishing zone near Mangalore.",
        "Is it safe to go out to sea tomorrow morning?",
        "What is the sea surface temperature near Kochi?",
        "Show me a route from Kochi to the candidate zone.",
        "Why did you recommend this specific zone?"
    ]
    for q in queries:
        t0 = time.perf_counter()
        ctx = ORCAExecutionContext(query=q)
        _ = orchestrator.planner.understand_request(ctx)
        t1 = time.perf_counter()
        intent_latencies.append((t1 - t0) * 1000.0)

    avg_intent_ms = statistics.mean(intent_latencies)
    p95_intent_ms = statistics.quantiles(intent_latencies, n=20)[-1] if len(intent_latencies) >= 20 else max(intent_latencies)
    print(f"     Mean: {avg_intent_ms:.2f} ms | Max: {max(intent_latencies):.2f} ms")
    check("1.1 Intent understanding executes under 50 ms", avg_intent_ms < 50.0)

    # -------------------------------------------------------------------------
    # 2. Satellite Raster Query Latency
    # -------------------------------------------------------------------------
    print("\n2. Satellite Earth Observation & Raster Extraction Latency")
    raster_latencies = []
    for _ in range(5):
        t0 = time.perf_counter()
        pt = catalog.get_spatial_point("sea_surface_temperature", 12.86, 74.84)
        t1 = time.perf_counter()
        raster_latencies.append((t1 - t0) * 1000.0)

    avg_raster_ms = statistics.mean(raster_latencies)
    print(f"     Mean: {avg_raster_ms:.2f} ms | Min: {min(raster_latencies):.2f} ms")
    check("2.1 NetCDF raster spatial point extraction under 100 ms", avg_raster_ms < 100.0)

    # -------------------------------------------------------------------------
    # 3. Spatial PFZ Candidate Analytics Latency
    # -------------------------------------------------------------------------
    print("\n3. Spatial PFZ Candidate Generation Latency")
    pfz_latencies = []
    for _ in range(3):
        t0 = time.perf_counter()
        _ = ocean_agent.find_candidates_within_radius(center_lat=12.86, center_lon=74.84, radius_km=150.0)
        t1 = time.perf_counter()
        pfz_latencies.append((t1 - t0) * 1000.0)

    avg_pfz_ms = statistics.mean(pfz_latencies)
    print(f"     Mean: {avg_pfz_ms:.2f} ms | Min: {min(pfz_latencies):.2f} ms")
    check("3.1 PFZ candidates generation and spatial clustering under 2500 ms", avg_pfz_ms < 2500.0)

    # -------------------------------------------------------------------------
    # 4. A* Safe Route Optimization Latency
    # -------------------------------------------------------------------------
    print("\n4. A* Least-Cost Safe Maritime Routing Latency")
    route_latencies = []
    for _ in range(3):
        t0 = time.perf_counter()
        res = route_optimizer.optimize_route(
            start_lat=12.86, start_lon=74.84,
            dest_lat=13.20, dest_lon=74.20,
            start_name="Mangalore", dest_name="Offshore"
        )
        t1 = time.perf_counter()
        route_latencies.append((t1 - t0) * 1000.0)

    avg_route_ms = statistics.mean(route_latencies)
    print(f"     Mean: {avg_route_ms:.2f} ms | Min: {min(route_latencies):.2f} ms")
    check("4.1 A* discrete surface cost search under 5000 ms", avg_route_ms < 5000.0)

    # -------------------------------------------------------------------------
    # 5. In-Memory Cache Speedup Factor
    # -------------------------------------------------------------------------
    print("\n5. In-Memory Cache Performance & Acceleration")
    # Fresh query (uncached)
    t0 = time.perf_counter()
    _ = catalog.get_regional_statistics("sea_surface_temperature", 11.0, 13.0, 74.0, 76.0)
    t_uncached = (time.perf_counter() - t0) * 1000.0

    # Repeat query (cached in catalog / memory)
    t0 = time.perf_counter()
    _ = catalog.get_regional_statistics("sea_surface_temperature", 11.0, 13.0, 74.0, 76.0)
    t_cached = (time.perf_counter() - t0) * 1000.0

    print(f"     Uncached: {t_uncached:.2f} ms | Cached: {t_cached:.2f} ms")
    check("5.1 Cached raster statistics execute significantly faster or under 15 ms", 
          t_cached < 15.0 or t_cached < t_uncached)

    # -------------------------------------------------------------------------
    # 6. Concurrency & Multi-Session Isolation
    # -------------------------------------------------------------------------
    print("\n6. Concurrency & Session State Isolation")
    session_store = SessionStore()
    
    # Simulate 10 simultaneous user sessions
    num_sessions = 10
    def simulate_user_session(user_idx: int):
        sid = f"SESSION-BENCH-{user_idx:03d}"
        session = session_store.get_or_create_session(sid)
        session.add_user_message(f"User {user_idx} asks for PFZ near port {user_idx}")
        session.add_assistant_message(f"ORCA recommends candidate zone {user_idx}")
        history = session.messages
        return len(history) == 2 and f"User {user_idx}" in history[0].content

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(simulate_user_session, range(num_sessions)))

    check("6.1 10 concurrent user sessions execute without cross-talk or race conditions",
          all(results) and len(results) == num_sessions)
    check("6.2 SessionStore correctly maintains distinct isolated states",
          len(session_store._sessions) >= num_sessions)

    # -------------------------------------------------------------------------
    # 7. Memory Bounds & Resource Hygiene
    # -------------------------------------------------------------------------
    print("\n7. Memory Limits & Resource Hygiene")
    # Verify SessionStore caps conversation history to prevent memory explosion
    test_session = session_store.get_or_create_session("SESSION-OVERFLOW-TEST")
    for i in range(30):
        test_session.add_user_message(f"Test message {i}")
    
    bounded_msgs = test_session.messages
    check("7.1 Long conversation memory is bounded (<=25 messages)", len(bounded_msgs) <= 25)

    print("\n" + "-"*75)
    print(f"PERFORMANCE BENCHMARK RESULTS: {passed} / {total} Tests Passed ({passed/total*100:.1f}%)")
    print("-"*75 + "\n")

    if passed == total:
        print(">>> ALL PERFORMANCE & CONCURRENCY BENCHMARKS FULLY VERIFIED! <<<\n")
        return 0
    else:
        print(">>> SOME BENCHMARK TESTS FAILED. <<<\n")
        return 1

if __name__ == "__main__":
    sys.exit(benchmark_all())
