"""
Test the new structured_output method (non-streaming).
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import the unified LLM interface
from streamshape import OpenAICompatible

# Load environment variables
load_dotenv()


# Define Pydantic model for structured output
class Joke(BaseModel):
    """Joke to tell user."""
    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline of the joke")
    rating: Optional[int] = Field(default=None, description="How funny the joke is, from 1 to 10")


def test_structured_output():
    """Test structured_output method (non-streaming)."""
    print("\n" + "="*80)
    print("Testing Structured Output Method (Non-Streaming)")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    
    provider = OpenAICompatible(api_key=api_key, base_url=base_url)
    
    print(f"\n📝 Prompt: Give me 3 jokes about Python programming")
    print(f"\n⏳ Waiting for complete response...\n")
    
    try:
        result = provider.structured_output(
            model=model,
            system_prompt="You are a helpful assistant that tells jokes.",
            user_prompt="Give me 3 jokes about Python programming",
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


def compare_streaming_vs_non_streaming():
    """Compare streaming vs non-streaming structured output."""
    print("\n" + "="*80)
    print("Comparing Streaming vs Non-Streaming Structured Output")
    print("="*80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    
    provider = OpenAICompatible(api_key=api_key, base_url=base_url)
    
    # Test non-streaming
    print(f"\n1️⃣  Non-Streaming (structured_output):")
    print(f"   Returns: List[Joke] - all at once")
    print(f"   Use case: When you need all data before processing\n")
    
    try:
        result = provider.structured_output(
            model=model,
            system_prompt="You are a helpful assistant that tells jokes.",
            user_prompt="Give me 2 jokes about databases",
            output_schema=Joke,
            temperature=0.7
        )
        jokes = result["data"]
        print(f"   ✅ Got {len(jokes)} jokes as a complete list")
        print(f"   Type: {type(jokes)}")
        print(f"   First joke: {jokes[0].setup}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test streaming
    print(f"2️⃣  Streaming (structured_streaming_output):")
    print(f"   Yields: Iterator[Joke] - one at a time")
    print(f"   Use case: When you want to process/display data as it arrives\n")
    
    try:
        count = 0
        for joke in provider.structured_streaming_output(
            model=model,
            system_prompt="You are a helpful assistant that tells jokes.",
            user_prompt="Give me 2 jokes about databases",
            output_schema=Joke,
            temperature=0.7
        ):
            count += 1
            print(f"   ✅ Received joke #{count}: {joke.setup}")
        print(f"   Total: {count} jokes streamed\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING NEW STRUCTURED_OUTPUT METHOD")
    print("="*80)
    
    test_structured_output()
    compare_streaming_vs_non_streaming()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")
