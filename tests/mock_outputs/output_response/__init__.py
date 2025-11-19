"""
Unified Mock Response Loader
Provides a single interface to load mock responses from all providers (OpenAI, Anthropic, Google).
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from . import openai_mock_response as openai_loader
from . import anthropic_mock_response as anthropic_loader
from . import google_mock_response as google_loader

# Import specific functions
openai_simple_text = openai_loader.get_simple_text_response
openai_streaming = openai_loader.get_streaming_response
openai_structured = openai_loader.get_structured_output_response
openai_streaming_structured = openai_loader.get_streaming_structured_output_response
openai_tool_call = openai_loader.get_tool_call_response
openai_streaming_tool_call = openai_loader.get_streaming_tool_call_response
openai_mcp_tool_call = openai_loader.get_mcp_tool_call_response
openai_raw_dict = openai_loader.get_raw_dict

anthropic_simple_text = anthropic_loader.get_simple_text_response
anthropic_streaming = anthropic_loader.get_streaming_response
anthropic_structured = anthropic_loader.get_structured_output_response
anthropic_tool_call = anthropic_loader.get_tool_call_response
anthropic_raw_dict = anthropic_loader.get_raw_dict


anthropic_streaming_structured = anthropic_loader.get_streaming_structured_output_response
anthropic_streaming_tool_call = anthropic_loader.get_streaming_tool_call_response


google_simple_text = google_loader.get_simple_text_response
google_streaming = google_loader.get_streaming_response
google_structured = google_loader.get_structured_output_response
google_tool_call = google_loader.get_tool_call_response
google_raw_dict = google_loader.get_raw_dict

google_streaming_structured = google_loader.get_streaming_structured_output_response
google_streaming_tool_call = google_loader.get_streaming_tool_call_response

class MockResponseLoader:
    """
    Unified interface to load mock responses from all providers.
    Use this class to simulate LLM API responses for testing without making actual API calls.
    """
    
    def __init__(self, provider: str):
        """
        Initialize loader for a specific provider.
        
        Args:
            provider: One of 'openai', 'anthropic', 'google'
        """
        if provider.lower() not in ['openai', 'anthropic', 'google']:
            raise ValueError(f"Unsupported provider: {provider}. Must be one of: openai, anthropic, google")
        
        self.provider = provider.lower()
    
    def load_simple_text(self):
        """Load simple text response"""
        if self.provider == 'openai':
            return openai_simple_text()
        elif self.provider == 'anthropic':
            return anthropic_simple_text()
        elif self.provider == 'google':
            return google_simple_text()
    
    def load_streaming(self):
        """Load streaming response (returns iterator)"""
        if self.provider == 'openai':
            return openai_streaming()
        elif self.provider == 'anthropic':
            return anthropic_streaming()
        elif self.provider == 'google':
            return google_streaming()
    
    def load_structured_output(self):
        """Load structured output response"""
        if self.provider == 'openai':
            return openai_structured()
        elif self.provider == 'anthropic':
            return anthropic_structured()
        elif self.provider == 'google':
            return google_structured()
    def load_streaming_structured_output(self):
        """Load structured output response"""
        if self.provider == 'openai':
            return openai_streaming_structured()
        elif self.provider == 'anthropic':
            return anthropic_streaming_structured()
        elif self.provider == 'google':
            return google_streaming_structured()
        
    def load_tool_call(self):
        """Load tool call response"""
        if self.provider == 'openai':
            return openai_tool_call()
        elif self.provider == 'anthropic':
            return anthropic_tool_call()
        elif self.provider == 'google':
            return google_tool_call()
    def load_streaming_tool_call(self):
        """Load structured output response"""
        if self.provider == 'openai':
            return openai_streaming_tool_call()
        elif self.provider == 'anthropic':
            return anthropic_streaming_tool_call()
        elif self.provider == 'google':
            return google_streaming_tool_call()
        
    def load_mcp_tool_call(self):
        """Load MCP tool call response (OpenAI only)"""
        if self.provider == 'openai':
            return openai_mcp_tool_call()
        else:
            raise NotImplementedError(f"MCP tool calls not available for {self.provider}")
    
    def load_raw_dict(self, response_type: str):
        """
        Load raw dictionary without converting to provider objects.
        
        Args:
            response_type: One of 'simple_text', 'streaming', 'structured_output', 'tool_call', 'mcp_tool_call'
        """
        if self.provider == 'openai':
            return openai_raw_dict(response_type)
        elif self.provider == 'anthropic':
            return anthropic_raw_dict(response_type)
        elif self.provider == 'google':
            return google_raw_dict(response_type)


# Convenience functions
def load_all_providers_simple_text():
    """Load simple text responses from all providers"""
    return {
        'openai': openai_simple_text(),
        'anthropic': anthropic_simple_text(),
        'google': google_simple_text()
    }


def load_all_providers_streaming():
    """Load streaming responses from all providers"""
    return {
        'openai': openai_streaming(),
        'anthropic': anthropic_streaming(),
        'google': google_streaming()
    }


def load_all_providers_tool_call():
    """Load tool call responses from all providers"""
    return {
        'openai': openai_tool_call(),
        'anthropic': anthropic_tool_call(),
        'google': google_tool_call()
    }


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("UNIFIED MOCK RESPONSE LOADER DEMO")
    print("=" * 60)
    
    # Load OpenAI responses
    print("\n### OpenAI Responses ###")
    openai_loader = MockResponseLoader('openai')
    openai_response = openai_loader.load_simple_text()
    print(f"Simple Text: {openai_response.choices[0].message.content[:100]}...")
    print(f"Model: {openai_response.model}")
    print(f"Tokens: {openai_response.usage.total_tokens}")
    
    # Load Anthropic responses
    print("\n### Anthropic Responses ###")
    anthropic_loader = MockResponseLoader('anthropic')
    anthropic_response = anthropic_loader.load_simple_text()
    print(f"Model: {anthropic_response.model}")
    print(f"Tokens: {anthropic_response.usage.input_tokens + anthropic_response.usage.output_tokens}")
    
    # Load Google responses
    print("\n### Google Responses ###")
    google_loader = MockResponseLoader('google')
    google_response = google_loader.load_simple_text()
    print(f"Simple Text: {google_response.text[:100]}...")
    print(f"Text length: {len(google_response.text)}")
    
    # Demonstrate streaming
    print("\n### Streaming Demo (OpenAI) ###")
    for i, chunk in enumerate(openai_loader.load_streaming()):
        if i < 5 and chunk.choices:  # Show first 5 chunks
            delta = chunk.choices[0].delta
            if delta.content:
                print(f"Chunk {i}: {delta.content}")
    def antropic_content(response):
        for block in response.content:
            if block.type == "text":
                return block.text
            elif block.type == "thinking":
                return block.thinking
    # Load all providers at once
    print("\n### All Providers - Simple Text ###")
    all_responses = load_all_providers_simple_text()
    for provider, response in all_responses.items():
        print(f"{provider.upper()}:")
        if provider == 'openai':
            print(f"  {response.choices[0].message.content[:80]}...")
        elif provider == 'anthropic':
            print(f"  {antropic_content(response)[:80]}...")
        elif provider == 'google':
            print(f"  {response.text[:80]}...")
    
    print("\n" + "=" * 60)
    print("✅ All mock responses loaded successfully!")
    print("=" * 60)
