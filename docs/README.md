# StreamShape Documentation

Welcome to the StreamShape package documentation! This package provides a simple, consistent interface for interacting with multiple LLM providers.

## Documentation Structure

- **[Quick Start Guide](quickstart.md)** - Get up and running in 5 minutes
- **[Installation Guide](installation.md)** - Detailed installation instructions
- **[Usage Guide](usage.md)** - Comprehensive usage examples for all methods
- **[Output Formats](output-formats.md)** - Complete output structure reference for all methods
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Provider Configuration](providers.md)** - Provider-specific setup and configuration
- **[Examples](examples.md)** - Real-world usage examples
- **[Error Handling](error-handling.md)** - Understanding and handling errors
- **[Best Practices](best-practices.md)** - Tips and recommendations
- **[Migration Guide](MIGRATION_STREAMING_USAGE.md)** - Migrating to new streaming format with usage tracking

## What is StreamShape?

StreamShape is a Python package that provides a simple, consistent API for working with multiple Large Language Model (LLM) providers. Instead of learning different APIs for OpenAI, Anthropic, Google, and others, you can use one unified interface.

## Key Features

✨ **5 Output Modes**
- Normal text generation
- Streaming text
- Function calling (tool use)
- Structured output (validated Pydantic objects)
- Streaming structured output with token usage tracking

🔌 **6 Supported Providers**
- OpenAI
- Google (Gemini)
- Anthropic (Claude)
- OpenRouter
- xAI (Grok)
- Any OpenAI-compatible endpoint

🛡️ **Type-Safe**
- Full type hints for IDE autocomplete
- Pydantic validation for structured outputs
- Clear error messages

🎯 **Simple & Consistent**
- Same API across all providers
- Minimal code to get started
- Built on battle-tested libraries (LiteLLM, Pydantic)

## Quick Example

```python
from streamshape import OpenAI
from pydantic import BaseModel

# Initialize provider
client = OpenAI(api_key="your-api-key")

# Generate text
response = client.generate(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What is Python?"
)
print(response)

# Structured output
class Joke(BaseModel):
    setup: str
    punchline: str

jokes = client.structured_output(
    model="gpt-4",
    system_prompt="You are a comedian.",
    user_prompt="Tell me 3 jokes about programming",
    output_schema=Joke
)

for joke in jokes:
    print(f"{joke.setup}\n{joke.punchline}\n")
```

## Getting Started

👉 **New users**: Start with the [Quick Start Guide](quickstart.md)

👉 **Experienced users**: Jump to the [Usage Guide](usage.md) or [API Reference](api-reference.md)

## Need Help?

- Check the [Examples](examples.md) for common use cases
- Review [Error Handling](error-handling.md) if you encounter issues
- See [Best Practices](best-practices.md) for optimization tips

## License

This package is open source and available under the MIT License.

