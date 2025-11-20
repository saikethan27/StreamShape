"""
LiteLLM integration module for making API calls to LLM providers.
"""

from typing import Any, Dict, List, Optional
import litellm


def call_litellm(
    provider: str,
    model: str,
    messages: List[Dict],
    api_key: str,
    stream: bool,
    response_format: Optional[Dict] = None,
    tools: Optional[List[Dict]] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Call LiteLLM with appropriate configuration.
    
    Args:
        provider: Provider identifier (e.g., "openai", "anthropic")
        model: Model identifier
        messages: Message array in OpenAI format
        api_key: API key for authentication
        stream: Whether to stream the response
        response_format: Optional response format for structured output
        tools: Optional tool definitions for function calling
        base_url: Optional custom base URL for OpenAI-compatible endpoints
        **kwargs: Additional parameters to pass to LiteLLM
    
    Returns:
        LiteLLM response object (streaming or complete)
    
    Raises:
        APIError: When the API call fails
        NetworkError: When network communication fails
    """
    from .exceptions import APIError, NetworkError
    
    try:
        # Build the full model name with provider prefix
        # When using custom base_url (OpenAI-compatible), always use openai/ prefix
        if base_url is not None:
            # Custom base URL means OpenAI-compatible endpoint
            if not model.startswith("openai/"):
                full_model = f"openai/{model}"
            else:
                full_model = model
        elif provider == "openai" and not model.startswith("openai/"):
            full_model = model  # OpenAI models don't need prefix when using official API
        elif provider == "openrouter":
            # OpenRouter requires openrouter/ prefix
            if not model.startswith("openrouter/"):
                full_model = f"openrouter/{model}"
            else:
                full_model = model
        elif "/" not in model:
            full_model = f"{provider}/{model}"
        else:
            full_model = model
        
        # Build parameters for LiteLLM
        params = {
            "model": full_model,
            "messages": messages,
            "api_key": api_key,
            "stream": stream,
            **kwargs
        }
        
        # Add optional parameters if provided
        if response_format is not None:
            params["response_format"] = response_format
        
        if tools is not None:
            params["tools"] = tools
        
        if base_url is not None:
            params["api_base"] = base_url  # LiteLLM uses api_base, not base_url
        
        # Make the LiteLLM API call
        response = litellm.completion(**params)
        
        return response
        
    except litellm.AuthenticationError as e:
        raise APIError(
            f"Authentication failed: {str(e)}",
            provider=provider,
            original_error=e
        )
    except litellm.RateLimitError as e:
        raise APIError(
            f"Rate limit exceeded: {str(e)}",
            provider=provider,
            original_error=e
        )
    except litellm.BadRequestError as e:
        raise APIError(
            f"Bad request: {str(e)}",
            provider=provider,
            original_error=e
        )
    except (ConnectionError, TimeoutError) as e:
        raise NetworkError(f"Network error: {str(e)}")
    except Exception as e:
        raise APIError(
            f"API call failed: {str(e)}",
            provider=provider,
            original_error=e
        )
