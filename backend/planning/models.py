"""
Task & Plan Representation Models for ORCA
ISRO SIH 2026 - Problem Statement 26176
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"

class Task(BaseModel):
    task_id: str
    title: str
    responsible_agent: str
    selected_tool: str
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    step_id: str = "STEP_AGENT_EXECUTION"
    thought: str = ""
    output_summary: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_execution_step(self) -> Dict[str, Any]:
        """Converts task execution record into frontend-compatible AgentExecutionStep format."""
        return {
            "step_id": self.step_id,
            "agent": self.responsible_agent,
            "tool": self.selected_tool,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "thought": self.thought,
            "output_summary": self.output_summary or (f"Completed with status: {self.status.value}" if self.status == TaskStatus.COMPLETED else str(self.error or "No output"))
        }

class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    user_goal: str
    intent: str
    complexity: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    tasks: List[Task] = Field(default_factory=list)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    rationale: str = ""
