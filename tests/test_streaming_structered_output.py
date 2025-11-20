"""
Test streaming structured output parser with mock data.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pydantic import BaseModel, Field
from typing import List
from tests.mock_outputs.mock_data import openai as openai_mock
from streamshape.streaming_structured_output_parser.parse_llm_output import read_tokens


# Define the schema based on the mock data (cities with weather)
class City(BaseModel):
    """City weather information."""
    city: str = Field(description="Name of the city")
    condition: str = Field(description="Weather condition")
    temperature_c: int = Field(description="Temperature in Celsius")


def test_streaming_structured_output():
    """Test the streaming structured output parser with OpenAI mock data."""
    print("\n" + "="*80)
    print("Testing Streaming Structured Output Parser")
    print("="*80)
    
    # Get mock streaming response
    response = openai_mock.get_streaming_structured_output_response()
    
    print("\n🔄 Processing streaming structured output...\n")
    
    city_count = 0
    final_usage = None
    result_count = 0
    
    # Process the stream
    for result in read_tokens(
        response=response,
        output_schema=City,
        request_type="openai",
        cancel_event=None
    ):
        result_count += 1
        data = result.get("data")
        usage = result.get("usage")
        finished = result.get("finished", False)
        error = result.get("error")
        
        if data:
            city_count += 1
            print(f"City #{city_count}: {data.city}")
            print(f"  Condition: {data.condition}")
            print(f"  Temperature: {data.temperature_c}°C")
            print()
        
        if usage:
            final_usage = usage
        
        if finished:
            print("✅ Stream completed!")
            break
        
        if error:
            print(f"❌ Error: {error}")
            break
    
    print(f"{'='*80}")
    print(f"✅ Test completed successfully!")
    print(f"   Parsed {city_count} cities")
    if final_usage:
        print(f"   Tokens used: {final_usage.get('total_tokens', 'N/A')}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_streaming_structured_output()
