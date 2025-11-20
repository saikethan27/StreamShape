"""
Custom exception classes for the unified LLM interface package.
"""

from typing import Optional


class UnifiedLLMError(Exception):
    """Base exception for all package errors."""
    pass


class ConfigurationError(UnifiedLLMError):
    """Raised when provider configuration is invalid."""
    pass


class ValidationError(UnifiedLLMError):
    """Raised when input validation fails."""
    pass


class APIError(UnifiedLLMError):
    """Raised when the LLM API call fails."""
    
    def __init__(self, message: str, provider: str, original_error: Optional[Exception] = None):
        """
        Initialize APIError with provider context.
        
        Args:
            message: Error message describing what went wrong
            provider: Name of the provider where the error occurred
            original_error: The original exception that was caught
        """
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")


class NetworkError(UnifiedLLMError):
    """Raised when network communication fails."""
    pass


class ParsingError(UnifiedLLMError):
    """Raised when response parsing fails (structured output only)."""
    pass
