"""Tool execution orchestrator for handling LLM function calling loops.

Reference: https://inference-docs.cerebras.ai/capabilities/tool-use
"""

from __future__ import annotations

import json
from typing import Any

from .client import CerebrasClient, get_cerebras_client
from .prompts import SYSTEM_PROMPT
from .tools import get_tool_registry


class ToolExecutor:
    """Orchestrates the tool calling loop with LLM."""

    def __init__(self, client: CerebrasClient | None = None, max_iterations: int = 5) -> None:
        """Initialize the tool executor.
        
        Args:
            client: Cerebras client instance
            max_iterations: Maximum number of tool calling iterations to prevent infinite loops
        """
        self.client = client or get_cerebras_client()
        self.max_iterations = max_iterations
        self.tool_registry = get_tool_registry()

    def execute_with_tools(
        self,
        *,
        messages: list[dict[str, Any]],
    ) -> tuple[Any, list[dict[str, Any]]]:
        """Execute a chat completion with automatic tool calling.
        
        This method handles the full tool calling loop:
        1. Call LLM with tools
        2. If LLM requests tool calls, execute them
        3. Send results back to LLM
        4. Repeat until LLM returns a final response
        
        Args:
            messages: Initial conversation messages
            
        Returns:
            Tuple of (final_response, full_conversation_history)
        """
        # Get all registered tools
        tools = self.tool_registry.get_all_schemas()
        
        # Add system prompt if not already present
        has_system = any(msg.get("role") == "system" for msg in messages)
        if not has_system:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(messages)
        
        # Make a copy of messages to track the conversation
        conversation = list(messages)
        
        for iteration in range(self.max_iterations):
            # Call LLM
            response = self.client.chat_completion(
                messages=conversation,
                tools=tools,
            )
            
            # Extract the assistant message
            if hasattr(response, 'choices'):
                choice = response.choices[0]
                message = choice.message
            else:
                # Fallback for dict response
                choice = response.get('choices', [{}])[0]
                message = choice.get('message', {})
            
            # Add assistant message to conversation
            assistant_message = self._message_to_dict(message)
            conversation.append(assistant_message)
            
            # Check if there are tool calls
            tool_calls = self._extract_tool_calls(message)
            
            if not tool_calls:
                # No more tool calls, return final response
                return response, conversation
            
            # Execute each tool call
            for tool_call in tool_calls:
                tool_result = self._execute_tool_call(tool_call)
                
                # Add tool result to conversation
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", ""),
                    "name": tool_call.get("function", {}).get("name", ""),
                    "content": tool_result,
                })
        
        # Max iterations reached, return last response
        return response, conversation

    def _extract_tool_calls(self, message: Any) -> list[dict[str, Any]]:
        """Extract tool calls from the assistant message.
        
        Args:
            message: Assistant message object
            
        Returns:
            List of tool call dictionaries
        """
        if hasattr(message, 'tool_calls') and message.tool_calls:
            # SDK object
            return [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in message.tool_calls
            ]
        elif isinstance(message, dict) and message.get('tool_calls'):
            # Dict response
            return message['tool_calls']
        
        return []

    def _message_to_dict(self, message: Any) -> dict[str, Any]:
        """Convert message object to dictionary.
        
        Args:
            message: Message object from SDK
            
        Returns:
            Dictionary representation
        """
        if hasattr(message, 'model_dump'):
            return message.model_dump()
        elif hasattr(message, 'dict'):
            return message.dict()
        elif isinstance(message, dict):
            return message
        
        # Fallback
        return {
            "role": getattr(message, 'role', 'assistant'),
            "content": getattr(message, 'content', ''),
        }

    def _execute_tool_call(self, tool_call: dict[str, Any]) -> str:
        """Execute a single tool call.
        
        Args:
            tool_call: Tool call dictionary with function name and arguments
            
        Returns:
            Tool execution result as JSON string
        """
        function_name = tool_call.get("function", {}).get("name", "")
        arguments_str = tool_call.get("function", {}).get("arguments", "{}")
        
        try:
            # Parse arguments
            if isinstance(arguments_str, str):
                arguments = json.loads(arguments_str)
            else:
                arguments = arguments_str
            
            # Execute the tool
            result = self.tool_registry.execute(function_name, arguments)
            
            # Return result as JSON string
            if isinstance(result, str):
                return result
            return json.dumps(result)
            
        except json.JSONDecodeError as exc:
            return json.dumps({"error": f"Invalid JSON arguments: {exc}"})
        except ValueError as exc:
            return json.dumps({"error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": f"Tool execution failed: {exc}"})


def execute_with_tools(
    *,
    messages: list[dict[str, Any]],
) -> tuple[Any, list[dict[str, Any]]]:
    """Convenience function to execute chat with tool calling.
    
    Args:
        messages: Initial conversation messages
        
    Returns:
        Tuple of (final_response, conversation_history)
    """
    executor = ToolExecutor()
    return executor.execute_with_tools(messages=messages)


def execute_with_tools_streaming(
    *,
    messages: list[dict[str, Any]],
) -> Any:
    """Execute chat with tool calling and stream the final response.
    
    This function:
    1. Handles the tool calling loop (blocking)
    2. Executes any tools needed
    3. Streams only the final response after all tools are done
    
    Args:
        messages: Initial conversation messages
        
    Yields:
        Response chunks from the final streaming completion
    """
    executor = ToolExecutor()
    
    # Get all registered tools
    tools = executor.tool_registry.get_all_schemas()
    
    # Add system prompt if not already present
    has_system = any(msg.get("role") == "system" for msg in messages)
    if not has_system:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(messages)
    
    # Make a copy of messages to track the conversation
    conversation = list(messages)
    
    # Handle tool calling loop (blocking until no more tools needed)
    for iteration in range(executor.max_iterations):
        # Call LLM (blocking)
        response = executor.client.chat_completion(
            messages=conversation,
            tools=tools,
        )
        
        # Extract the assistant message
        if hasattr(response, 'choices'):
            choice = response.choices[0]
            message = choice.message
        else:
            choice = response.get('choices', [{}])[0]
            message = choice.get('message', {})
        
        # Add assistant message to conversation
        assistant_message = executor._message_to_dict(message)
        conversation.append(assistant_message)
        
        # Check if there are tool calls
        tool_calls = executor._extract_tool_calls(message)
        
        if not tool_calls:
            # No more tool calls - now stream the final response
            # Remove the last assistant message since we'll stream it
            conversation.pop()
            
            # Stream the final response
            for chunk in executor.client.chat_completion_stream(messages=conversation):
                yield chunk
            return
        
        # Execute each tool call
        for tool_call in tool_calls:
            tool_result = executor._execute_tool_call(tool_call)
            
            # Add tool result to conversation
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", ""),
                "name": tool_call.get("function", {}).get("name", ""),
                "content": tool_result,
            })
    
    # Max iterations reached - stream last response anyway
    for chunk in executor.client.chat_completion_stream(messages=conversation):
        yield chunk

