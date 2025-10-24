"""Tool registry and definitions for LLM function calling.

Reference: https://inference-docs.cerebras.ai/capabilities/tool-use
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable


class ToolRegistry:
    """Registry for managing available tools/functions."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}
        self._schemas: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        function: Callable[..., Any],
        schema: dict[str, Any],
    ) -> None:
        """Register a tool with its function and schema.
        
        Args:
            name: Function name
            function: The actual Python function to execute
            schema: OpenAI-compatible tool schema
        """
        self._tools[name] = function
        self._schemas[name] = schema

    def get_function(self, name: str) -> Callable[..., Any] | None:
        """Get the function by name."""
        return self._tools.get(name)

    def get_schema(self, name: str) -> dict[str, Any] | None:
        """Get the schema by name."""
        return self._schemas.get(name)

    def get_all_schemas(self) -> list[dict[str, Any]]:
        """Get all tool schemas."""
        return list(self._schemas.values())

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by name with the given arguments.
        
        Args:
            name: Function name
            arguments: Function arguments as a dict
            
        Returns:
            Function result
            
        Raises:
            ValueError: If tool not found
        """
        function = self._tools.get(name)
        if function is None:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        return function(**arguments)


# Global tool registry
_tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _tool_registry


# ============================================================================
# Example Tools - Replace with your actual business logic
# ============================================================================


def calculate(expression: str) -> str:
    """A calculator tool that evaluates mathematical expressions.
    
    Args:
        expression: Mathematical expression (e.g., "25 * 4")
        
    Returns:
        Result as string or error message
    """
    # Sanitize expression
    expression = re.sub(r'[^0-9+\-*/().]', '', expression)
    
    try:
        result = eval(expression)  # noqa: S307
        return str(result)
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError) as exc:
        return f"Error: Invalid expression - {exc}"


def get_weather(location: str, unit: str = "celsius") -> str:
    """Get weather information for a location (mock implementation).
    
    Args:
        location: City name or location
        unit: Temperature unit (celsius or fahrenheit)
        
    Returns:
        Weather information as JSON string
    """
    # Mock implementation - replace with actual weather API
    return json.dumps({
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny",
        "humidity": 65
    })


# ============================================================================
# Register Default Tools
# ============================================================================


def register_default_tools() -> None:
    """Register the default set of tools."""
    registry = get_tool_registry()
    
    # Register calculator
    registry.register(
        name="calculate",
        function=calculate,
        schema={
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluates mathematical expressions and returns the result",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate (e.g., '25 * 4')"
                        }
                    },
                    "required": ["expression"]
                },
                "strict": True
            }
        }
    )
    
    # Register weather tool
    registry.register(
        name="get_weather",
        function=get_weather,
        schema={
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or location"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature unit"
                        }
                    },
                    "required": ["location"]
                },
                "strict": True
            }
        }
    )


# Auto-register on import
register_default_tools()

