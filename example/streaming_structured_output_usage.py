"""
Test streaming structured output with real API calls.
"""
import os
import sys
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add src to path to use local development version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the unified LLM interface
from streamshape import OpenRouter, Google, OpenAICompatible

# Load environment variables
load_dotenv()

class PunchlinesSchema(BaseModel):
    item: str = Field(description="item name punchline comes under")

# Define Pydantic model for joke response
class Joke(BaseModel):
    """Joke to tell user."""
    setup: str = Field(description="The setup of the joke")
    punchlines: list[PunchlinesSchema] = Field(description="List of items for the joke")
    rating: Optional[int] = Field(default=None, description="How funny the joke is, from 1 to 10")


def openrouter_streaming_structured():
    """Test streaming structured output with OpenRouter."""
    print("\n" + "="*80)
    print("Testing OpenRouter Streaming Structured Output")
    print("="*80)
    
    # Initialize OpenAI-compatible provider with OpenRouter
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENROUTER_MODEL")
    
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in .env file")
        return
    
    provider = OpenRouter(api_key=api_key)
    
    # Create the prompt
    system_prompt = "You are a helpful assistant that tells jokes."
    user_prompt = "Give me 5 jokes on Graph Theory and 2 on python indivudial"
    
    print(f"\n📝 Model: {model}")
    print(f"📝 Prompt: {user_prompt}")
    print(f"\n🔄 Streaming jokes...\n")
    
    try:
        # Stream structured output
        joke_count = 0
        final_usage = None
        
        for result in provider.structured_streaming_output(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=Joke,
            temperature=0.7
        ):
            # Extract data and usage from result dictionary
            joke = result.get('data')
            usage = result.get('usage')
            
            # Store usage data if present
            if usage:
                final_usage = usage
            
            # Skip if no data (final chunk with just usage)
            if not joke:
                continue
            
            joke_count += 1
            print(f"Joke #{joke_count}:")
            print(f"  Setup: {joke.setup}")
            print(f"  Punchlines:")
            for punchline in joke.punchlines:
                print(f"    - (under: {punchline.item})")
            if joke.rating:
                print(f"  Rating: {joke.rating}/10")
            print()
        
        print(f"{'='*80}")
        print(f"✅ Successfully received {joke_count} jokes!")
        if final_usage:
            print(f"📊 Token Usage:")
            print(f"   - Prompt tokens: {final_usage.get('prompt_tokens', 'N/A')}")
            print(f"   - Completion tokens: {final_usage.get('completion_tokens', 'N/A')}")
            print(f"   - Total tokens: {final_usage.get('total_tokens', 'N/A')}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def google_streaming_structured():
    """Test streaming structured output with Google Gemini."""
    print("\n" + "="*80)
    print("Testing Google Gemini Streaming Structured Output")
    print("="*80)
    
    # Initialize Google provider
    api_key = os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GOOGLE_MODEL")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env file")
        return
    
    provider = Google(api_key=api_key)
    
    # Create the prompt
    system_prompt = "You are a helpful assistant that tells jokes."
    user_prompt = "Give me 3 jokes on Computer Science"
    
    print(f"\n📝 Model: {model}")
    print(f"📝 Prompt: {user_prompt}")
    print(f"\n🔄 Streaming jokes...\n")
    
    try:
        # Stream structured output
        joke_count = 0
        final_usage = None
        
        for result in provider.structured_streaming_output(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=Joke,
            temperature=0.7
        ):
            # Extract data and usage from result dictionary
            joke = result.get('data')
            usage = result.get('usage')
            
            # Store usage data if present
            if usage:
                final_usage = usage
            
            # Skip if no data (final chunk with just usage)
            if not joke:
                continue
            
            joke_count += 1
            print(f"Joke #{joke_count}:")
            print(f"  Setup: {joke.setup}")
            print(f"  Punchlines:")
            for punchline in joke.punchlines:
                print(f"    - (under: {punchline.item})")
            if joke.rating:
                print(f"  Rating: {joke.rating}/10")
            print()
        
        print(f"{'='*80}")
        print(f"✅ Successfully received {joke_count} jokes!")
        if final_usage:
            print(f"📊 Token Usage:")
            print(f"   - Prompt tokens: {final_usage.get('prompt_tokens', 'N/A')}")
            print(f"   - Completion tokens: {final_usage.get('completion_tokens', 'N/A')}")
            print(f"   - Total tokens: {final_usage.get('total_tokens', 'N/A')}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def openai_compatible_streaming_structured():
    """Test streaming structured output with OpenAI-compatible endpoint."""
    print("\n" + "="*80)
    print("Testing OpenAI-Compatible Streaming Structured Output")
    print("="*80)
    
    # Initialize OpenAI-compatible provider
    api_key = os.getenv("OPENAI_COMP_API_KEY")
    base_url = os.getenv("OPENAI_COMP_BASE_URL")
    model = os.getenv("OPENAI_COMP_MODEL")
    
    if not api_key:
        print("❌ OPENAI_COMP_API_KEY not found in .env file")
        return
    
    provider = OpenAICompatible(api_key=api_key, base_url=base_url)
    
    # Create the prompt
    system_prompt = "You are a helpful assistant that tells jokes."
    user_prompt = "Give me 4 jokes on Algorithms"
    
    print(f"\n📝 Model: {model}")
    print(f"📝 Prompt: {user_prompt}")
    print(f"\n🔄 Streaming jokes...\n")
    
    try:
        # Stream structured output
        joke_count = 0
        final_usage = None
        
        for result in provider.structured_streaming_output(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=Joke,
            temperature=0.7
        ):
            # Extract data and usage from result dictionary
            joke = result.get('data')
            usage = result.get('usage')
            
            # Store usage data if present
            if usage:
                final_usage = usage
            
            # Skip if no data (final chunk with just usage)
            if not joke:
                continue
            
            joke_count += 1
            print(f"Joke #{joke_count}:")
            print(f"  Setup: {joke.setup}")
            print(f"  Punchlines:")
            for punchline in joke.punchlines:
                print(f"    - (under: {punchline.item})")
            if joke.rating:
                print(f"  Rating: {joke.rating}/10")
            print()
        
        print(f"{'='*80}")
        print(f"✅ Successfully received {joke_count} jokes!")
        if final_usage:
            print(f"📊 Token Usage:")
            print(f"   - Prompt tokens: {final_usage.get('prompt_tokens', 'N/A')}")
            print(f"   - Completion tokens: {final_usage.get('completion_tokens', 'N/A')}")
            print(f"   - Total tokens: {final_usage.get('total_tokens', 'N/A')}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Test with OpenRouter (using OpenAI-compatible endpoint)
    # openrouter_streaming_structured()
    
    # Uncomment to test with Google Gemini
    google_streaming_structured()

    # Uncomment to test with another OpenAI-compatible endpoint
    # openai_compatible_streaming_structured()
