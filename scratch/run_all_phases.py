#!/usr/bin/env python3
"""
ORCA Master Regression & Verification Harness
ISRO Smart India Hackathon 2026 - Problem Statement 26176
Theme: Disaster Management & Blue Economy (ISRO / Dept. of Space)

Executes all 13 project test suites across all phases (1 through 10):
- Phase 1: Security & Hardening
- Phase 2: Dynamic Planner & Tool Execution DAG
- Phase 3: Session Memory & Temporal Reasoning
- Phase 4: Marine & Meteorological Infrastructure
- Phase 5: Satellite Earth Observation & NetCDF Rasters
- Phase 6: PFZ Intelligence & Coincident Front Analytics
- Phase 7: Geofencing, Risk Engine & A* Safe Routing
- Phase 8: Decision Engine, Explainability & Provenance
- Phase 9: Operational UI, Map Layers & GeoJSON Export
- Phase 10: Scientific Validation Framework
- Phase 10: Security Hardening & Prompt Injection Defenses
- Phase 10: Performance & Concurrency Benchmarks
- Platform: Master Microservice Sanity Suite (verify_system.py)
"""

import sys
import os
import subprocess
import time

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SUITES = [
    ("Phase 1: Security & Input Hardening", ["python", "-u", "scratch/test_phase1.py"]),
    ("Phase 2: Dynamic Planner & Execution Graph", ["python", "-u", "scratch/test_phase2.py"]),
    ("Phase 3: Session Memory & Temporal Reasoning", ["python", "-u", "scratch/test_phase3.py"]),
    ("Phase 4: Real Marine & Weather Feeds", ["python", "-u", "scratch/test_phase4.py"]),
    ("Phase 5: Satellite EO & NetCDF Rasters", ["python", "-u", "scratch/test_phase5.py"]),
    ("Phase 6: PFZ Intelligence & Front Analytics", ["python", "-u", "scratch/test_phase6.py"]),
    ("Phase 7: Geofencing & A* Route Optimization", ["python", "-u", "scratch/test_phase7.py"]),
    ("Phase 8: Decision Engine & Provenance DAG", ["python", "-u", "scratch/test_phase8.py"]),
    ("Phase 9: UI, Layers & GeoJSON Export", ["python", "-u", "scratch/test_phase9.py"]),
    ("Phase 10: Scientific Validation Framework", ["python", "-u", "scratch/validate_science.py"]),
    ("Phase 10: Security & Prompt-Injection Audit", ["python", "-u", "scratch/test_security_hardening.py"]),
    ("Phase 10: Performance & Concurrency Benchmarks", ["python", "-u", "scratch/benchmark_performance.py"]),
    ("Platform: System Sanity Verification", ["python", "-u", "verify_system.py"]),
]

def main():
    print("\n" + "="*80)
    print("ORCA SIH 2026 — MASTER ALL-PHASES VERIFICATION RUNNER")
    print("="*80 + "\n")

    results = []
    total_start = time.perf_counter()

    for idx, (name, cmd) in enumerate(SUITES, 1):
        print(f"[{idx:02d}/{len(SUITES):02d}] RUNNING: {name} ...")
        t0 = time.perf_counter()
        
        proc = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        elapsed = time.perf_counter() - t0
        passed = (proc.returncode == 0)
        results.append((name, passed, elapsed, proc.stdout))
        
        status_str = "PASS" if passed else "FAIL"
        print(f"       -> {status_str} ({elapsed:.2f}s)")
        if not passed:
            print("\n--- Output on failure ---")
            print(proc.stdout[-800:])
            print("-------------------------\n")

    total_elapsed = time.perf_counter() - total_start
    total_suites = len(results)
    passed_suites = sum(1 for _, p, _, _ in results if p)

    print("\n" + "="*80)
    print("MASTER VERIFICATION SUMMARY")
    print("="*80)
    for name, p, el, _ in results:
        sym = "PASS" if p else "FAIL"
        print(f"  [{sym}] {name:<45} ({el:.2f}s)")
    print("-"*80)
    print(f"TOTAL: {passed_suites} / {total_suites} Suites Passed ({passed_suites/total_suites*100:.1f}%) in {total_elapsed:.1f}s")
    print("="*80 + "\n")

    if passed_suites == total_suites:
        print(">>> ALL 13 TEST SUITES PASSED! ZERO REGRESSIONS DETECTED! <<<\n")
        return 0
    else:
        print(">>> SOME TEST SUITES FAILED! <<<\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
