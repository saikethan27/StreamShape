"""
Parser integration module for structured streaming output.

Integrates with the existing parser module to parse streaming JSON
responses into validated Pydantic objects.
"""

from typing import Any, Iterator, Type
from pydantic import BaseModel


def parse_streaming_response(
    response: Any,
    output_schema: Type[BaseModel]
) -> Iterator[BaseModel]:
    """
    Delegate to existing parser module for structured output parsing.
    
    Always uses "openai_lib" as request_type for LiteLLM responses since
    LiteLLM returns OpenAI SDK-compatible response objects.
    
    Args:
        response: LiteLLM streaming response object
        output_schema: Pydantic BaseModel class for validation
    
    Yields:
        Validated Pydantic objects
    
    Raises:
        ParsingError: When parsing or validation fails
    """
    from src.streaming_structured_output_parser.parse_llm_output import read_tokens
    
    # Always use "openai_lib" as request_type for LiteLLM responses
    # Yield objects from read_tokens unchanged
    yield from read_tokens(response, output_schema, "openai_lib")
