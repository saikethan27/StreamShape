"""
Property-based tests for BaseLLMProvider.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch
from hypothesis import given, settings, strategies as st, HealthCheck
from pydantic import BaseModel
from streamshape.base import BaseLLMProvider
from streamshape.exceptions import ValidationError


class ConcreteProvider(BaseLLMProvider):
    """Concrete implementation for testing."""
    def _get_provider_name(self) -> str:
        return "test_provider"


# Feature: unified-llm-interface, Property 1: Provider instantiation stores credentials
@given(
    api_key=st.text(min_size=1, max_size=100),
    extra_params=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False), st.booleans()),
        max_size=5
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_provider_instantiation_stores_credentials(api_key: str, extra_params: dict):
    """
    Property 1: Provider instantiation stores credentials
    For any provider class and any valid API key string, instantiating the provider 
    should create an instance that stores the API key and can be used for subsequent calls.
    
    Validates: Requirements 1.2
    """
    # Create provider instance
    provider = ConcreteProvider(api_key, **extra_params)
    
    # Verify API key is stored
    assert provider.api_key == api_key, "API key should be stored correctly"
    
    # Verify extra config is stored
    assert provider.extra_config == extra_params, "Extra config should be stored correctly"
    
    # Verify provider name is accessible
    assert provider._get_provider_name() == "test_provider", "Provider name should be accessible"



# Feature: unified-llm-interface, Property 2: Credentials are not exposed
@given(
    api_key=st.text(
        min_size=10,  # Avoid short strings that might coincidentally appear
        max_size=100,
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))  # Avoid control characters
    )
)
@settings(max_examples=100)
def test_credentials_are_not_exposed(api_key: str):
    """
    Property 2: Credentials are not exposed
    For any provider instance with an API key, the string representation and any 
    error messages should not contain the actual API key value.
    
    Validates: Requirements 1.5
    """
    # Create provider instance
    provider = ConcreteProvider(api_key)
    
    # Get string representations
    repr_str = repr(provider)
    str_str = str(provider)
    
    # Verify API key is not exposed in repr
    # Only check if the API key is long enough to be meaningful (avoid false positives)
    if len(api_key) >= 10:
        assert api_key not in repr_str, f"API key should not be exposed in repr(): {repr_str}"
        assert api_key not in str_str, f"API key should not be exposed in str(): {str_str}"
    
    # Verify the representations are meaningful (contain provider info)
    assert "ConcreteProvider" in repr_str or "test_provider" in repr_str, \
        "repr should contain provider information"



# Unit tests for generate method
def test_generate_validates_required_parameters():
    """Test that generate validates required parameters."""
    provider = ConcreteProvider("test_api_key")
    
    # Test missing model
    with pytest.raises(ValidationError, match="model"):
        provider.generate("", "system", "user")
    
    # Test missing system_prompt
    with pytest.raises(ValidationError, match="system_prompt"):
        provider.generate("gpt-4", "", "user")
    
    # Test missing user_prompt
    with pytest.raises(ValidationError, match="user_prompt"):
        provider.generate("gpt-4", "system", "")


@patch('streamshape.litellm_integration.litellm.completion')
def test_generate_returns_complete_text(mock_completion):
    """Test that generate returns complete text response."""
    # Mock the LiteLLM response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "This is the complete response"
    mock_completion.return_value = mock_response
    
    # Create provider and call generate
    provider = ConcreteProvider("test_api_key")
    result = provider.generate(
        model="gpt-4",
        system_prompt="You are a helpful assistant",
        user_prompt="Hello, world!"
    )
    
    # Verify the result structure
    assert isinstance(result, dict)
    assert "data" in result
    assert "raw_chunks" in result
    assert result["data"] == "This is the complete response"
    assert result["raw_chunks"] == mock_response
    
    # Verify LiteLLM was called correctly
    mock_completion.assert_called_once()
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["model"] == "test_provider/gpt-4"
    assert call_kwargs["stream"] is False
    assert len(call_kwargs["messages"]) == 2
    assert call_kwargs["messages"][0]["role"] == "system"
    assert call_kwargs["messages"][1]["role"] == "user"


@patch('streamshape.litellm_integration.litellm.completion')
def test_generate_forwards_optional_parameters(mock_completion):
    """Test that generate forwards optional parameters to LiteLLM."""
    # Mock the LiteLLM response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Response"
    mock_completion.return_value = mock_response
    
    # Create provider and call generate with optional params
    provider = ConcreteProvider("test_api_key")
    result = provider.generate(
        model="gpt-4",
        system_prompt="System",
        user_prompt="User",
        temperature=0.7,
        max_tokens=100,
        top_p=0.9
    )
    
    # Verify optional parameters were forwarded
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["temperature"] == 0.7
    assert call_kwargs["max_tokens"] == 100
    assert call_kwargs["top_p"] == 0.9



# Unit tests for stream method
def test_stream_validates_required_parameters():
    """Test that stream validates required parameters."""
    provider = ConcreteProvider("test_api_key")
    
    # Test missing model
    with pytest.raises(ValidationError, match="model"):
        list(provider.stream("", "system", "user"))
    
    # Test missing system_prompt
    with pytest.raises(ValidationError, match="system_prompt"):
        list(provider.stream("gpt-4", "", "user"))
    
    # Test missing user_prompt
    with pytest.raises(ValidationError, match="user_prompt"):
        list(provider.stream("gpt-4", "system", ""))


@patch('streamshape.litellm_integration.litellm.completion')
def test_stream_yields_text_chunks(mock_completion):
    """Test that stream yields text chunks as they arrive."""
    # Mock the LiteLLM streaming response
    mock_chunk1 = Mock()
    mock_chunk1.choices = [Mock()]
    mock_chunk1.choices[0].delta = Mock()
    mock_chunk1.choices[0].delta.content = "Hello"
    
    mock_chunk2 = Mock()
    mock_chunk2.choices = [Mock()]
    mock_chunk2.choices[0].delta = Mock()
    mock_chunk2.choices[0].delta.content = " world"
    
    mock_chunk3 = Mock()
    mock_chunk3.choices = [Mock()]
    mock_chunk3.choices[0].delta = Mock()
    mock_chunk3.choices[0].delta.content = "!"
    
    mock_completion.return_value = iter([mock_chunk1, mock_chunk2, mock_chunk3])
    
    # Create provider and call stream
    provider = ConcreteProvider("test_api_key")
    chunks = list(provider.stream(
        model="gpt-4",
        system_prompt="You are a helpful assistant",
        user_prompt="Say hello"
    ))
    
    # Verify the chunks structure
    assert len(chunks) == 3
    assert all(isinstance(chunk, dict) for chunk in chunks)
    assert all("data" in chunk and "raw_chunks" in chunk for chunk in chunks)
    assert chunks[0]["data"] == "Hello"
    assert chunks[1]["data"] == " world"
    assert chunks[2]["data"] == "!"
    assert chunks[0]["raw_chunks"] == mock_chunk1
    assert chunks[1]["raw_chunks"] == mock_chunk2
    assert chunks[2]["raw_chunks"] == mock_chunk3
    
    # Verify LiteLLM was called correctly
    mock_completion.assert_called_once()
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["model"] == "test_provider/gpt-4"
    assert call_kwargs["stream"] is True
    assert len(call_kwargs["messages"]) == 2


@patch('streamshape.litellm_integration.litellm.completion')
def test_stream_forwards_optional_parameters(mock_completion):
    """Test that stream forwards optional parameters to LiteLLM."""
    # Mock the LiteLLM streaming response
    mock_chunk = Mock()
    mock_chunk.choices = [Mock()]
    mock_chunk.choices[0].delta = Mock()
    mock_chunk.choices[0].delta.content = "Response"
    
    mock_completion.return_value = iter([mock_chunk])
    
    # Create provider and call stream with optional params
    provider = ConcreteProvider("test_api_key")
    chunks = list(provider.stream(
        model="gpt-4",
        system_prompt="System",
        user_prompt="User",
        temperature=0.7,
        max_tokens=100,
        top_p=0.9
    ))
    
    # Verify optional parameters were forwarded
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["temperature"] == 0.7
    assert call_kwargs["max_tokens"] == 100
    assert call_kwargs["top_p"] == 0.9


@patch('streamshape.litellm_integration.litellm.completion')
def test_stream_handles_empty_content(mock_completion):
    """Test that stream handles chunks with None content."""
    # Mock chunks with some having None content
    mock_chunk1 = Mock()
    mock_chunk1.choices = [Mock()]
    mock_chunk1.choices[0].delta = Mock()
    mock_chunk1.choices[0].delta.content = "Hello"
    
    mock_chunk2 = Mock()
    mock_chunk2.choices = [Mock()]
    mock_chunk2.choices[0].delta = Mock()
    mock_chunk2.choices[0].delta.content = None  # Empty content
    
    mock_chunk3 = Mock()
    mock_chunk3.choices = [Mock()]
    mock_chunk3.choices[0].delta = Mock()
    mock_chunk3.choices[0].delta.content = " world"
    
    mock_completion.return_value = iter([mock_chunk1, mock_chunk2, mock_chunk3])
    
    # Create provider and call stream
    provider = ConcreteProvider("test_api_key")
    chunks = list(provider.stream(
        model="gpt-4",
        system_prompt="System",
        user_prompt="User"
    ))
    
    # Verify all chunks are yielded with proper structure
    assert len(chunks) == 3
    assert chunks[0]["data"] == "Hello"
    assert chunks[1]["data"] == ""  # None content becomes empty string
    assert chunks[2]["data"] == " world"



# Unit tests for tool_call method
def test_tool_call_validates_required_parameters():
    """Test that tool_call validates required parameters."""
    provider = ConcreteProvider("test_api_key")
    tools = [{"type": "function", "function": {"name": "test"}}]
    
    # Test missing model
    with pytest.raises(ValidationError, match="model"):
        provider.tool_call("", "system", "user", tools)
    
    # Test missing system_prompt
    with pytest.raises(ValidationError, match="system_prompt"):
        provider.tool_call("gpt-4", "", "user", tools)
    
    # Test missing user_prompt
    with pytest.raises(ValidationError, match="user_prompt"):
        provider.tool_call("gpt-4", "system", "", tools)
    
    # Test missing tools
    with pytest.raises(ValidationError, match="tools"):
        provider.tool_call("gpt-4", "system", "user", None)


def test_tool_call_validates_tools_is_list():
    """Test that tool_call validates tools parameter is a list."""
    provider = ConcreteProvider("test_api_key")
    
    # Test tools is not a list
    with pytest.raises(ValidationError, match="must be a list"):
        provider.tool_call("gpt-4", "system", "user", "not a list")
    
    with pytest.raises(ValidationError, match="must be a list"):
        provider.tool_call("gpt-4", "system", "user", {"type": "function"})


@patch('streamshape.litellm_integration.litellm.completion')
def test_tool_call_returns_tool_name_and_arguments(mock_completion):
    """Test that tool_call returns tool name and arguments."""
    # Mock the LiteLLM response with tool call
    mock_tool_call = Mock()
    mock_tool_call.function = Mock()
    mock_tool_call.function.name = "get_weather"
    mock_tool_call.function.arguments = '{"location": "San Francisco"}'
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.tool_calls = [mock_tool_call]
    mock_completion.return_value = mock_response
    
    # Create provider and call tool_call
    provider = ConcreteProvider("test_api_key")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather",
                "parameters": {"type": "object", "properties": {}}
            }
        }
    ]
    result = provider.tool_call(
        model="gpt-4",
        system_prompt="You are a helpful assistant",
        user_prompt="What's the weather?",
        tools=tools
    )
    
    # Verify the result structure
    assert isinstance(result, dict)
    assert "data" in result
    assert "raw_chunks" in result
    assert result["data"]["tool_name"] == "get_weather"
    assert result["data"]["arguments"] == '{"location": "San Francisco"}'
    assert result["raw_chunks"] == mock_response
    
    # Verify LiteLLM was called correctly
    mock_completion.assert_called_once()
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["model"] == "test_provider/gpt-4"
    assert call_kwargs["stream"] is False
    assert call_kwargs["tools"] == tools


@patch('streamshape.litellm_integration.litellm.completion')
def test_tool_call_forwards_optional_parameters(mock_completion):
    """Test that tool_call forwards optional parameters to LiteLLM."""
    # Mock the LiteLLM response
    mock_tool_call = Mock()
    mock_tool_call.function = Mock()
    mock_tool_call.function.name = "test_tool"
    mock_tool_call.function.arguments = '{}'
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.tool_calls = [mock_tool_call]
    mock_completion.return_value = mock_response
    
    # Create provider and call tool_call with optional params
    provider = ConcreteProvider("test_api_key")
    tools = [{"type": "function", "function": {"name": "test_tool"}}]
    result = provider.tool_call(
        model="gpt-4",
        system_prompt="System",
        user_prompt="User",
        tools=tools,
        temperature=0.7,
        max_tokens=100
    )
    
    # Verify optional parameters were forwarded
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["temperature"] == 0.7
    assert call_kwargs["max_tokens"] == 100


@patch('streamshape.litellm_integration.litellm.completion')
def test_tool_call_handles_no_tool_calls(mock_completion):
    """Test that tool_call handles responses with no tool calls."""
    # Mock the LiteLLM response with no tool calls
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.tool_calls = None
    mock_completion.return_value = mock_response
    
    # Create provider and call tool_call
    provider = ConcreteProvider("test_api_key")
    tools = [{"type": "function", "function": {"name": "test_tool"}}]
    result = provider.tool_call(
        model="gpt-4",
        system_prompt="System",
        user_prompt="User",
        tools=tools
    )
    
    # Verify the result structure with None values
    assert isinstance(result, dict)
    assert "data" in result
    assert "raw_chunks" in result
    assert result["data"]["tool_name"] is None
    assert result["data"]["arguments"] is None
    assert result["raw_chunks"] == mock_response



# Unit tests for structured_streaming_output method
class SampleSchema(BaseModel):
    """Sample schema for structured output tests."""
    name: str
    value: int


def test_structured_streaming_output_validates_required_parameters():
    """Test that structured_streaming_output validates required parameters."""
    provider = ConcreteProvider("test_api_key")
    
    # Test missing model
    with pytest.raises(ValidationError, match="model"):
        list(provider.structured_streaming_output("", "system", "user", SampleSchema))
    
    # Test missing system_prompt
    with pytest.raises(ValidationError, match="system_prompt"):
        list(provider.structured_streaming_output("gpt-4", "", "user", SampleSchema))
    
    # Test missing user_prompt
    with pytest.raises(ValidationError, match="user_prompt"):
        list(provider.structured_streaming_output("gpt-4", "system", "", SampleSchema))
    
    # Test missing output_schema
    with pytest.raises(ValidationError, match="output_schema"):
        list(provider.structured_streaming_output("gpt-4", "system", "user", None))


def test_structured_streaming_output_validates_schema_is_basemodel():
    """Test that structured_streaming_output validates output_schema is a BaseModel."""
    provider = ConcreteProvider("test_api_key")
    
    # Test with non-BaseModel type
    with pytest.raises(ValidationError, match="must be a Pydantic BaseModel class"):
        list(provider.structured_streaming_output("gpt-4", "system", "user", str))
    
    with pytest.raises(ValidationError, match="must be a Pydantic BaseModel class"):
        list(provider.structured_streaming_output("gpt-4", "system", "user", dict))
    
    with pytest.raises(ValidationError, match="must be a Pydantic BaseModel class"):
        list(provider.structured_streaming_output("gpt-4", "system", "user", "not a class"))


@patch('streamshape.parser_integration.parse_streaming_response')
@patch('streamshape.litellm_integration.litellm.completion')
def test_structured_streaming_output_yields_validated_objects(mock_completion, mock_parser):
    """Test that structured_streaming_output yields validated Pydantic objects."""
    # Mock the LiteLLM streaming response
    mock_response = Mock()
    mock_completion.return_value = mock_response
    
    # Mock the parser to yield validated objects in the expected format
    obj1 = SampleSchema(name="test1", value=1)
    obj2 = SampleSchema(name="test2", value=2)
    mock_parser.return_value = iter([
        {"data": obj1, "usage": {}, "finished": False},
        {"data": obj2, "usage": {}, "finished": False},
        {"data": None, "usage": {}, "finished": True}
    ])
    
    # Create provider and call structured_streaming_output
    provider = ConcreteProvider("test_api_key")
    results = list(provider.structured_streaming_output(
        model="gpt-4",
        system_prompt="You are a helpful assistant",
        user_prompt="Generate data",
        output_schema=SampleSchema
    ))
    
    # Verify the results
    assert len(results) == 2
    assert results[0] == obj1
    assert results[1] == obj2
    
    # Verify LiteLLM was called correctly
    mock_completion.assert_called_once()
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["model"] == "test_provider/gpt-4"
    assert call_kwargs["stream"] is True
    assert "response_format" in call_kwargs
    assert call_kwargs["response_format"]["type"] == "json_schema"
    
    # Verify the prompt was augmented
    messages = call_kwargs["messages"]
    assert "Output only the JSON array" in messages[1]["content"]
    
    # Verify parser was called with correct arguments
    mock_parser.assert_called_once_with(mock_response, SampleSchema)


@patch('streamshape.parser_integration.parse_streaming_response')
@patch('streamshape.litellm_integration.litellm.completion')
def test_structured_streaming_output_forwards_optional_parameters(mock_completion, mock_parser):
    """Test that structured_streaming_output forwards optional parameters to LiteLLM."""
    # Mock the LiteLLM streaming response
    mock_response = Mock()
    mock_completion.return_value = mock_response
    
    # Mock the parser
    mock_parser.return_value = iter([])
    
    # Create provider and call with optional params
    provider = ConcreteProvider("test_api_key")
    list(provider.structured_streaming_output(
        model="gpt-4",
        system_prompt="System",
        user_prompt="User",
        output_schema=SampleSchema,
        temperature=0.7,
        max_tokens=100
    ))
    
    # Verify optional parameters were forwarded
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["temperature"] == 0.7
    assert call_kwargs["max_tokens"] == 100


@patch('streamshape.parser_integration.parse_streaming_response')
@patch('streamshape.litellm_integration.litellm.completion')
def test_structured_streaming_output_builds_correct_response_format(mock_completion, mock_parser):
    """Test that structured_streaming_output builds correct response_format."""
    # Mock the LiteLLM streaming response
    mock_response = Mock()
    mock_completion.return_value = mock_response
    
    # Mock the parser
    mock_parser.return_value = iter([])
    
    # Create provider and call
    provider = ConcreteProvider("test_api_key")
    list(provider.structured_streaming_output(
        model="gpt-4",
        system_prompt="System",
        user_prompt="User",
        output_schema=SampleSchema
    ))
    
    # Verify response_format structure
    call_kwargs = mock_completion.call_args.kwargs
    response_format = call_kwargs["response_format"]
    
    assert response_format["type"] == "json_schema"
    assert "json_schema" in response_format
    assert response_format["json_schema"]["name"] == "response_schema"
    assert response_format["json_schema"]["strict"] is False
    assert "schema" in response_format["json_schema"]
    assert response_format["json_schema"]["schema"]["type"] == "array"
    assert "items" in response_format["json_schema"]["schema"]
