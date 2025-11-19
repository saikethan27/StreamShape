"""Tests for the unified LLM interface with mock data."""

from __future__ import annotations

import json
from typing import List
from unittest.mock import patch

import pytest
from pydantic import BaseModel, Field

from src import OpenAI, Google, Anthropic
from src.exceptions import ValidationError
from tests.mock_outputs.mock_data import openai as openai_mock
from tests.mock_outputs.mock_data import google as google_mock
from tests.mock_outputs.mock_data import anthropic as anthropic_mock


class City(BaseModel):
    """Test schema for structured output."""
    city: str = Field(description="City name")
    condition: str = Field(description="Weather condition")
    temperature_c: int = Field(description="Temperature in Celsius")


def test_openai_generate_with_mock_data() -> None:
    """Test OpenAI provider's generate method with mock data."""
    mock_response = openai_mock.get_simple_text_response()
    
    with patch("src.litellm_integration.litellm.completion", return_value=mock_response):
        provider = OpenAI(api_key="test-key")
        result = provider.generate(
            model="gpt-4",
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me a joke"
        )
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "raw_chunks" in result
        assert isinstance(result["data"], str)
        assert "joke" in result["data"].lower()


def test_google_generate_with_mock_data() -> None:
    """Test Google provider's generate method with mock data."""
    # Google returns native objects, so we need to create a normalized mock
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Why did the programmer quit his job? Because he didn't get arrays!"
    
    with patch("src.litellm_integration.litellm.completion", return_value=mock_response):
        provider = Google(api_key="test-key")
        result = provider.generate(
            model="gemini-pro",
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me a joke"
        )
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "raw_chunks" in result
        assert isinstance(result["data"], str)
        assert len(result["data"]) > 0


def test_anthropic_generate_with_mock_data() -> None:
    """Test Anthropic provider's generate method with mock data."""
    # Anthropic returns native objects, so we need to create a normalized mock
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Why don't scientists trust atoms? Because they make up everything!"
    
    with patch("src.litellm_integration.litellm.completion", return_value=mock_response):
        provider = Anthropic(api_key="test-key")
        result = provider.generate(
            model="claude-3-opus",
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me a joke"
        )
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "raw_chunks" in result
        assert isinstance(result["data"], str)
        assert len(result["data"]) > 0


def test_tool_call_with_mock_data() -> None:
    """Test tool calling functionality with mock data."""
    mock_response = openai_mock.get_tool_call_response()
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    }
                }
            }
        }
    ]
    
    with patch("src.litellm_integration.litellm.completion", return_value=mock_response):
        provider = OpenAI(api_key="test-key")
        result = provider.tool_call(
            model="gpt-4",
            system_prompt="You are a helpful assistant.",
            user_prompt="What's the weather in Berlin?",
            tools=tools
        )
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "raw_chunks" in result
        assert result["data"]["tool_name"] == "get_weather"
        assert "Berlin" in result["data"]["arguments"]


def test_streaming_with_mock_data() -> None:
    """Test streaming functionality with mock data."""
    mock_stream = openai_mock.get_streaming_response()
    
    with patch("src.litellm_integration.litellm.completion", return_value=mock_stream):
        provider = OpenAI(api_key="test-key")
        chunks = list(provider.stream(
            model="gpt-4",
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me a joke"
        ))
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("data" in chunk and "raw_chunks" in chunk for chunk in chunks)
        full_text = "".join([chunk["data"] for chunk in chunks])
        assert len(full_text) > 0


def test_google_streaming_with_mock_data() -> None:
    """Test Google provider's streaming with mock data."""
    # Create normalized streaming chunks
    from unittest.mock import Mock
    
    mock_chunks = []
    for text in ["Why ", "did ", "the ", "chicken ", "cross ", "the ", "road?"]:
        chunk = Mock()
        chunk.choices = [Mock()]
        chunk.choices[0].delta = Mock()
        chunk.choices[0].delta.content = text
        mock_chunks.append(chunk)
    
    with patch("src.litellm_integration.litellm.completion", return_value=iter(mock_chunks)):
        provider = Google(api_key="test-key")
        chunks = list(provider.stream(
            model="gemini-pro",
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me a joke"
        ))
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("data" in chunk and "raw_chunks" in chunk for chunk in chunks)
        full_text = "".join([chunk["data"] for chunk in chunks])
        assert len(full_text) > 0


def test_anthropic_streaming_with_mock_data() -> None:
    """Test Anthropic provider's streaming with mock data."""
    # Create normalized streaming chunks
    from unittest.mock import Mock
    
    mock_chunks = []
    for text in ["Here's ", "a ", "joke: ", "Why ", "don't ", "atoms ", "trust ", "each ", "other?"]:
        chunk = Mock()
        chunk.choices = [Mock()]
        chunk.choices[0].delta = Mock()
        chunk.choices[0].delta.content = text
        mock_chunks.append(chunk)
    
    with patch("src.litellm_integration.litellm.completion", return_value=iter(mock_chunks)):
        provider = Anthropic(api_key="test-key")
        chunks = list(provider.stream(
            model="claude-3-opus",
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me a joke"
        ))
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("data" in chunk and "raw_chunks" in chunk for chunk in chunks)
        full_text = "".join([chunk["data"] for chunk in chunks])
        assert len(full_text) > 0


