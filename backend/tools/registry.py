"""
Central Tool Registry for ORCA / Blue Orbit
ISRO SIH 2026 - Problem Statement 26176
"""

import logging
from typing import Dict, Any, List, Optional
from backend.tools.base import BaseTool, ToolResult

logger = logging.getLogger("blue_orbit.tools.registry")

class ToolRegistry:
    """
    Central discovery and execution catalog for ORCA tools.
    Enables dynamic tool lookup, schema reflection, and safe execution.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registers a tool instance by its declared name."""
        if tool.name in self._tools:
            logger.warning(f"Overwriting existing tool registration for: {tool.name}")
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Optional[BaseTool]:
        """Retrieves a registered tool by name."""
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        """Checks if a tool name is registered."""
        return name in self._tools

    def list_tools(self) -> List[BaseTool]:
        """Returns all registered tool instances."""
        return list(self._tools.values())

    def get_tool_names(self) -> List[str]:
        """Returns list of registered tool names."""
        return list(self._tools.keys())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns introspectable schemas for all registered tools."""
        schemas = []
        for tool in self._tools.values():
            params = {}
            for p_name, p_def in tool.schema.parameters.items():
                params[p_name] = {
                    "type": p_def.param_type,
                    "description": p_def.description,
                    "required": p_def.required,
                    "default": p_def.default
                }
            schemas.append({
                "name": tool.name,
                "description": tool.description,
                "purpose": tool.purpose,
                "parameters": params,
                "return_description": tool.schema.return_description
            })
        return schemas

    async def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """
        Safely dispatches execution to the named tool.
        Returns a failed ToolResult if tool does not exist.
        """
        tool = self.get(name)
        if not tool:
            logger.error(f"Requested tool not found in registry: {name}")
            return ToolResult(
                tool_name=name,
                success=False,
                data=None,
                error=f"Tool '{name}' is not registered in ORCA ToolRegistry.",
                duration_ms=0.0,
                metadata={"registered_tools": self.get_tool_names()}
            )
        return await tool.execute(**kwargs)
