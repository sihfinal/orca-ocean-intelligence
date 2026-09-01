"""
Standard Tool Abstraction for ORCA / Blue Orbit
ISRO SIH 2026 - Problem Statement 26176
"""

import time
import inspect
from typing import Dict, Any, Optional, Type, Callable, List
from dataclasses import dataclass, field
from pydantic import BaseModel

@dataclass
class ToolParameter:
    name: str
    param_type: str
    description: str
    required: bool = True
    default: Any = None

@dataclass
class ToolSchema:
    name: str
    description: str
    purpose: str
    parameters: Dict[str, ToolParameter] = field(default_factory=dict)
    return_description: str = "JSON-serializable result dictionary"

@dataclass
class ToolResult:
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

class BaseTool:
    """
    Standard interface for all callable tools in ORCA.
    Wraps domain actions, provides schemas, validates inputs, and captures execution metrics.
    """
    name: str = "base_tool"
    description: str = "Base tool abstraction"
    purpose: str = "General execution"
    
    def __init__(self):
        self.schema = self._build_schema()

    def _build_schema(self) -> ToolSchema:
        """Subclasses define their explicit parameter schema here."""
        return ToolSchema(
            name=self.name,
            description=self.description,
            purpose=self.purpose,
            parameters={}
        )

    async def execute(self, **kwargs) -> ToolResult:
        """
        Executes the tool with timing, parameter validation, and safe error capture.
        """
        start_time = time.time()
        
        # Validate required parameters against schema
        missing_params = []
        for param_name, param_def in self.schema.parameters.items():
            if param_def.required and param_name not in kwargs and param_def.default is None:
                missing_params.append(param_name)
                
        if missing_params:
            return ToolResult(
                tool_name=self.name,
                success=False,
                data=None,
                error=f"Missing required parameter(s): {', '.join(missing_params)}",
                duration_ms=round((time.time() - start_time) * 1000, 2),
                metadata={"validation_failed": True}
            )

        try:
            # Execute underlying logic (supports both async and sync implementations)
            if inspect.iscoroutinefunction(self._run):
                raw_data = await self._run(**kwargs)
            else:
                raw_data = self._run(**kwargs)

            duration = round((time.time() - start_time) * 1000, 2)
            return ToolResult(
                tool_name=self.name,
                success=True,
                data=raw_data,
                error=None,
                duration_ms=duration,
                metadata={"executed_at": time.time()}
            )
        except Exception as exc:
            duration = round((time.time() - start_time) * 1000, 2)
            return ToolResult(
                tool_name=self.name,
                success=False,
                data=None,
                error=f"Tool '{self.name}' execution error: {type(exc).__name__}: {str(exc)}",
                duration_ms=duration,
                metadata={"exception_class": type(exc).__name__}
            )

    def _run(self, **kwargs) -> Any:
        """Actual business logic implementation."""
        raise NotImplementedError(f"Tool {self.name} must implement _run()")
