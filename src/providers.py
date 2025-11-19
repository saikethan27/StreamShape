"""
Provider-specific classes for different LLM services.
"""

from src.base import BaseLLMProvider


class OpenAI(BaseLLMProvider):
    """OpenAI provider client."""
    
    def _get_provider_name(self) -> str:
        return "openai"


class Google(BaseLLMProvider):
    """Google (Gemini) provider client."""
    
    def _get_provider_name(self) -> str:
        return "gemini"


class Anthropic(BaseLLMProvider):
    """Anthropic (Claude) provider client."""
    
    def _get_provider_name(self) -> str:
        return "anthropic"


class OpenRouter(BaseLLMProvider):
    """OpenRouter provider client."""
    
    def _get_provider_name(self) -> str:
        return "openrouter"


class XAI(BaseLLMProvider):
    """xAI (Grok) provider client."""
    
    def _get_provider_name(self) -> str:
        return "xai"


class OpenAICompatible(BaseLLMProvider):
    """OpenAI-compatible endpoint provider client."""
    
    def __init__(self, api_key: str, base_url: str, **kwargs):
        """
        Initialize OpenAI-compatible provider with custom base URL.
        
        Args:
            api_key: API key for the endpoint
            base_url: Base URL for the OpenAI-compatible endpoint
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.base_url = base_url
    
    def _get_provider_name(self) -> str:
        return "openai"
