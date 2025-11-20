"""
Test all four methods with real API calls.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import the unified LLM interface
from src import OpenAICompatible

# Load environment variables
load_dotenv()


# Define Pydantic model for structured output
class Joke(BaseModel):
    """Joke to tell user."""
    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline of the joke")
    rating: Optional[int] = Field(default=None, description="How funny the joke is, from 1 to 10")


def test_generate():
    """Test generate method (non-streaming text)."""
    print("\n" + "="*80)
    print("1. Testing Generate Method (Non-Streaming Text)")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    
    provider = OpenAICompatible(api_key=api_key, base_url=base_url)
    
    print(f"\n📝 Prompt: Tell me a short joke about programming")
    
    try:
        result = provider.generate(
            model=model,
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me a short joke about programming",
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"\n✅ Response:\n{result['data']}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_stream():
    """Test stream method (streaming text)."""
    print("\n" + "="*80)
    print("2. Testing Stream Method (Streaming Text)")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    
    provider = OpenAICompatible(api_key=api_key, base_url=base_url)
    
    print(f"\n📝 Prompt: Write a haiku about coding")
    print(f"\n🔄 Streaming response:\n")
    
    try:
        for chunk in provider.stream(
            model=model,
            system_prompt="You are a helpful assistant.",
            user_prompt="Write a haiku about coding",
            temperature=0.7,
            max_tokens=100
        ):
            print(chunk["data"], end="", flush=True)
        
        print("\n\n✅ Stream completed!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_tool_call():
    """Test tool_call method (function calling)."""
    print("\n" + "="*80)
    print("3. Testing Tool Call Method (Function Calling)")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    
    provider = OpenAICompatible(api_key=api_key, base_url=base_url)
    
    # Define a tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    print(f"\n📝 Prompt: What's the weather like in San Francisco?")
    
    try:
        result = provider.tool_call(
            model=model,
            system_prompt="You are a helpful assistant with access to weather information.",
            user_prompt="What's the weather like in San Francisco?",
            tools=tools,
            temperature=0.7
        )
        
        print(f"\n✅ Tool Call Result:")
        print(f"  Tool Name: {result['data']['tool_name']}")
        print(f"  Arguments: {result['data']['arguments']}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_structured_output():
    """Test structured_output method (non-streaming)."""
    print("\n" + "="*80)
    print("4. Testing Structured Output (Non-Streaming)")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    
    provider = OpenAICompatible(api_key=api_key, base_url=base_url)
    
    print(f"\n📝 Prompt: Give me 3 jokes on Graph Theory")
    print(f"\n⏳ Waiting for complete response...\n")
    
    try:
        result = provider.structured_output(
            model=model,
            system_prompt="You are a helpful assistant that tells jokes.",
            user_prompt="Give me 3 jokes on Graph Theory",
            output_schema=Joke,
            temperature=0.7
        )
        
        jokes = result["data"]
        print(f"✅ Received {len(jokes)} jokes:\n")
        
        for i, joke in enumerate(jokes, 1):
            print(f"Joke #{i}:")
            print(f"  Setup: {joke.setup}")
            print(f"  Punchline: {joke.punchline}")
            if joke.rating:
                print(f"  Rating: {joke.rating}/10")
            print()
        
        print(f"✅ Successfully received all jokes at once!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_structured_streaming_output():
    """Test structured_streaming_output method."""
    print("\n" + "="*80)
    print("5. Testing Structured Streaming Output")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    
    provider = OpenAICompatible(api_key=api_key, base_url=base_url)
    
    print(f"\n📝 Prompt: Give me 3 jokes on Graph Theory")
    print(f"\n🔄 Streaming structured output...\n")
    
    try:
        joke_count = 0
        for joke in provider.structured_streaming_output(
            model=model,
            system_prompt="You are a helpful assistant that tells jokes.",
            user_prompt="Give me 3 jokes on Graph Theory",
            output_schema=Joke,
            temperature=0.7
        ):
            joke_count += 1
            print(f"Joke #{joke_count}:")
            print(f"  Setup: {joke.setup}")
            print(f"  Punchline: {joke.punchline}")
            if joke.rating:
                print(f"  Rating: {joke.rating}/10")
            print()
        
        print(f"✅ Successfully received {joke_count} jokes!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("UNIFIED LLM INTERFACE - TESTING ALL METHODS")
    print("="*80)
    
    # Test all five methods
    test_generate()
    test_stream()
    test_tool_call()
    test_structured_output()
    test_structured_streaming_output()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")
