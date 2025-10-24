"""Tool registry and definitions for LLM function calling.

Reference: https://inference-docs.cerebras.ai/capabilities/tool-use
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

import httpx

from ..settings import settings


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
# Kubo Booking System Tools
# ============================================================================

# Base URL for internal API calls
API_BASE_URL = "http://localhost:8000"


def list_available_pods() -> str:
    """List all available pods that can be booked.
    
    Returns:
        JSON string with list of pods including name, description, capacity, and price
    """
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE_URL}/kubo/pods")
            response.raise_for_status()
            return json.dumps(response.json())
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to fetch pods: {exc}"})


def get_pod_details(pod_id: int) -> str:
    """Get detailed information about a specific pod.
    
    Args:
        pod_id: The ID of the pod to retrieve
        
    Returns:
        JSON string with pod details including name, description, capacity, and price
    """
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE_URL}/kubo/pods/{pod_id}")
            response.raise_for_status()
            return json.dumps(response.json())
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "Pod not found"})
        return json.dumps({"error": f"Failed to fetch pod: {exc}"})
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to fetch pod: {exc}"})


def list_user_bookings() -> str:
    """List all bookings in the system.
    
    Returns:
        JSON string with list of bookings including pod, time slots, and status
    """
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE_URL}/kubo/bookings")
            response.raise_for_status()
            return json.dumps(response.json())
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to fetch bookings: {exc}"})


def get_booking_details(booking_id: int) -> str:
    """Get detailed information about a specific booking.
    
    Args:
        booking_id: The ID of the booking to retrieve
        
    Returns:
        JSON string with booking details including pod, times, status, and price
    """
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE_URL}/kubo/bookings/{booking_id}")
            response.raise_for_status()
            return json.dumps(response.json())
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "Booking not found"})
        return json.dumps({"error": f"Failed to fetch booking: {exc}"})
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to fetch booking: {exc}"})


def create_booking(
    user_id: int,
    pod_id: int,
    start_time: str,
    end_time: str,
    total_price_cents: int,
) -> str:
    """Create a new booking for a pod.
    
    Args:
        user_id: The ID of the user making the booking
        pod_id: The ID of the pod to book
        start_time: Start time in ISO format (e.g., "2024-01-15T10:00:00Z")
        end_time: End time in ISO format (e.g., "2024-01-15T12:00:00Z")
        total_price_cents: Total price in cents
        
    Returns:
        JSON string with the created booking details
    """
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{API_BASE_URL}/kubo/bookings",
                json={
                    "user_id": user_id,
                    "pod_id": pod_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "pending",
                    "total_price_cents": total_price_cents,
                },
            )
            response.raise_for_status()
            return json.dumps(response.json())
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            return json.dumps({"error": "Booking conflict - time slot already taken"})
        return json.dumps({"error": f"Failed to create booking: {exc}"})
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to create booking: {exc}"})


def update_booking(
    booking_id: int,
    start_time: str | None = None,
    end_time: str | None = None,
    status: str | None = None,
) -> str:
    """Update an existing booking.
    
    Args:
        booking_id: The ID of the booking to update
        start_time: New start time in ISO format (optional)
        end_time: New end time in ISO format (optional)
        status: New status - one of: pending, confirmed, cancelled, completed (optional)
        
    Returns:
        JSON string with the updated booking details
    """
    try:
        payload = {}
        if start_time is not None:
            payload["start_time"] = start_time
        if end_time is not None:
            payload["end_time"] = end_time
        if status is not None:
            payload["status"] = status
        
        if not payload:
            return json.dumps({"error": "No fields provided for update"})
        
        with httpx.Client() as client:
            response = client.patch(
                f"{API_BASE_URL}/kubo/bookings/{booking_id}",
                json=payload,
            )
            response.raise_for_status()
            return json.dumps(response.json())
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "Booking not found"})
        if exc.response.status_code == 409:
            return json.dumps({"error": "Booking conflict - time slot already taken"})
        return json.dumps({"error": f"Failed to update booking: {exc}"})
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to update booking: {exc}"})


def cancel_booking(booking_id: int) -> str:
    """Cancel/delete a booking.
    
    Args:
        booking_id: The ID of the booking to cancel
        
    Returns:
        JSON string with success or error message
    """
    try:
        with httpx.Client() as client:
            response = client.delete(f"{API_BASE_URL}/kubo/bookings/{booking_id}")
            response.raise_for_status()
            return json.dumps({"success": True, "message": "Booking cancelled successfully"})
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "Booking not found"})
        return json.dumps({"error": f"Failed to cancel booking: {exc}"})
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to cancel booking: {exc}"})


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
    
    # Register Kubo booking tools
    registry.register(
        name="list_available_pods",
        function=list_available_pods,
        schema={
            "type": "function",
            "function": {
                "name": "list_available_pods",
                "description": "List all available pods that can be booked. Shows pod names, descriptions, capacity, and pricing.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "strict": True
            }
        }
    )
    
    registry.register(
        name="get_pod_details",
        function=get_pod_details,
        schema={
            "type": "function",
            "function": {
                "name": "get_pod_details",
                "description": "Get detailed information about a specific pod including capacity, pricing, and availability status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pod_id": {
                            "type": "integer",
                            "description": "The ID of the pod to retrieve"
                        }
                    },
                    "required": ["pod_id"]
                },
                "strict": True
            }
        }
    )
    
    registry.register(
        name="list_user_bookings",
        function=list_user_bookings,
        schema={
            "type": "function",
            "function": {
                "name": "list_user_bookings",
                "description": "List all bookings in the system with details about pod, time slots, status, and pricing.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "strict": True
            }
        }
    )
    
    registry.register(
        name="get_booking_details",
        function=get_booking_details,
        schema={
            "type": "function",
            "function": {
                "name": "get_booking_details",
                "description": "Get detailed information about a specific booking including pod assignment, time range, status, and total price.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "booking_id": {
                            "type": "integer",
                            "description": "The ID of the booking to retrieve"
                        }
                    },
                    "required": ["booking_id"]
                },
                "strict": True
            }
        }
    )
    
    registry.register(
        name="create_booking",
        function=create_booking,
        schema={
            "type": "function",
            "function": {
                "name": "create_booking",
                "description": "Create a new booking for a pod. Requires user ID, pod ID, time range, and price calculation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "The ID of the user making the booking"
                        },
                        "pod_id": {
                            "type": "integer",
                            "description": "The ID of the pod to book"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time in ISO 8601 format (e.g., '2024-01-15T10:00:00Z')"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time in ISO 8601 format (e.g., '2024-01-15T12:00:00Z')"
                        },
                        "total_price_cents": {
                            "type": "integer",
                            "description": "Total price in cents (e.g., 5000 for $50.00)"
                        }
                    },
                    "required": ["user_id", "pod_id", "start_time", "end_time", "total_price_cents"]
                },
                "strict": True
            }
        }
    )
    
    registry.register(
        name="update_booking",
        function=update_booking,
        schema={
            "type": "function",
            "function": {
                "name": "update_booking",
                "description": "Update an existing booking's time range or status. At least one field must be provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "booking_id": {
                            "type": "integer",
                            "description": "The ID of the booking to update"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "New start time in ISO 8601 format (optional)"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "New end time in ISO 8601 format (optional)"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "confirmed", "cancelled", "completed"],
                            "description": "New booking status (optional)"
                        }
                    },
                    "required": ["booking_id"]
                },
                "strict": True
            }
        }
    )
    
    registry.register(
        name="cancel_booking",
        function=cancel_booking,
        schema={
            "type": "function",
            "function": {
                "name": "cancel_booking",
                "description": "Cancel and delete a booking. This action cannot be undone.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "booking_id": {
                            "type": "integer",
                            "description": "The ID of the booking to cancel"
                        }
                    },
                    "required": ["booking_id"]
                },
                "strict": True
            }
        }
    )


# Auto-register on import
register_default_tools()

