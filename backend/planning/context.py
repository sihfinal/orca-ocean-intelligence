"""
Runtime Execution Context for ORCA Requests
ISRO SIH 2026 - Problem Statement 26176
"""

import time
from typing import Dict, Any, List, Optional
from backend.planning.models import ExecutionPlan, Task, TaskStatus

class ORCAExecutionContext:
    """
    Central execution context for a single ORCA user request.
    Travels through planning, task execution, tool dispatch, and final synthesis.
    Strictly runtime-only (does not persist cross-turn memory in Phase 2).
    """
    def __init__(
        self,
        query: str,
        requested_lang: Optional[str] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        reference_port_override: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        self.query: str = query
        self.requested_lang: Optional[str] = requested_lang
        self.user_lat: Optional[float] = user_lat
        self.user_lon: Optional[float] = user_lon
        self.reference_port_override: Optional[str] = reference_port_override
        self.session_id: Optional[str] = session_id

        # Phase 3 Conversational & Temporal Context
        self.session: Optional[Any] = None
        self.resolved_context: Optional[Any] = None
        self.temporal_window: Optional[Any] = None

        self.start_time: float = time.time()
        self.total_latency_ms: float = 0.0

        # Request Understanding
        self.understanding: Dict[str, Any] = {}
        self.detected_lang: str = "en"
        self.intent: str = "general_inquiry"

        # Plan & Graph
        self.plan: Optional[ExecutionPlan] = None
        self.task_results: Dict[str, Any] = {}
        self.tasks_by_id: Dict[str, Task] = {}

        # Resolved Data Bundles for Downstream Consumption
        self.port_info: Dict[str, Any] = {}
        self.top_pfz: Dict[str, Any] = {}
        self.all_pfz: List[Dict[str, Any]] = []
        self.weather: Dict[str, Any] = {}
        self.geofence: Dict[str, Any] = {}
        self.safe_route: Dict[str, Any] = {}
        self.satellite_telemetry: List[Dict[str, Any]] = []
        self.satellite_raster: Dict[str, Any] = {}
        self.cyclone_info: Dict[str, Any] = {}
        self.pfz_candidates: List[Dict[str, Any]] = []
        self.pfz_analysis: Dict[str, Any] = {}
        self.safety_evaluations: List[Dict[str, Any]] = []
        self.decision: Dict[str, Any] = {}
        self.evidence_package: Dict[str, Any] = {}
        self.claim_validation: Dict[str, Any] = {}

        # Real Execution Trace
        self.execution_trace: List[Dict[str, Any]] = []

        # Observations, Failures & Validation
        self.errors: List[str] = []
        self.limitations: List[str] = []
        self.validation_notes: List[str] = []
        self.completed_tasks_count: int = 0
        self.failed_tasks_count: int = 0

    def add_trace_step(self, step: Dict[str, Any]) -> None:
        """Appends an actual execution step to the runtime trace."""
        self.execution_trace.append(step)

    def mark_task_complete(self, task: Task, data: Any) -> None:
        """Records task completion and stores data into context."""
        task.status = TaskStatus.COMPLETED
        task.result = data
        self.task_results[task.task_id] = data
        self.tasks_by_id[task.task_id] = task
        self.completed_tasks_count += 1

    def mark_task_failed(self, task: Task, error: str) -> None:
        """Records task failure without fabricating data."""
        task.status = TaskStatus.FAILED
        task.error = error
        self.tasks_by_id[task.task_id] = task
        self.errors.append(f"{task.task_id} failed: {error}")
        self.limitations.append(f"Subtask '{task.title}' could not be completed ({error}).")
        self.failed_tasks_count += 1

    def mark_task_blocked(self, task: Task, missing_deps: List[str]) -> None:
        """Marks a task blocked due to upstream dependency failure."""
        task.status = TaskStatus.BLOCKED
        task.error = f"Upstream dependency failed or missing: {', '.join(missing_deps)}"
        self.tasks_by_id[task.task_id] = task
        self.limitations.append(f"Subtask '{task.title}' blocked because upstream {missing_deps} did not complete successfully.")

    def build_context_bundle(self) -> Dict[str, Any]:
        """Assembles the available telemetry bundle for final response generation."""
        return {
            "port": self.port_info,
            "top_pfz": self.top_pfz,
            "weather": self.weather,
            "geofence": self.geofence,
            "route": self.safe_route,
            "telemetry": self.satellite_telemetry,
            "satellite_raster": self.satellite_raster,
            "cyclones": self.cyclone_info,
            "pfz_candidates": self.pfz_candidates,
            "pfz_analysis": self.pfz_analysis,
            "safety_evaluations": self.safety_evaluations,
            "decision": self.decision,
            "evidence_package": self.evidence_package,
            "claim_validation": self.claim_validation,
            "limitations": self.limitations,
            "validation_notes": self.validation_notes,
            "temporal_window": self.temporal_window.to_dict() if self.temporal_window else None,
            "session_id": self.session_id
        }