def test_structured_output_with_mock_data() -> None:
    """Test structured output with mock data."""
    # The mock returns {"cities": [...]}, but structured_output expects [...]
    # So we create a proper mock response with an array
    from unittest.mock import Mock
    import json
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = json.dumps([
        {"city": "Tokyo", "condition": "Partly Cloudy", "temperature_c": 22},
        {"city": "London", "condition": "Rainy", "temperature_c": 15},
        {"city": "Delhi", "condition": "Hazy", "temperature_c": 28}
    ])
    
    with patch("src.litellm_integration.litellm.completion", return_value=mock_response):
        provider = OpenAI(api_key="test-key")
        result = provider.structured_output(
            model="gpt-4",
            system_prompt="You are a helpful assistant.",
            user_prompt="Give me weather for cities",
            output_schema=City
        )
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "raw_chunks" in result
        assert len(result["data"]) == 3
        assert all(isinstance(r, City) for r in result["data"])
        assert result["data"][0].city == "Tokyo"


def test_validation_errors() -> None:
    """Test that validation errors are raised for invalid inputs."""
    provider = OpenAI(api_key="test-key")
    
    # Test missing model
    with pytest.raises(ValidationError, match="model.*required"):
        provider.generate(
            model="",
            system_prompt="Test",
            user_prompt="Test"
        )
    
    # Test missing system_prompt
    with pytest.raises(ValidationError, match="system_prompt.*required"):
        provider.generate(
            model="gpt-4",
            system_prompt="",
            user_prompt="Test"
        )
    
    # Test missing user_prompt
    with pytest.raises(ValidationError, match="user_prompt.*required"):
        provider.generate(
            model="gpt-4",
            system_prompt="Test",
            user_prompt=""
        )
    
    # Test missing tools
    with pytest.raises(ValidationError, match="tools.*required"):
        provider.tool_call(
            model="gpt-4",
            system_prompt="Test",
            user_prompt="Test",
            tools=None
        )
    
    # Test invalid tools type
    with pytest.raises(ValidationError, match="tools.*must be a list"):
        provider.tool_call(
            model="gpt-4",
            system_prompt="Test",
            user_prompt="Test",
            tools="invalid"
        )


def test_structured_output_validation() -> None:
    """Test structured output with schema validation."""
    # Create a mock response with JSON array
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = json.dumps([
        {"city": "Paris", "condition": "Sunny", "temperature_c": 20},
        {"city": "London", "condition": "Rainy", "temperature_c": 15}
    ])
    
    with patch("src.litellm_integration.litellm.completion", return_value=mock_response):
        provider = OpenAI(api_key="test-key")
        result = provider.structured_output(
            model="gpt-4",
            system_prompt="You are a helpful assistant.",
            user_prompt="Give me weather for 2 cities",
            output_schema=City
        )
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "raw_chunks" in result
        assert len(result["data"]) == 2
        assert all(isinstance(r, City) for r in result["data"])
        assert result["data"][0].city == "Paris"
        assert result["data"][1].city == "London"


def test_provider_representation() -> None:
    """Test that provider objects have proper string representation."""
    openai_provider = OpenAI(api_key="secret-key")
    google_provider = Google(api_key="secret-key")
    anthropic_provider = Anthropic(api_key="secret-key")
    
    # Ensure API keys are not exposed in string representation
    assert "secret-key" not in str(openai_provider)
    assert "secret-key" not in repr(openai_provider)
    
    # Ensure provider names are included
    assert "openai" in str(openai_provider).lower()
    assert "gemini" in str(google_provider).lower()
    assert "anthropic" in str(anthropic_provider).lower()


def test_message_building() -> None:
    """Test that messages are built correctly."""
    provider = OpenAI(api_key="test-key")
    messages = provider._build_messages("System prompt", "User prompt")
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "System prompt"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "User prompt"


def test_response_format_building() -> None:
    """Test that response format is built correctly for structured output."""
    provider = OpenAI(api_key="test-key")
    response_format = provider._build_response_format(City)
    
    assert response_format["type"] == "json_schema"
    assert "json_schema" in response_format
    assert response_format["json_schema"]["name"] == "response_schema"
    assert response_format["json_schema"]["schema"]["type"] == "array"
    assert "items" in response_format["json_schema"]["schema"]


def test_multiple_providers_consistency() -> None:
    """Test that all providers work consistently with normalized mock responses."""
    from unittest.mock import Mock
    
    # Create a normalized mock response that works for all providers
    def create_mock_response(content: str):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = content
        return mock_response
    
    providers = [
        OpenAI(api_key="test-key"),
        Google(api_key="test-key"),
        Anthropic(api_key="test-key"),
    ]
    
    for provider in providers:
        mock_response = create_mock_response("This is a test joke!")
        with patch("src.litellm_integration.litellm.completion", return_value=mock_response):
            result = provider.generate(
                model="test-model",
                system_prompt="You are a helpful assistant.",
                user_prompt="Tell me a joke"
            )
            
            assert isinstance(result, dict)
            assert "data" in result
            assert "raw_chunks" in result
            assert isinstance(result["data"], str)
            assert len(result["data"]) > 0
            assert "test joke" in result["data"].lower()
