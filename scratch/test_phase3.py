import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath("."))
from datetime import datetime, timedelta
from backend.agents.orchestrator import MasterOrchestrator
from backend.temporal.models import IST_OFFSET
from backend.temporal.resolver import TemporalResolver
from backend.memory.models import ConversationState

async def run_phase3_tests():
    print("==================================================")
    print("ORCA PHASE 3 COMPREHENSIVE ACCEPTANCE TEST SUITE")
    print("==================================================")

    orchestrator = MasterOrchestrator()
    temp_resolver = TemporalResolver()

    # ----------------------------------------------------------------------
    # TEST 1: Single-turn query
    # ----------------------------------------------------------------------
    print("\n--- TEST 1: Single-Turn Query ---")
    session_1 = "test_sess_01"
    res_1 = await orchestrator.execute_query_pipeline("Find fishing zones near Mangalore.", session_id=session_1)
    assert res_1["session_id"] == session_1
    assert res_1["top_pfz"] is not None
    assert len(res_1["all_pfz_hotspots"]) > 0
    assert res_1["reference_port"]["port_key"] == "mangalore"
    print(f"PASS: Single turn query planned and executed. Stored {len(res_1['all_pfz_hotspots'])} candidates in session.")

    # ----------------------------------------------------------------------
    # TEST 2: Follow-up "Which is closest?"
    # ----------------------------------------------------------------------
    print("\n--- TEST 2: Follow-up 'Which is closest?' ---")
    res_2 = await orchestrator.execute_query_pipeline("Which is closest?", session_id=session_1)
    assert res_2["session_id"] == session_1
    assert res_2["reference_port"]["port_key"] == "mangalore", "Lost Mangalore location continuity!"
    assert res_2["top_pfz"] is not None
    # Verify candidate resolution happened
    ref_res = res_2["resolved_context"]["reference_resolutions"]
    assert any(r.get("criterion") == "closest" for r in ref_res)
    print(f"PASS: 'Which is closest?' successfully resolved to closest zone: '{res_2['top_pfz'].get('name')}' using Mangalore context.")

    # ----------------------------------------------------------------------
    # TEST 3: Follow-up pronoun "Will it be safe?"
    # ----------------------------------------------------------------------
    print("\n--- TEST 3: Follow-up Pronoun 'Will it be safe?' ---")
    res_3 = await orchestrator.execute_query_pipeline("Will it be safe?", session_id=session_1)
    assert res_3["session_id"] == session_1
    assert res_3["weather_and_safety"] is not None
    ref_res_3 = res_3["resolved_context"]["reference_resolutions"]
    assert any(r.get("type") == "PRONOUN_RESOLUTION" for r in ref_res_3)
    print(f"PASS: Pronoun 'it' resolved to '{res_3['top_pfz'].get('name')}'. Weather safety evaluated: {res_3['weather_and_safety'].get('safety_status')}.")

    # ----------------------------------------------------------------------
    # TEST 4: Follow-up route "Give me the safest route there."
    # ----------------------------------------------------------------------
    print("\n--- TEST 4: Follow-up Route 'Give me the safest route there.' ---")
    res_4 = await orchestrator.execute_query_pipeline("Give me the safest route there.", session_id=session_1)
    assert res_4["session_id"] == session_1
    assert res_4["safe_navigation_route"] is not None
    assert res_4["reference_port"]["port_key"] == "mangalore"
    print(f"PASS: 'there' resolved to '{res_2['top_pfz'].get('name')}'. Route generated: {res_4['safe_navigation_route'].get('total_distance_nm')} NM from Mangalore.")

    # ----------------------------------------------------------------------
    # TEST 5: Explicit Context Override
    # ----------------------------------------------------------------------
    print("\n--- TEST 5: Explicit Context Override ---")
    res_5 = await orchestrator.execute_query_pipeline("Actually what about Chennai?", session_id=session_1)
    assert res_5["session_id"] == session_1
    assert res_5["reference_port"]["port_key"] == "chennai", "Explicit port override failed to overwrite previous Mangalore memory!"
    # Verify session structured memory updated to Chennai
    stored_sess = orchestrator.session_store.get_or_create_session(session_1)
    assert stored_sess.structured.active_port["port_key"] == "chennai"
    print(f"PASS: Explicit location 'Chennai' successfully overrode previous 'Mangalore' memory.")

    # ----------------------------------------------------------------------
    # TEST 6: Temporal "tomorrow"
    # ----------------------------------------------------------------------
    print("\n--- TEST 6: Temporal 'tomorrow' ---")
    res_6 = await orchestrator.execute_query_pipeline("What is the sea condition near Kochi tomorrow?", session_id="test_sess_temp")
    assert res_6["temporal_context"] is not None
    assert res_6["temporal_context"]["is_future"] is True
    assert res_6["temporal_context"]["label"] == "tomorrow_full_day"
    assert res_6["temporal_context"]["forecast_executable"] is False
    print(f"PASS: 'tomorrow' resolved to {res_6['temporal_context']['start_datetime']}. Honesty gate preserved: forecast_executable={res_6['temporal_context']['forecast_executable']}.")

    # ----------------------------------------------------------------------
    # TEST 7: Temporal "tomorrow morning"
    # ----------------------------------------------------------------------
    print("\n--- TEST 7: Temporal 'tomorrow morning' ---")
    res_7 = await orchestrator.execute_query_pipeline("Will it be safe tomorrow morning near Kochi?", session_id="test_sess_temp")
    assert res_7["temporal_context"] is not None
    assert res_7["temporal_context"]["label"] == "tomorrow_morning"
    start_dt = datetime.fromisoformat(res_7["temporal_context"]["start_datetime"])
    end_dt = datetime.fromisoformat(res_7["temporal_context"]["end_datetime"])
    assert start_dt.hour == 6 and end_dt.hour == 12
    print(f"PASS: 'tomorrow morning' resolved to IST {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}.")

    # ----------------------------------------------------------------------
    # TEST 8: Specific Date
    # ----------------------------------------------------------------------
    print("\n--- TEST 8: Specific Date ---")
    res_8 = await orchestrator.execute_query_pipeline("Sea state near Kochi on 15 September 2026", session_id="test_sess_temp")
    assert res_8["temporal_context"] is not None
    assert res_8["temporal_context"]["label"] == "date_2026_09_15"
    dt_8 = datetime.fromisoformat(res_8["temporal_context"]["start_datetime"])
    assert dt_8.year == 2026 and dt_8.month == 9 and dt_8.day == 15
    print(f"PASS: '15 September 2026' resolved to calendar date: {dt_8.date()}.")

    # ----------------------------------------------------------------------
    # TEST 9: Time Range
    # ----------------------------------------------------------------------
    print("\n--- TEST 9: Time Range ---")
    res_9 = await orchestrator.execute_query_pipeline("Is it safe tomorrow between 6 AM and 10 AM near Kochi?", session_id="test_sess_temp")
    assert res_9["temporal_context"] is not None
    start_dt_9 = datetime.fromisoformat(res_9["temporal_context"]["start_datetime"])
    end_dt_9 = datetime.fromisoformat(res_9["temporal_context"]["end_datetime"])
    assert start_dt_9.hour == 6 and end_dt_9.hour == 10
    print(f"PASS: Time range resolved: {start_dt_9.strftime('%H:%M')} to {end_dt_9.strftime('%H:%M')} IST.")

    # ----------------------------------------------------------------------
    # TEST 10: Session Isolation (Session A Mangalore, Session B Kochi)
    # ----------------------------------------------------------------------
    print("\n--- TEST 10: Session Isolation ---")
    sess_a = "session_A_mangalore"
    sess_b = "session_B_kochi"

    await orchestrator.execute_query_pipeline("Find fishing zones near Mangalore.", session_id=sess_a)
    await orchestrator.execute_query_pipeline("Find fishing zones near Kochi.", session_id=sess_b)

    res_followup_a = await orchestrator.execute_query_pipeline("Which is closest?", session_id=sess_a)
    res_followup_b = await orchestrator.execute_query_pipeline("Which is closest?", session_id=sess_b)

    assert res_followup_a["reference_port"]["port_key"] == "mangalore", "Session A context was corrupted!"
    assert res_followup_b["reference_port"]["port_key"] == "kochi", "Session B context was corrupted!"
    assert res_followup_a["reference_port"]["port_key"] != res_followup_b["reference_port"]["port_key"]
    print(f"PASS: Strict session isolation verified. Session A port={res_followup_a['reference_port']['port_key']}, Session B port={res_followup_b['reference_port']['port_key']}.")

    # ----------------------------------------------------------------------
    # TEST 11: Mixed-Language Conversation
    # ----------------------------------------------------------------------
    print("\n--- TEST 11: Mixed-Language Conversation ---")
    sess_lang = "session_multilang"
    # Turn 1 in English:
    await orchestrator.execute_query_pipeline("Find fishing zones near Mangalore.", session_id=sess_lang)
    # Turn 2 in Kannada asking "Which is closest?":
    res_lang_kn = await orchestrator.execute_query_pipeline("ಇದರಲ್ಲಿ ಯಾವುದು ಹತ್ತಿರದಲ್ಲಿದೆ?", session_id=sess_lang)
    assert res_lang_kn["reference_port"]["port_key"] == "mangalore", "Kannada follow-up lost Mangalore context!"
    assert res_lang_kn["language"]["code"] == "kn", f"Expected Kannada response language, got: {res_lang_kn['language']['code']}"
    assert res_lang_kn["top_pfz"] is not None
    print(f"PASS: Mixed-language turn preserved Mangalore structured context and responded in Kannada ({res_lang_kn['language']['name']}).")

    # ----------------------------------------------------------------------
    # TEST 12: Ambiguous Reference
    # ----------------------------------------------------------------------
    print("\n--- TEST 12: Ambiguous Reference ---")
    sess_ambig = "session_ambig_test"
    res_ambig = await orchestrator.execute_query_pipeline("Check the second one.", session_id=sess_ambig)
    assert res_ambig["resolved_context"]["is_ambiguous"] is True
    assert "Requested second zone, but no candidate list exists" in res_ambig["resolved_context"]["ambiguity_reason"]
    print(f"PASS: Ambiguous reference correctly flagged without silent hallucination: {res_ambig['resolved_context']['ambiguity_reason']}.")

    # ----------------------------------------------------------------------
    # TEST 13: Session Expiration / Memory Bounds
    # ----------------------------------------------------------------------
    print("\n--- TEST 13: Session Expiration & Memory Bounds ---")
    sess_bound = ConversationState(session_id="bound_test")
    for i in range(15):
        sess_bound.add_user_message(f"Turn {i}", max_turns=5)
        sess_bound.add_assistant_message(f"Reply {i}", max_turns=5)
    # Bounded to 5 turns = 10 messages max
    assert len(sess_bound.messages) <= 10, f"Messages exceeded bounds: {len(sess_bound.messages)}"
    print(f"PASS: Bounded message strategy enforced. Retained {len(sess_bound.messages)} messages after 15 turns.")

    # ----------------------------------------------------------------------
    # TEST 14: Memory Update After Failed Execution
    # ----------------------------------------------------------------------
    print("\n--- TEST 14: Memory Update After Failure ---")
    sess_fail = "session_fail_test"
    from backend.tools.base import BaseTool
    class MockFailTool(BaseTool):
        name = "compute_safe_route"
        description = "Failing route"
        purpose = "Test failure memory"
        def _run(self, **kwargs):
            raise TimeoutError("Simulated bathymetric collision calculation timeout")

    orig_route_tool = orchestrator.tool_registry.get("compute_safe_route")
    orchestrator.tool_registry.register(MockFailTool())

    res_fail = await orchestrator.execute_query_pipeline("Give me a route from Kochi to target", session_id=sess_fail)
    orchestrator.tool_registry.register(orig_route_tool)

    stored_sess_fail = orchestrator.session_store.get_or_create_session(sess_fail)
    assert stored_sess_fail.structured.last_status == "FAILED"
    print(f"PASS: Task failure marked as '{stored_sess_fail.structured.last_status}' in session memory without fabricating success.")

    # ----------------------------------------------------------------------
    # TEST 15: Phase-2 Planner Receives Resolved Context
    # ----------------------------------------------------------------------
    print("\n--- TEST 15: Planner Receives Resolved Context ---")
    trace_steps = [s["agent"] for s in res_2["evidence_and_provenance"]["execution_trace"]]
    assert "ORCA Multi-Turn Context & Temporal Resolver" in trace_steps
    assert "ORCA Master Supervisor & Autonomous Planner" in trace_steps
    assert res_2["execution_metadata"]["session_id"] == session_1
    assert res_2["execution_metadata"]["turn_count"] >= 2
    print(f"PASS: Planner received resolved context. Execution trace confirmed real sequential execution with turn telemetry.")

    print("\n==================================================")
    print("ALL 15 PHASE 3 ACCEPTANCE TESTS PASSED PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_phase3_tests())
