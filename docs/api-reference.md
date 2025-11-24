# API Reference

Complete API documentation for StreamShape.

## Table of Contents

1. [Provider Classes](#provider-classes)
2. [Methods](#methods)
3. [Parameters](#parameters)
4. [Return Types](#return-types)
5. [Exceptions](#exceptions)

## Provider Classes

All provider classes inherit from `BaseLLMProvider` and share the same interface.

### OpenAI

```python
from streamshape import OpenAI

client = OpenAI(api_key: str, **kwargs)
```

**Parameters:**
- `api_key` (str, required): OpenAI API key
- `**kwargs`: Additional configuration options

**Supported Models:**
- `gpt-4`, `gpt-4-turbo`, `gpt-4-turbo-preview`
- `gpt-3.5-turbo`, `gpt-3.5-turbo-16k`

### Anthropic

```python
from streamshape import Anthropic

client = Anthropic(api_key: str, **kwargs)
```

**Parameters:**
- `api_key` (str, required): Anthropic API key
- `**kwargs`: Additional configuration options

**Supported Models:**
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`
- `claude-2.1`, `claude-2.0`


### Google

```python
from streamshape import Google

client = Google(api_key: str, **kwargs)
```

**Parameters:**
- `api_key` (str, required): Google API key
- `**kwargs`: Additional configuration options

**Supported Models:**
- `gemini-pro`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

### OpenRouter

```python
from streamshape import OpenRouter

client = OpenRouter(api_key: str, **kwargs)
```

**Parameters:**
- `api_key` (str, required): OpenRouter API key
- `**kwargs`: Additional configuration options

**Supported Models:** All models available on OpenRouter

### XAI

```python
from streamshape import XAI

client = XAI(api_key: str, **kwargs)
```

**Parameters:**
- `api_key` (str, required): xAI API key
- `**kwargs`: Additional configuration options

**Supported Models:**
- `grok-beta`
- `grok-vision-beta`

### OpenAICompatible

```python
from streamshape import OpenAICompatible

client = OpenAICompatible(
    api_key: str,
    base_url: str,
    **kwargs
)
```

**Parameters:**
- `api_key` (str, required): API key for the endpoint
- `base_url` (str, required): Base URL of the OpenAI-compatible endpoint
- `**kwargs`: Additional configuration options

**Use Cases:**
- Local models (Ollama, LM Studio, etc.)
- Custom OpenAI-compatible APIs
- Self-hosted models

### LiteLLM

```python
from streamshape import LiteLLM

client = LiteLLM(
    api_key: str,
    provider: str,
    **kwargs
)
```

**Parameters:**
- `api_key` (str, required): API key for the provider
- `provider` (str, required): Provider name (e.g., "openrouter", "anthropic", "openai", "gemini")
- `**kwargs`: Additional configuration options (e.g., base_url for custom endpoints)

**Use Cases:**
- Flexible provider switching without changing code
- Using providers without dedicated classes
- Dynamic provider selection at runtime
- Testing multiple providers

**Example:**
```python
# OpenRouter
client = LiteLLM(api_key="sk-or-...", provider="openrouter")

# Anthropic
client = LiteLLM(api_key="sk-ant-...", provider="anthropic")

# Custom endpoint
client = LiteLLM(
    api_key="...",
    provider="openai",
    base_url="http://localhost:11434/v1"
)
```

See [LiteLLM Provider Guide](litellm-provider.md) for detailed usage




## Methods

All provider classes share the same five methods:

### 1. generate()

Generate complete text response (non-streaming).

```python
result = client.generate(
    model: str,
    system_prompt: str,
    user_prompt: str,
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `model` (str, required): Model identifier
- `system_prompt` (str, required): Instructions for the LLM's behavior
- `user_prompt` (str, required): The actual query or request
- `**kwargs`: Optional parameters (temperature, max_tokens, top_p, etc.)

**Returns:**
```python
{
    "data": str,  # The generated text content
    "raw_chunks": object  # Raw API response object
}
```

**Example:**
```python
response = client.generate(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What is Python?",
    temperature=0.7,
    max_tokens=500
)
print(response["data"])
```

### 2. stream()

Stream text chunks as they're generated.

```python
for chunk in client.stream(
    model: str,
    system_prompt: str,
    user_prompt: str,
    **kwargs
) -> Iterator[Dict[str, Any]]
```

**Parameters:**
- `model` (str, required): Model identifier
- `system_prompt` (str, required): Instructions for the LLM's behavior
- `user_prompt` (str, required): The actual query or request
- `**kwargs`: Optional parameters (temperature, max_tokens, top_p, etc.)

**Yields:**
```python
{
    "data": str,  # Text chunk (empty string if None)
    "raw_chunks": object  # Raw streaming chunk object
}
```

**Example:**
```python
for chunk in client.stream(
    model="gpt-4",
    system_prompt="You are a storyteller.",
    user_prompt="Write a short story",
    temperature=0.8
):
    print(chunk["data"], end="", flush=True)
```

### 3. tool_call()

Execute function calling with tool definitions.

```python
result = client.tool_call(
    model: str,
    system_prompt: str,
    user_prompt: str,
    tools: List[Dict],
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `model` (str, required): Model identifier
- `system_prompt` (str, required): Instructions for the LLM's behavior
- `user_prompt` (str, required): The actual query or request
- `tools` (List[Dict], required): List of tool definitions in OpenAI format
- `**kwargs`: Optional parameters (temperature, max_tokens, etc.)

**Returns:**
```python
{
    "data": {
        "tool_name": str,  # Name of the tool to call
        "arguments": str   # JSON string of arguments
    },
    "raw_chunks": object  # Raw API response object
}
```

**Example:**
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

result = client.tool_call(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What's the weather in Paris?",
    tools=tools
)

print(result["data"]["tool_name"])    # "get_weather"
print(result["data"]["arguments"])    # '{"location": "Paris"}'
```

### 4. structured_output()

Generate validated Pydantic objects (non-streaming).

```python
result = client.structured_output(
    model: str,
    system_prompt: str,
    user_prompt: str,
    output_schema: Type[BaseModel],
    **kwargs
) -> Dict[str, Any]
```

**Parameters:**
- `model` (str, required): Model identifier
- `system_prompt` (str, required): Instructions for the LLM's behavior
- `user_prompt` (str, required): The actual query or request
- `output_schema` (Type[BaseModel], required): Pydantic BaseModel class
- `**kwargs`: Optional parameters (temperature, max_tokens, etc.)

**Returns:**
```python
{
    "data": List[BaseModel],  # List of validated Pydantic objects
    "raw_chunks": object      # Raw API response object
}
```

**Example:**
```python
from pydantic import BaseModel

class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    steps: list[str]

result = client.structured_output(
    model="gpt-4",
    system_prompt="You are a chef.",
    user_prompt="Give me 2 pasta recipes",
    output_schema=Recipe
)

for recipe in result["data"]:
    print(f"Recipe: {recipe.name}")
    print(f"Ingredients: {', '.join(recipe.ingredients)}")
```

### 5. structured_streaming_output()

Stream validated Pydantic objects as they're generated with usage data.

```python
for result in client.structured_streaming_output(
    model: str,
    system_prompt: str,
    user_prompt: str,
    output_schema: Type[BaseModel],
    **kwargs
) -> Iterator[Dict[str, Any]]
```

**Parameters:**
- `model` (str, required): Model identifier
- `system_prompt` (str, required): Instructions for the LLM's behavior
- `user_prompt` (str, required): The actual query or request
- `output_schema` (Type[BaseModel], required): Pydantic BaseModel class
- `**kwargs`: Optional parameters (temperature, max_tokens, etc.)

**Yields:**
```python
{
    "data": BaseModel or None,  # Validated Pydantic object (None for final chunk)
    "usage": dict,              # Token usage statistics (populated in final chunk)
    "finished": bool,           # True for final chunk
    "raw_chunks": list          # List of raw response chunks (only in final chunk)
}
```

**Example:**
```python
from pydantic import BaseModel

class Task(BaseModel):
    title: str
    priority: str
    estimated_hours: int

final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 5 tasks for building a website",
    output_schema=Task
):
    # Extract data and usage
    task = result.get("data")
    usage = result.get("usage")
    
    # Store usage data if present
    if usage:
        final_usage = usage
    
    # Skip final chunk (no data, just usage)
    if not task:
        continue
    
    print(f"Task: {task.title} (Priority: {task.priority})")

# Display token usage
if final_usage:
    print(f"\nTokens used: {final_usage.get('total_tokens')}")
```

## Parameters

### Common Optional Parameters

All methods accept these optional parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | float | 1.0 | Controls randomness (0.0-2.0). Lower = more focused, higher = more creative |
| `max_tokens` | int | None | Maximum tokens in response |
| `top_p` | float | 1.0 | Nucleus sampling threshold (0.0-1.0) |
| `frequency_penalty` | float | 0.0 | Reduce repetition (-2.0 to 2.0) |
| `presence_penalty` | float | 0.0 | Encourage new topics (-2.0 to 2.0) |
| `stop` | List[str] | None | Stop sequences |
| `n` | int | 1 | Number of completions to generate |

**Example:**
```python
response = client.generate(
    model="gpt-4",
    system_prompt="You are helpful.",
    user_prompt="Hello",
    temperature=0.7,
    max_tokens=100,
    top_p=0.9,
    frequency_penalty=0.5,
    presence_penalty=0.3
)
```

## Return Types

### Standard Return Format

All methods return a dictionary format:

```python
{
    "data": Any,      # The actual content/result
    "raw_chunks": Any # Raw API response object (or list for streaming)
}
```

**Note:** `structured_streaming_output()` also includes `usage` and `finished` keys for token tracking.

### Accessing Results

```python
# generate(), tool_call(), structured_output()
result = client.generate(...)
content = result["data"]
raw_response = result["raw_chunks"]

# stream()
for chunk in client.stream(...):
    text = chunk["data"]
    raw_chunk = chunk["raw_chunks"]

# structured_streaming_output()
for result in client.structured_streaming_output(...):
    obj = result.get("data")  # Pydantic object or None
    usage = result.get("usage")  # Token usage dict
    finished = result.get("finished")  # Boolean
    
    if obj:  # Skip final chunk with just usage
        print(obj.field_name)
```

## Exceptions

All exceptions inherit from `UnifiedLLMError`:

### Exception Hierarchy

```
UnifiedLLMError (base)
├── ConfigurationError
├── ValidationError
├── APIError
├── NetworkError
└── ParsingError
```

### Importing Exceptions

```python
from streamshape.exceptions import (
    UnifiedLLMError,
    ConfigurationError,
    ValidationError,
    APIError,
    NetworkError,
    ParsingError
)
```

### Exception Details

#### UnifiedLLMError
Base exception for all package errors.

#### ConfigurationError
Raised when provider configuration is invalid (e.g., missing base_url for OpenAICompatible).

#### ValidationError
Raised when input validation fails (e.g., empty model name, missing required parameters).

#### APIError
Raised when the LLM API call fails (e.g., authentication error, rate limit, invalid model).

**Attributes:**
- `provider`: Name of the provider where error occurred
- `original_error`: The underlying exception

#### NetworkError
Raised when network communication fails (e.g., connection timeout, DNS failure).

#### ParsingError
Raised when response parsing fails (structured output only).

### Error Handling Example

```python
from streamshape import OpenAI
from streamshape.exceptions import ValidationError, APIError, NetworkError

client = OpenAI(api_key="...")

try:
    response = client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt="Hello"
    )
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error from {e.provider}: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## See Also

- [Usage Guide](usage.md) - Detailed usage examples
- [Output Formats](output-formats.md) - Complete output structure reference
- [Error Handling](error-handling.md) - Comprehensive error handling guide
- [Examples](examples.md) - Real-world use cases
