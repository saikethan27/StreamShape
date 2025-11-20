"""
Example using the general LiteLLM provider class.

This allows you to use any LiteLLM-supported provider without needing
a specific provider class.
"""
import os
import sys
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add src to path to use local development version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the general LiteLLM provider
from streamshape import LiteLLM

# Load environment variables
load_dotenv()


class Joke(BaseModel):
    """Joke to tell user."""
    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline of the joke")
    rating: Optional[int] = Field(default=None, description="How funny the joke is, from 1 to 10")


def test_openrouter_with_litellm():
    """Test using OpenRouter through the general LiteLLM class."""
    print("\n" + "="*80)
    print("Testing OpenRouter with LiteLLM General Provider")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")
    
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in .env file")
        return
    
    # Initialize with provider="openrouter"
    provider = LiteLLM(api_key=api_key, provider="openrouter")
    
    print(f"\n📝 Provider: openrouter")
    print(f"📝 Model: {model}")
    print(f"📝 Prompt: Tell me a joke about Python programming")
    
    try:
        result = provider.generate(
            model=model,
            system_prompt="You are a helpful assistant.",
            user_prompt="Tell me a joke about Python programming",
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"\n✅ Response:\n{result['data']}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_anthropic_with_litellm():
    """Test using Anthropic through the general LiteLLM class."""
    print("\n" + "="*80)
    print("Testing Anthropic with LiteLLM General Provider")
    print("="*80)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        return
    
    # Initialize with provider="anthropic"
    provider = LiteLLM(api_key=api_key, provider="anthropic")
    
    print(f"\n📝 Provider: anthropic")
    print(f"📝 Model: claude-3-haiku-20240307")
    print(f"📝 Prompt: What is 2+2?")
    
    try:
        result = provider.generate(
            model="claude-3-haiku-20240307",
            system_prompt="You are a helpful assistant.",
            user_prompt="What is 2+2?",
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"\n✅ Response:\n{result['data']}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_structured_output_with_litellm():
    """Test structured output with the general LiteLLM class."""
    print("\n" + "="*80)
    print("Testing Structured Output with LiteLLM General Provider")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")
    
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in .env file")
        return
    
    # Initialize with provider="openrouter"
    provider = LiteLLM(api_key=api_key, provider="openrouter")
    
    print(f"\n📝 Provider: openrouter")
    print(f"📝 Model: {model}")
    print(f"📝 Prompt: Give me 3 jokes about AI")
    
    try:
        result = provider.structured_output(
            model=model,
            system_prompt="You are a helpful assistant that tells jokes.",
            user_prompt="Give me 3 jokes about AI",
            output_schema=Joke,
            temperature=0.7
        )
        
        jokes = result["data"]
        print(f"\n✅ Received {len(jokes)} jokes:\n")
        
        for i, joke in enumerate(jokes, 1):
            print(f"Joke #{i}:")
            print(f"  Setup: {joke.setup}")
            print(f"  Punchline: {joke.punchline}")
            if joke.rating:
                print(f"  Rating: {joke.rating}/10")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_custom_base_url_with_litellm():
    """Test using custom base URL (like Ollama) with LiteLLM class."""
    print("\n" + "="*80)
    print("Testing Custom Base URL with LiteLLM General Provider")
    print("="*80)
    
    # Example for Ollama or other OpenAI-compatible endpoints
    provider = LiteLLM(
        api_key="ollama",  # Can be any string for local endpoints
        provider="openai",  # Use openai for OpenAI-compatible endpoints
        base_url="http://localhost:11434/v1"
    )
    
    print(f"\n📝 Provider: openai (OpenAI-compatible)")
    print(f"📝 Base URL: http://localhost:11434/v1")
    print(f"📝 Model: llama2")
    print(f"\nNote: This requires Ollama to be running locally")
    print("Skipping actual call...\n")


if __name__ == "__main__":
    # Test with OpenRouter
    test_openrouter_with_litellm()
    
    # Uncomment to test with Anthropic
    # test_anthropic_with_litellm()
    
    # Test structured output
    test_structured_output_with_litellm()
    
    # Show custom base URL example
    test_custom_base_url_with_litellm()
