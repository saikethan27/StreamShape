"""
Unified LLM Interface Package

A simple, consistent interface for interacting with multiple LLM providers.
Supports OpenAI, Google, Anthropic, OpenRouter, xAI, and OpenAI-compatible endpoints.
"""

from streamshape.providers import (
    OpenAI,
    Google,
    Anthropic,
    OpenRouter,
    XAI,
    OpenAICompatible,
)
from streamshape.exceptions import (
    UnifiedLLMError,
    ConfigurationError,
    ValidationError,
    APIError,
    NetworkError,
    ParsingError,
)

__all__ = [
    "OpenAI",
    "Google",
    "Anthropic",
    "OpenRouter",
    "XAI",
    "OpenAICompatible",
    "UnifiedLLMError",
    "ConfigurationError",
    "ValidationError",
    "APIError",
    "NetworkError",
    "ParsingError",
]

__version__ = "0.1.0"
