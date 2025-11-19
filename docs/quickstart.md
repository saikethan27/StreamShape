# Quick Start Guide

Get started with Unified LLM Interface in 5 minutes!

## Installation

```bash
pip install unified-llm-interface
```

Or install from source:

```bash
git clone https://github.com/yourusername/unified-llm-interface.git
cd unified-llm-interface
pip install -e .
```

## Basic Setup

### 1. Get Your API Key

Choose a provider and get an API key:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google**: https://makersuite.google.com/app/apikey
- **OpenRouter**: https://openrouter.ai/keys
- **xAI**: https://console.x.ai/

### 2. Initialize a Provider

```python
from src import OpenAI

# Initialize with your API key
client = OpenAI(api_key="your-api-key-here")
```

### 3. Generate Text

```python
# Simple text generation
response = client.generate(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="Explain what Python is in one sentence."
)

print(response["data"])
# Output: Python is a high-level, interpreted programming language...
```

## Five Ways to Use LLMs

### 1. Generate (Complete Text)

Get a complete response all at once:

```python
response = client.generate(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="Write a haiku about coding",
    temperature=0.7
)
print(response["data"])
```

### 2. Stream (Real-time Text)

Get text as it's generated:

```python
for chunk in client.stream(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="Write a short story",
    temperature=0.7
):
    print(chunk["data"], end="", flush=True)
```

### 3. Tool Call (Function Calling)

Let the LLM call functions:

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
            }
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
print(result["data"]["arguments"])    # {"location": "Paris"}
```

### 4. Structured Output (Complete)

Get validated data objects all at once:

```python
from pydantic import BaseModel

class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    steps: list[str]

result = client.structured_output(
    model="gpt-4",
    system_prompt="You are a chef.",
    user_prompt="Give me 2 simple pasta recipes",
    output_schema=Recipe
)

for recipe in result["data"]:
    print(f"Recipe: {recipe.name}")
    print(f"Ingredients: {', '.join(recipe.ingredients)}")
```

### 5. Structured Streaming Output

Get validated data objects as they're generated:

```python
from pydantic import BaseModel

class Task(BaseModel):
    title: str
    priority: str
    estimated_hours: int

for task in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 5 tasks for building a website",
    output_schema=Task
):
    print(f"New task: {task.title} (Priority: {task.priority})")
```

## Using Different Providers

Switch providers by changing the import:

```python
# OpenAI
from src import OpenAI
client = OpenAI(api_key="sk-...")

# Anthropic
from src import Anthropic
client = Anthropic(api_key="sk-ant-...")

# Google
from src import Google
client = Google(api_key="...")

# OpenRouter
from src import OpenRouter
client = OpenRouter(api_key="sk-or-...")

# xAI
from src import XAI
client = XAI(api_key="...")

# OpenAI-compatible (e.g., local models)
from src import OpenAICompatible
client = OpenAICompatible(
    api_key="...",
    base_url="http://localhost:8000/v1"
)
```

**The API is identical across all providers!** Just change the model name.

## Common Parameters

All methods accept these optional parameters:

```python
client.generate(
    model="gpt-4",
    system_prompt="...",
    user_prompt="...",
    
    # Optional parameters
    temperature=0.7,        # Creativity (0.0 - 2.0)
    max_tokens=1000,        # Maximum response length
    top_p=0.9,             # Nucleus sampling
    frequency_penalty=0.0,  # Reduce repetition
    presence_penalty=0.0,   # Encourage new topics
)
```

## Environment Variables

Store API keys securely using environment variables:

```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

```python
import os
from dotenv import load_dotenv
from src import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

## Next Steps

🎯 **Ready for more?** Check out the [Usage Guide](usage.md) for detailed examples

📚 **Need reference?** See the [API Reference](api-reference.md) for complete documentation

💡 **Want examples?** Browse [Examples](examples.md) for real-world use cases

## Common Issues

### ModuleNotFoundError

```bash
pip install unified-llm-interface
```

### Authentication Error

Check that your API key is correct and has the right permissions.

### Model Not Found

Verify the model name is correct for your provider:
- OpenAI: `gpt-4`, `gpt-3.5-turbo`
- Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- Google: `gemini-pro`, `gemini-1.5-pro`

See [Provider Configuration](providers.md) for complete model lists.
