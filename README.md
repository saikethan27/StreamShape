# Unified LLM Interface

A Python package that provides a simple, consistent interface for interacting with multiple Large Language Model (LLM) providers. Write once, run anywhere - switch between OpenAI, Anthropic, Google, and other providers without changing your code.

## Key Features

✨ **5 Output Modes**
- Normal text generation
- Streaming text
- Function calling (tool use)
- Structured output (validated Pydantic objects)
- Streaming structured output

🔌 **6 Supported Providers**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- OpenRouter (100+ models)
- xAI (Grok)
- Any OpenAI-compatible endpoint (Ollama, LM Studio, etc.)

🛡️ **Type-Safe & Validated**
- Full type hints for IDE autocomplete
- Pydantic validation for structured outputs
- Clear, consistent error messages

🎯 **Simple & Consistent**
- Same API across all providers
- Built on battle-tested libraries (LiteLLM, Pydantic)
- Minimal code to get started

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

Or install from source:

```bash
git clone <repository-url>
cd output_parsar
pip install -e .
```

### Basic Usage

```python
from src import OpenAI
from pydantic import BaseModel

# Initialize provider
client = OpenAI(api_key="your-api-key")

# 1. Generate text
response = client.generate(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What is Python?"
)
print(response["data"])

# 2. Stream text
for chunk in client.stream(
    model="gpt-4",
    system_prompt="You are a storyteller.",
    user_prompt="Tell me a short story"
):
    print(chunk["data"], end="", flush=True)

# 3. Structured output
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

### Switch Providers Easily

```python
# Just change the import - same API!

from src import OpenAI
client = OpenAI(api_key="sk-...")

# Or use Anthropic
from src import Anthropic
client = Anthropic(api_key="sk-ant-...")

# Or Google
from src import Google
client = Google(api_key="...")

# Same code works for all providers!
```

## Documentation

📚 **Complete documentation available in the `/docs` folder:**

- **[Quick Start Guide](docs/quickstart.md)** - Get up and running in 5 minutes
- **[Installation Guide](docs/installation.md)** - Detailed installation instructions
- **[Usage Guide](docs/usage.md)** - Comprehensive examples for all methods
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Provider Configuration](docs/providers.md)** - Provider-specific setup
- **[Examples](docs/examples.md)** - Real-world usage examples
- **[Error Handling](docs/error-handling.md)** - Understanding and handling errors
- **[Best Practices](docs/best-practices.md)** - Tips and recommendations

## Five Ways to Use LLMs

### 1. Generate (Complete Text)

```python
response = client.generate(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="Explain quantum computing in simple terms",
    temperature=0.7
)
print(response["data"])
```

### 2. Stream (Real-time Text)

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

```python
from pydantic import BaseModel

class Task(BaseModel):
    title: str
    priority: str
    estimated_hours: int

result = client.structured_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 5 tasks for building a website",
    output_schema=Task
)

for task in result["data"]:
    print(f"Task: {task.title} (Priority: {task.priority})")
```

### 5. Structured Streaming Output

```python
for task in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 10 tasks for building a mobile app",
    output_schema=Task
):
    print(f"New task: {task.title} (Priority: {task.priority})")
```

## Real-World Examples

Check out the `/real_use` directory for complete working examples:

- **[All Methods Usage](real_use/all_methods_usage.py)** - Demonstrates all 5 output modes
- **[Structured Output](real_use/structured_output_usage.py)** - Complete structured output examples
- **[Streaming Structured Output](real_use/streaming_structured_output_usage.py)** - Real-time structured data

## Testing

Run the test suite to verify everything works:

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_normalizer.py
python -m pytest tests/test_base_provider.py
python -m pytest tests/test_streaming_structered_output.py
```

Tests use mock payloads and Hypothesis for property-based testing, so no API calls are made during testing.

## Environment Variables

Store your API keys securely using environment variables:

```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
OPENROUTER_API_KEY=sk-or-...
XAI_API_KEY=...
```

Load them in your code:

```python
import os
from dotenv import load_dotenv
from src import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

## Project Structure

```
output_parsar/
├── src/                          # Main package source code
│   ├── base.py                   # Base provider class
│   ├── providers.py              # Provider implementations
│   ├── exceptions.py             # Custom exceptions
│   ├── litellm_integration.py    # LiteLLM integration
│   ├── parser_integration.py     # Parser integration
│   └── streaming_structured_output_parser/  # Streaming parser
├── docs/                         # Complete documentation
├── tests/                        # Test suite
├── real_use/                     # Real-world examples
├── dummy/                        # Demo scripts
└── requirements.txt              # Dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

- Check the [documentation](docs/README.md) for detailed guides
- Review [examples](docs/examples.md) for common use cases
- See [error handling](docs/error-handling.md) for troubleshooting
- Open an issue on GitHub for bugs or feature requests
