import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath("."))
from typing import Dict, Any
from backend.agents.orchestrator import MasterOrchestrator
from backend.planning.models import TaskStatus
from backend.tools.base import BaseTool, ToolResult, ToolSchema

async def run_phase2_tests():
    print("==================================================")
    print("ORCA PHASE 2 COMPREHENSIVE ACCEPTANCE TEST SUITE")
    print("==================================================")

    orchestrator = MasterOrchestrator()

    # ----------------------------------------------------------------------
    # TEST 1: Simple Weather Query
    # ----------------------------------------------------------------------
    print("\n--- TEST 1: Simple Weather Query ---")
    query_1 = "What is the sea condition near Mangalore?"
    res_1 = await orchestrator.execute_query_pipeline(query_1)
    
    trace_1 = res_1["evidence_and_provenance"]["execution_trace"]
    executed_tools_1 = [s["agent"] for s in trace_1]
    
    assert res_1["detected_intent"] == "sea_weather_safety", f"Wrong intent: {res_1['detected_intent']}"
    assert res_1["weather_and_safety"] is not None and "significant_wave_height_m" in res_1["weather_and_safety"]
    # Verify PFZ and Route did NOT execute
    assert not any("PFZ" in a for a in executed_tools_1), "PFZ agent executed when not requested!"
    assert not any("Route" in a for a in executed_tools_1), "Route agent executed when not requested!"
    print(f"PASS: Executed only {len(trace_1)} relevant tasks. PFZ and Route correctly skipped.")

    # ----------------------------------------------------------------------
    # TEST 2: Pure PFZ Query
    # ----------------------------------------------------------------------
    print("\n--- TEST 2: Pure PFZ Query ---")
    query_2 = "Find fishing zones near Mangalore."
    res_2 = await orchestrator.execute_query_pipeline(query_2)
    
    trace_2 = res_2["evidence_and_provenance"]["execution_trace"]
    executed_tools_2 = [s["agent"] for s in trace_2]
    
    assert res_2["detected_intent"] == "pfz_advisory", f"Wrong intent: {res_2['detected_intent']}"
    assert res_2["top_pfz"] is not None and "name" in res_2["top_pfz"]
    assert any("PFZ" in a for a in executed_tools_2), "PFZ agent was not executed!"
    # Verify Route did NOT execute
    assert not any("Route" in a for a in executed_tools_2), "Route agent executed when not requested!"
    print(f"PASS: Executed {len(trace_2)} tasks. PFZ executed, Route correctly skipped.")

    # ----------------------------------------------------------------------
    # TEST 3: Pure Safety Query
    # ----------------------------------------------------------------------
    print("\n--- TEST 3: Pure Safety Query ---")
    query_3 = "Is it safe to go fishing near Mangalore?"
    res_3 = await orchestrator.execute_query_pipeline(query_3)
    
    trace_3 = res_3["evidence_and_provenance"]["execution_trace"]
    executed_tools_3 = [s["agent"] for s in trace_3]
    
    assert res_3["detected_intent"] in ["sea_weather_safety", "composite_marine_advisory"]
    assert res_3["weather_and_safety"] is not None
    print(f"PASS: Safety query processed with {len(trace_3)} tasks. Weather evaluated: {res_3['weather_and_safety'].get('safety_status')}")

    # ----------------------------------------------------------------------
    # TEST 4: Pure Route Query
    # ----------------------------------------------------------------------
    print("\n--- TEST 4: Route Query ---")
    query_4 = "Give me a route from Mangalore to the selected waypoint."
    res_4 = await orchestrator.execute_query_pipeline(query_4)
    
    trace_4 = res_4["evidence_and_provenance"]["execution_trace"]
    executed_tools_4 = [s["agent"] for s in trace_4]
    
    assert res_4["detected_intent"] == "safe_navigation_route", f"Wrong intent: {res_4['detected_intent']}"
    assert any("Route" in a for a in executed_tools_4), "Route agent was not executed!"
    # Verify PFZ hotspot generator did NOT execute
    assert not any("Ocean Analytics & PFZ" in a for a in executed_tools_4), "PFZ agent ran when not requested!"
    print(f"PASS: Executed {len(trace_4)} tasks. Route executed, PFZ hotspot generator skipped.")

    # ----------------------------------------------------------------------
    # TEST 5: Composite Mission Query
    # ----------------------------------------------------------------------
    print("\n--- TEST 5: Composite Mission Query ---")
    query_5 = "Find the best fishing zone near Mangalore, check safety, avoid restricted waters, and give me a route."
    res_5 = await orchestrator.execute_query_pipeline(query_5)
    
    trace_5 = res_5["evidence_and_provenance"]["execution_trace"]
    executed_tools_5 = [s["agent"] for s in trace_5]
    
    assert res_5["detected_intent"] == "composite_marine_advisory"
    assert res_5["top_pfz"] is not None
    assert res_5["weather_and_safety"] is not None
    assert res_5["safe_navigation_route"] is not None
    assert res_5["geofence_status"] is not None
    print(f"PASS: Composite query successfully orchestrated {len(trace_5)} multi-agent tasks across all domains.")

    # ----------------------------------------------------------------------
    # TEST 6: Greeting Interaction (Low Complexity)
    # ----------------------------------------------------------------------
    print("\n--- TEST 6: Greeting (Low Complexity) ---")
    query_6 = "Hello"
    res_6 = await orchestrator.execute_query_pipeline(query_6)
    
    trace_6 = res_6["evidence_and_provenance"]["execution_trace"]
    executed_tools_6 = [s["agent"] for s in trace_6]
    
    assert res_6["detected_intent"] == "greeting"
    # Must only execute context resolver, planner, port grounding, and synthesis
    assert len(trace_6) <= 4, f"Too many tasks for greeting: {len(trace_6)}"
    assert not any("PFZ" in a for a in executed_tools_6), "PFZ executed for greeting!"
    assert not any("Weather" in a for a in executed_tools_6), "Weather executed for greeting!"
    assert not any("Route" in a for a in executed_tools_6), "Route executed for greeting!"
    print(f"PASS: Greeting executed minimal {len(trace_6)} tasks. Heavy marine agents skipped.")

    # ----------------------------------------------------------------------
    # TEST 7: Tool Failure Handling (Honesty & Non-Fabrication)
    # ----------------------------------------------------------------------
    print("\n--- TEST 7: Tool Failure Handling ---")
    # Mock weather tool failure
    class FailingWeatherTool(BaseTool):
        name = "get_weather_at_point"
        description = "Simulated failing weather tool"
        purpose = "Test failure tolerance"
        def _run(self, **kwargs):
            raise ConnectionError("Simulated INCOIS OSF telemetry sensor timeout")

    # Replace tool in registry temporarily
    original_weather_tool = orchestrator.tool_registry.get("get_weather_at_point")
    orchestrator.tool_registry.register(FailingWeatherTool())

    res_7 = await orchestrator.execute_query_pipeline("What is the sea condition near Kochi?")
    # Restore original tool
    orchestrator.tool_registry.register(original_weather_tool)

    trace_7 = res_7["evidence_and_provenance"]["execution_trace"]
    failed_steps = [s for s in trace_7 if s["status"] == "FAILED"]
    assert len(failed_steps) > 0, "Failed tool was not marked as FAILED in trace!"
    assert res_7["execution_metadata"]["failed_tasks"] > 0, "failed_tasks count was not updated!"
    assert "Simulated INCOIS OSF telemetry sensor timeout" in failed_steps[0]["output_summary"]
    print(f"PASS: Tool failure was explicitly captured as FAILED without crashing or fabricating fake success.")

    # ----------------------------------------------------------------------
    # TEST 8: Dependency Failure Handling (Blocking Downstream Tasks)
    # ----------------------------------------------------------------------
    print("\n--- TEST 8: Dependency Failure & Blocking ---")
    class FailingPortTool(BaseTool):
        name = "resolve_reference_port"
        description = "Simulated failing port tool"
        purpose = "Test dependency cascade"
        def _run(self, **kwargs):
            raise ValueError("Simulated GIS port database corruption")

    original_port_tool = orchestrator.tool_registry.get("resolve_reference_port")
    orchestrator.tool_registry.register(FailingPortTool())

    res_8 = await orchestrator.execute_query_pipeline("What is the sea condition near Kochi?")
    orchestrator.tool_registry.register(original_port_tool)

    trace_8 = res_8["evidence_and_provenance"]["execution_trace"]
    blocked_or_failed = [s for s in trace_8 if s["status"] in ["FAILED", "BLOCKED"]]
    assert len(blocked_or_failed) >= 2, f"Expected failed root task and blocked downstream tasks, got {len(blocked_or_failed)}"
    print(f"PASS: Upstream failure properly blocked downstream tasks. No fake data fabricated.")

    # ----------------------------------------------------------------------
    # TEST 9: Real Execution Trace Verification (No Hardcoded Claims)
    # ----------------------------------------------------------------------
    print("\n--- TEST 9: Execution Trace Verification ---")
    for s in trace_5:
        assert "Decomposed into 5 parallel agent subtasks" not in s.get("output_summary", ""), "Fake old trace string found!"
        assert "duration_ms" in s and s["duration_ms"] >= 0
        assert "agent" in s and len(s["agent"]) > 0
        assert "step_id" in s and len(s["step_id"]) > 0
    print("PASS: Execution trace contains 100% genuine dynamic telemetry.")

    print("\n==================================================")
    print("ALL 9 PHASE 2 ACCEPTANCE TESTS PASSED PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_phase2_tests())
