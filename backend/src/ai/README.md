# AI Module - Cerebras LLM Integration

Complete integration with Cerebras Cloud SDK for LLM interactions with automatic tool/function calling.

## Features

- ✅ Cerebras Cloud SDK integration
- ✅ Function calling / Tool use
- ✅ Automatic tool execution
- ✅ Streaming support
- ✅ Default model: `gpt-oss-120b`

## Quick Start

### 1. Set Environment Variable

```bash
export CEREBRAS_API_KEY="your-api-key-here"
```

Or add to your `.env` file:
```
CEREBRAS_API_KEY=your-api-key-here
```

### 2. API Endpoints

#### GET `/ai/models`
List available Cerebras models.

#### GET `/ai/tools`
List available tools/functions that the LLM can call.

#### POST `/ai/chat/auto` ⭐ **Main Endpoint**
Automatic tool execution - handles the full loop for you.

**Example: Simple Math**
```bash
curl -X POST http://localhost:8000/ai/chat/auto \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Add 5 and 3"}]
  }'
```

#### POST `/ai/chat/auto/stream` ⭐ **Streaming with Tools**
Automatic tool execution with streaming response.

**Example: Streaming Math**
```bash
curl -X POST http://localhost:8000/ai/chat/auto/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is 125 divided by 5?"}]
  }'
```

Note: Tools are executed first (blocking), then the final response is streamed in real-time.

**Response:**
```json
{
  "response": {
    "choices": [{
      "message": {
        "role": "assistant",
        "content": "The sum of 5 and 3 is 8."
      }
    }]
  },
  "text": "The sum of 5 and 3 is 8.",
  "conversation": [
    {"role": "user", "content": "Add 5 and 3"},
    {"role": "assistant", "tool_calls": [...]},
    {"role": "tool", "content": "8", "name": "calculate"},
    {"role": "assistant", "content": "The sum of 5 and 3 is 8."}
  ],
  "tool_calls_executed": 1
}
```

**Example: Complex Calculation**
```bash
curl -X POST http://localhost:8000/ai/chat/auto \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is 25 multiplied by 4?"}]
  }'
```

**Example: Weather (Mock)**
```bash
curl -X POST http://localhost:8000/ai/chat/auto \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the weather in Paris?"}]
  }'
```

## Built-in Tools

### 1. `calculate`
Evaluates mathematical expressions.

**Example:**
- "Add 5 and 3"
- "What is 125 divided by 5?"
- "Calculate (10 + 5) * 3"

### 2. `get_weather` (Mock)
Returns mock weather data.

**Example:**
- "What's the weather in London?"
- "Get weather for Tokyo in fahrenheit"

## Using System Prompt Directly

You can import and use the system prompt directly in your code:

```python
from src.ai.prompts import SYSTEM_PROMPT

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Add 5 and 3"}
]
```

The system prompt encourages the AI to use tools when available for accurate results.

## Adding Custom Tools

### Step 1: Define Your Function

```python
# In src/ai/tools.py

def my_custom_tool(param1: str, param2: int) -> str:
    """Your business logic here."""
    return f"Result: {param1} - {param2}"
```

### Step 2: Register the Tool

```python
# In src/ai/tools.py, inside register_default_tools()

registry.register(
    name="my_custom_tool",
    function=my_custom_tool,
    schema={
        "type": "function",
        "function": {
            "name": "my_custom_tool",
            "description": "What this tool does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Second parameter"
                    }
                },
                "required": ["param1", "param2"]
            },
            "strict": True
        }
    }
)
```

### Step 3: Use It!

The LLM will automatically discover and call your tool when appropriate.

```bash
curl -X POST http://localhost:8000/ai/chat/auto \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Call my_custom_tool with hello and 42"}]
  }'
```

## Module Structure

```
src/ai/
├── __init__.py       # Package exports
├── client.py         # Cerebras SDK client wrapper
├── executor.py       # Tool execution orchestrator
├── models.py         # Model registry
├── prompts.py        # System prompts
├── tools.py          # Tool registry and definitions
└── README.md         # This file
```

## How Tool Calling Works

1. **User asks a question** → "Add 5 and 3"
2. **LLM receives tools** → Sees `calculate` tool is available
3. **LLM decides to call tool** → `calculate(expression="5+3")`
4. **Executor executes function** → Python function runs → Returns "8"
5. **Result sent back to LLM** → LLM receives "8"
6. **LLM generates response** → "The sum of 5 and 3 is 8."
7. **User gets final answer** ✅

## Configuration

### Default Model
Default: `gpt-oss-120b`

Change in `src/ai/client.py`:
```python
_DEFAULT_MODEL = "llama3.1-70b"
```

### Available Models
- `gpt-oss-120b` (default, 65K context, reasoning support)
- `llama3.1-8b` (128K context)
- `llama3.1-70b` (128K context)
- `llama3.3-70b` (128K context)

## Reference

- [Cerebras Tool Use Documentation](https://inference-docs.cerebras.ai/capabilities/tool-use)
- [Cerebras Inference API](https://inference-docs.cerebras.ai/)

