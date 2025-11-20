# LiteLLM General Provider

The `LiteLLM` class is a general-purpose provider that allows you to use any LiteLLM-supported provider without needing a specific provider class.

## When to Use

Use `LiteLLM` when:
- You want flexibility to switch between providers easily
- You're using a provider that doesn't have a dedicated class
- You want to pass the provider name dynamically
- You prefer the LiteLLM format directly

## Basic Usage

```python
from streamshape import LiteLLM

# Initialize with provider name
client = LiteLLM(
    api_key="your-api-key",
    provider="openrouter"  # or "anthropic", "openai", "gemini", etc.
)

# Use like any other provider
response = client.generate(
    model="model-name",
    system_prompt="You are helpful.",
    user_prompt="Hello!"
)
```

## Examples

### OpenRouter

```python
from streamshape import LiteLLM

client = LiteLLM(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    provider="openrouter"
)

response = client.generate(
    model="anthropic/claude-3-haiku",
    system_prompt="You are helpful.",
    user_prompt="What is Python?"
)
```

### Anthropic

```python
client = LiteLLM(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    provider="anthropic"
)

response = client.generate(
    model="claude-3-haiku-20240307",
    system_prompt="You are helpful.",
    user_prompt="Hello!"
)
```

### Google Gemini

```python
client = LiteLLM(
    api_key=os.getenv("GOOGLE_API_KEY"),
    provider="gemini"
)

response = client.generate(
    model="gemini-pro",
    system_prompt="You are helpful.",
    user_prompt="Hello!"
)
```

### Custom Base URL (OpenAI-Compatible)

```python
# For Ollama, LM Studio, or other OpenAI-compatible endpoints
client = LiteLLM(
    api_key="any-string",
    provider="openai",
    base_url="http://localhost:11434/v1"
)

response = client.generate(
    model="llama2",
    system_prompt="You are helpful.",
    user_prompt="Hello!"
)
```

## All Methods Supported

The `LiteLLM` class supports all standard methods:

### 1. Generate (Non-Streaming Text)

```python
result = client.generate(
    model="model-name",
    system_prompt="You are helpful.",
    user_prompt="Hello!",
    temperature=0.7
)
print(result["data"])
```

### 2. Stream (Streaming Text)

```python
for chunk in client.stream(
    model="model-name",
    system_prompt="You are helpful.",
    user_prompt="Write a story",
    temperature=0.7
):
    print(chunk["data"], end="", flush=True)
```

### 3. Tool Call (Function Calling)

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
}]

result = client.tool_call(
    model="model-name",
    system_prompt="You are helpful.",
    user_prompt="What's the weather in NYC?",
    tools=tools
)
```

### 4. Structured Output (Non-Streaming)

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

result = client.structured_output(
    model="model-name",
    system_prompt="Generate user data.",
    user_prompt="Create 3 users",
    output_schema=User
)

for user in result["data"]:
    print(f"{user.name}, {user.age}")
```

### 5. Structured Streaming Output

```python
for user in client.structured_streaming_output(
    model="model-name",
    system_prompt="Generate user data.",
    user_prompt="Create 5 users",
    output_schema=User
):
    print(f"{user.name}, {user.age}")
```

## Comparison with Specific Provider Classes

### Using Specific Class
```python
from streamshape import OpenRouter

client = OpenRouter(api_key="...")
response = client.generate(model="model-name", ...)
```

### Using LiteLLM General Class
```python
from streamshape import LiteLLM

client = LiteLLM(api_key="...", provider="openrouter")
response = client.generate(model="model-name", ...)
```

Both approaches work identically. Use specific classes for clarity, or `LiteLLM` for flexibility.

## Supported Providers

The `LiteLLM` class supports all providers that LiteLLM supports:

- `openai` - OpenAI
- `anthropic` - Anthropic (Claude)
- `gemini` - Google Gemini
- `openrouter` - OpenRouter
- `xai` - xAI (Grok)
- `cohere` - Cohere
- `replicate` - Replicate
- `huggingface` - Hugging Face
- `together_ai` - Together AI
- `bedrock` - AWS Bedrock
- `vertex_ai` - Google Vertex AI
- And many more...

See [LiteLLM Providers](https://docs.litellm.ai/docs/providers) for the full list.

## Model Name Format

When using `LiteLLM`, the model name is automatically prefixed with the provider:

```python
# You pass: model="claude-3-haiku"
# LiteLLM receives: "anthropic/claude-3-haiku"
```

If your model already includes the provider prefix, it won't be added again:

```python
# You pass: model="anthropic/claude-3-haiku"
# LiteLLM receives: "anthropic/claude-3-haiku"
```

## Error Handling

```python
from streamshape import LiteLLM
from streamshape.exceptions import APIError, ValidationError

try:
    client = LiteLLM(api_key="...", provider="openrouter")
    result = client.generate(...)
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Best Practices

1. **Use environment variables** for API keys
2. **Validate provider names** before passing to LiteLLM
3. **Handle errors gracefully** with try-except blocks
4. **Check model availability** for your chosen provider
5. **Use specific classes** when you know the provider upfront for better IDE support
