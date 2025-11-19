# API Reference

Complete API documentation for Unified LLM Interface.

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
from src import OpenAI

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
from src import Anthropic

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
from src import Google

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
from src import OpenRouter

client = OpenRouter(api_key: str, **kwargs)
```

**Parameters:**
- `api_key` (str, required): OpenRouter API key
- `**kwargs`: Additional configuration options

**Supported Models:** All models available on OpenRouter

### XAI

```python
from src import XAI

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
from src import OpenAICompatible

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

