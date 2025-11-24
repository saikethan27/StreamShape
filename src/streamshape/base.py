"""
Base provider class with shared logic for all LLM providers.
"""

from typing import Any, Dict, Iterator, List, Optional, Type
from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseLLMProvider(ABC):
    """
    Base class for all LLM provider clients.
    
    Provides a unified interface for interacting with different LLM providers
    through four output modes: generate, stream, tool_call, and structured_streaming_output.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the provider with credentials.
        
        Args:
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.extra_config = kwargs
    
    @abstractmethod
    def _get_provider_name(self) -> str:
        """
        Return the provider identifier for LiteLLM.
        
        Returns:
            Provider name string (e.g., "openai", "anthropic", "gemini")
        """
        pass
    
    def __repr__(self) -> str:
        """Return string representation without exposing credentials."""
        return f"{self.__class__.__name__}(provider={self._get_provider_name()})"
    
    def __str__(self) -> str:
        """Return string representation without exposing credentials."""
        return self.__repr__()
    
    def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate complete text response (non-streaming).
        
        Args:
            model: Model identifier (e.g., "gpt-4", "claude-3-opus")
            system_prompt: Instructions that define the LLM's behavior
            user_prompt: The actual query or request
            **kwargs: Optional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Dictionary with "data" (text content) and "raw_chunks" (raw response object) keys
        
        Raises:
            ValidationError: When required parameters are missing or invalid
        """
        from .exceptions import ValidationError
        
        # Validate required parameters
        if not model:
            raise ValidationError("Parameter 'model' is required and cannot be empty")
        if not system_prompt:
            raise ValidationError("Parameter 'system_prompt' is required and cannot be empty")
        if not user_prompt:
            raise ValidationError("Parameter 'user_prompt' is required and cannot be empty")
        
        # Build messages using helper method
        messages = self._build_messages(system_prompt, user_prompt)
        
        # Call LiteLLM with stream=False
        response = self._call_litellm(
            model=model,
            messages=messages,
            stream=False,
            **kwargs
        )
        
        # Extract and return structured response
        return {
            "data": response.choices[0].message.content,
            "raw_chunks": response
        }
    
    def stream(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream text chunks as they arrive.
        
        Args:
            model: Model identifier
            system_prompt: Instructions that define the LLM's behavior
            user_prompt: The actual query or request
            **kwargs: Optional parameters (temperature, max_tokens, etc.)
        
        Yields:
            Dictionary with "data" (text content) and "raw_chunks" (raw chunk object) keys.
            Final chunk has empty "data" field.
        
        Raises:
            ValidationError: When required parameters are missing or invalid
        """
        from .exceptions import ValidationError
        
        # Validate required parameters
        if not model:
            raise ValidationError("Parameter 'model' is required and cannot be empty")
        if not system_prompt:
            raise ValidationError("Parameter 'system_prompt' is required and cannot be empty")
        if not user_prompt:
            raise ValidationError("Parameter 'user_prompt' is required and cannot be empty")
        
        # Build messages using helper method
        messages = self._build_messages(system_prompt, user_prompt)
        
        # Call LiteLLM with stream=True
        response = self._call_litellm(
            model=model,
            messages=messages,
            stream=True,
            **kwargs
        )
        
        # Iterate over response chunks and yield structured data
        for chunk in response:
            # Extract delta content from the chunk
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                content = delta.content if hasattr(delta, 'content') and delta.content is not None else ""
                
                yield {
                    "data": content,
                    "raw_chunks": chunk
                }
    
    def tool_call(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        tools: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute function calling with tool definitions.
        
        Args:
            model: Model identifier
            system_prompt: Instructions that define the LLM's behavior
            user_prompt: The actual query or request
            tools: List of tool definitions in OpenAI format
            **kwargs: Optional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Dictionary with "data" (containing "tool_name" and "arguments") and "raw_chunks" keys
        
        Raises:
            ValidationError: When required parameters are missing or invalid
        """
        from .exceptions import ValidationError
        
        # Validate required parameters
        if not model:
            raise ValidationError("Parameter 'model' is required and cannot be empty")
        if not system_prompt:
            raise ValidationError("Parameter 'system_prompt' is required and cannot be empty")
        if not user_prompt:
            raise ValidationError("Parameter 'user_prompt' is required and cannot be empty")
        if tools is None:
            raise ValidationError("Parameter 'tools' is required")
        
        # Validate tools parameter is a list
        if not isinstance(tools, list):
            raise ValidationError("Parameter 'tools' must be a list of tool definitions")
        
        # Build messages using helper method
        messages = self._build_messages(system_prompt, user_prompt)
        
        # Call LiteLLM with tools parameter
        response = self._call_litellm(
            model=model,
            messages=messages,
            stream=False,
            tools=tools,
            **kwargs
        )
        
        # Extract tool call information
        tool_calls = response.choices[0].message.tool_calls
        tool_data = {
            "tool_name": None,
            "arguments": None
        }
        
        if tool_calls and len(tool_calls) > 0:
            tool_call = tool_calls[0]
            tool_data = {
                "tool_name": tool_call.function.name,
                "arguments": tool_call.function.arguments
            }
        
        # Return structured response
        return {
            "data": tool_data,
            "raw_chunks": response
        }
    
    def structured_output(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        output_schema: Type[BaseModel],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate complete list of validated Pydantic objects (non-streaming).
        
        Args:
            model: Model identifier
            system_prompt: Instructions that define the LLM's behavior
            user_prompt: The actual query or request
            output_schema: Pydantic BaseModel class defining expected structure
            **kwargs: Optional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Dictionary with "data" (list of validated Pydantic objects) and "raw_chunks" keys
        
        Raises:
            ValidationError: When required parameters are missing or invalid
        """
        from .exceptions import ValidationError
        import json
        
        # Validate required parameters
        if not model:
            raise ValidationError("Parameter 'model' is required and cannot be empty")
        if not system_prompt:
            raise ValidationError("Parameter 'system_prompt' is required and cannot be empty")
        if not user_prompt:
            raise ValidationError("Parameter 'user_prompt' is required and cannot be empty")
        if output_schema is None:
            raise ValidationError("Parameter 'output_schema' is required")
        
        # Validate output_schema is a Pydantic BaseModel class
        if not (isinstance(output_schema, type) and issubclass(output_schema, BaseModel)):
            raise ValidationError("Parameter 'output_schema' must be a Pydantic BaseModel class")
        
        # Augment user_prompt with JSON output instructions
        augmented_prompt = f"{user_prompt}\n\nOutput only the JSON array, nothing else."
        
        # Build response_format using helper method
        response_format = self._build_response_format(output_schema)
        
        # Build messages using helper method
        messages = self._build_messages(system_prompt, augmented_prompt)
        
        # Call LiteLLM with stream=False and response_format
        response = self._call_litellm(
            model=model,
            messages=messages,
            stream=False,
            response_format=response_format,
            **kwargs
        )
        
        # Extract JSON content from response
        content = response.choices[0].message.content
        
        # Parse JSON array and validate each object
        try:
            data = json.loads(content)
            if not isinstance(data, list):
                raise ValidationError("Response must be a JSON array")
            
            # Validate and convert each item to Pydantic object
            validated_objects = []
            for item in data:
                validated_obj = output_schema.model_validate(item)
                validated_objects.append(validated_obj)
            
            return {
                "data": validated_objects,
                "raw_chunks": response
            }
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Failed to validate response: {str(e)}")
    
    def structured_streaming_output(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        output_schema: Type[BaseModel],
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream validated Pydantic objects with usage data.
        
        Args:
            model: Model identifier
            system_prompt: Instructions that define the LLM's behavior
            user_prompt: The actual query or request
            output_schema: Pydantic BaseModel class defining expected structure
            **kwargs: Optional parameters (temperature, max_tokens, etc.)
        
        Yields:
            Dictionary with keys:
            - data: Validated Pydantic object (or None for final chunk)
            - usage: Token usage statistics (dict, may be empty until final chunk)
            - finished: Boolean indicating if this is the final chunk
            - raw_chunks: List of raw response chunks (only in final chunk)
        
        Raises:
            ValidationError: When required parameters are missing or invalid
        """
        from .exceptions import ValidationError
        from .parser_integration import parse_streaming_response
        
        # Validate required parameters
        if not model:
            raise ValidationError("Parameter 'model' is required and cannot be empty")
        if not system_prompt:
            raise ValidationError("Parameter 'system_prompt' is required and cannot be empty")
        if not user_prompt:
            raise ValidationError("Parameter 'user_prompt' is required and cannot be empty")
        if output_schema is None:
            raise ValidationError("Parameter 'output_schema' is required")
        
        # Validate output_schema is a Pydantic BaseModel class
        if not (isinstance(output_schema, type) and issubclass(output_schema, BaseModel)):
            raise ValidationError("Parameter 'output_schema' must be a Pydantic BaseModel class")
        
        # Augment user_prompt with JSON output instructions
        augmented_prompt = f"{user_prompt}\n\nOutput only the JSON array, nothing else."
        
        # Build response_format using helper method
        response_format = self._build_response_format(output_schema)
        
        # Build messages using helper method
        messages = self._build_messages(system_prompt, augmented_prompt)
        
        # Call LiteLLM with stream=True and response_format
        response = self._call_litellm(
            model=model,
            messages=messages,
            stream=True,
            response_format=response_format,
            **kwargs
        )
        
        # Pass response to parser_integration module and yield result dictionaries
        # Each result contains: data (BaseModel or None), usage (dict), finished (bool)
        yield from parse_streaming_response(response, output_schema)
    
    def _build_messages(self, system_prompt: str, user_prompt: str) -> List[Dict]:
        """
        Construct message array in OpenAI format.
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
        
        Returns:
            List of message dictionaries
        """
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _build_response_format(self, output_schema: Type[BaseModel]) -> Dict:
        """
        Convert Pydantic schema to JSON schema format for LiteLLM.
        
        Args:
            output_schema: Pydantic BaseModel class
        
        Returns:
            Response format dictionary for LiteLLM
        """
        # Get the schema with ref_template='#/items/$defs/{model}' to fix nested references
        # This ensures $ref paths work correctly when schema is wrapped in array
        schema = output_schema.model_json_schema(ref_template='#/items/$defs/{model}')
        
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "response_schema",
                "strict": False,
                "schema": {
                    "type": "array",
                    "items": schema
                }
            }
        }
    
    def _call_litellm(
        self,
        model: str,
        messages: List[Dict],
        stream: bool,
        response_format: Optional[Dict] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Any:
        """
        Make the LiteLLM API call.
        
        Args:
            model: Model identifier
            messages: Message array
            stream: Whether to stream the response
            response_format: Optional response format for structured output
            tools: Optional tool definitions for function calling
            **kwargs: Additional parameters
        
        Returns:
            LiteLLM response object
        """
        from .litellm_integration import call_litellm
        
        # Get base_url if this is an OpenAI-compatible provider
        base_url = getattr(self, 'base_url', None)
        
        # Merge extra_config with kwargs
        merged_kwargs = {**self.extra_config, **kwargs}
        
        # Add stream_options to include usage data when streaming
        if stream and 'stream_options' not in merged_kwargs:
            merged_kwargs['stream_options'] = {"include_usage": True}
        
        return call_litellm(
            provider=self._get_provider_name(),
            model=model,
            messages=messages,
            api_key=self.api_key,
            stream=stream,
            response_format=response_format,
            tools=tools,
            base_url=base_url,
            **merged_kwargs
        )
