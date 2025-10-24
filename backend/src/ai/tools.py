"""Tool registry and definitions for LLM function calling.

Reference: https://inference-docs.cerebras.ai/capabilities/tool-use
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from ..db import DatabaseManager
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

# Initialize database manager for tools
_db_manager: DatabaseManager | None = None


def _get_db_manager() -> DatabaseManager:
    """Get or create the database manager instance for tools."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.connect()
    return _db_manager


def list_available_pods() -> str:
    """List all available pods that can be booked.
    
    Returns:
        JSON string with list of pods including name, description, capacity, and price
    """
    try:
        db = _get_db_manager()
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, capacity, price_cents, is_active, created_at, updated_at
                FROM pods
                ORDER BY name
                """
            )
            rows = cur.fetchall()
            
            pods = [
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "capacity": row[3],
                    "price_cents": row[4],
                    "is_active": row[5],
                    "created_at": row[6].isoformat() if row[6] else None,
                    "updated_at": row[7].isoformat() if row[7] else None,
                }
                for row in rows
            ]
            return json.dumps(pods)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to fetch pods: {str(exc)}"})


def get_pod_details(pod_id: int) -> str:
    """Get detailed information about a specific pod.
    
    Args:
        pod_id: The ID of the pod to retrieve
        
    Returns:
        JSON string with pod details including name, description, capacity, and price
    """
    try:
        db = _get_db_manager()
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, capacity, price_cents, is_active, created_at, updated_at
                FROM pods
                WHERE id = %s
                """,
                (pod_id,),
            )
            row = cur.fetchone()
            
            if row is None:
                return json.dumps({"error": "Pod not found"})
            
            pod = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "capacity": row[3],
                "price_cents": row[4],
                "is_active": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None,
            }
            return json.dumps(pod)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to fetch pod: {str(exc)}"})


def list_user_bookings() -> str:
    """List all bookings in the system.
    
    Returns:
        JSON string with list of bookings including pod, time slots, and status
    """
    try:
        db = _get_db_manager()
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_id, pod_id, start_time, end_time, status, total_price_cents, created_at, updated_at
                FROM bookings
                ORDER BY start_time DESC
                """
            )
            rows = cur.fetchall()
            
            bookings = [
                {
                    "id": row[0],
                    "user_id": row[1],
                    "pod_id": row[2],
                    "start_time": row[3].isoformat() if row[3] else None,
                    "end_time": row[4].isoformat() if row[4] else None,
                    "status": row[5],
                    "total_price_cents": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None,
                }
                for row in rows
            ]
            return json.dumps(bookings)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to fetch bookings: {str(exc)}"})


def get_booking_details(booking_id: int) -> str:
    """Get detailed information about a specific booking.
    
    Args:
        booking_id: The ID of the booking to retrieve
        
    Returns:
        JSON string with booking details including pod, times, status, and price
    """
    try:
        db = _get_db_manager()
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_id, pod_id, start_time, end_time, status, total_price_cents, created_at, updated_at
                FROM bookings
                WHERE id = %s
                """,
                (booking_id,),
            )
            row = cur.fetchone()
            
            if row is None:
                return json.dumps({"error": "Booking not found"})
            
            booking = {
                "id": row[0],
                "user_id": row[1],
                "pod_id": row[2],
                "start_time": row[3].isoformat() if row[3] else None,
                "end_time": row[4].isoformat() if row[4] else None,
                "status": row[5],
                "total_price_cents": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None,
            }
            return json.dumps(booking)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to fetch booking: {str(exc)}"})


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
        db = _get_db_manager()
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bookings (user_id, pod_id, start_time, end_time, status, total_price_cents)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, pod_id, start_time, end_time, status, total_price_cents, created_at, updated_at
                """,
                (user_id, pod_id, start_time, end_time, "pending", total_price_cents),
            )
            row = cur.fetchone()
            
            booking = {
                "id": row[0],
                "user_id": row[1],
                "pod_id": row[2],
                "start_time": row[3].isoformat() if row[3] else None,
                "end_time": row[4].isoformat() if row[4] else None,
                "status": row[5],
                "total_price_cents": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None,
            }
            return json.dumps(booking)
    except Exception as exc:  # noqa: BLE001
        error_str = str(exc)
        if "uq_pod_time_window" in error_str or "duplicate key" in error_str:
            return json.dumps({"error": "Booking conflict - time slot already taken"})
        return json.dumps({"error": f"Failed to create booking: {error_str}"})


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
        updates: list[str] = []
        params: list[Any] = []

        if start_time is not None:
            updates.append("start_time = %s")
            params.append(start_time)
        if end_time is not None:
            updates.append("end_time = %s")
            params.append(end_time)
        if status is not None:
            updates.append("status = %s")
            params.append(status)

        if not updates:
            return json.dumps({"error": "No fields provided for update"})

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(booking_id)

        db = _get_db_manager()
        with db.cursor() as cur:
            cur.execute(
                f"""
                UPDATE bookings
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, user_id, pod_id, start_time, end_time, status, total_price_cents, created_at, updated_at
                """,
                tuple(params),
            )
            row = cur.fetchone()
            
            if row is None:
                return json.dumps({"error": "Booking not found"})
            
            booking = {
                "id": row[0],
                "user_id": row[1],
                "pod_id": row[2],
                "start_time": row[3].isoformat() if row[3] else None,
                "end_time": row[4].isoformat() if row[4] else None,
                "status": row[5],
                "total_price_cents": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None,
            }
            return json.dumps(booking)
    except Exception as exc:  # noqa: BLE001
        error_str = str(exc)
        if "uq_pod_time_window" in error_str or "duplicate key" in error_str:
            return json.dumps({"error": "Booking conflict - time slot already taken"})
        return json.dumps({"error": f"Failed to update booking: {error_str}"})


def cancel_booking(booking_id: int) -> str:
    """Cancel/delete a booking.
    
    Args:
        booking_id: The ID of the booking to cancel
        
    Returns:
        JSON string with success or error message
    """
    try:
        db = _get_db_manager()
        with db.cursor() as cur:
            cur.execute("DELETE FROM bookings WHERE id = %s RETURNING id", (booking_id,))
            row = cur.fetchone()
            
            if row is None:
                return json.dumps({"error": "Booking not found"})
            
            return json.dumps({"success": True, "message": "Booking cancelled successfully"})
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": f"Failed to cancel booking: {str(exc)}"})


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

