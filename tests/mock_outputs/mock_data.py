from abc import ABC
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tests.mock_outputs.output_response import MockResponseLoader

class mock_data(ABC):
    def get_simple_text_response():
        pass
    def get_streaming_response():
        pass
    def get_structured_output_response():
        pass
    def get_streaming_structured_output_response():
        pass
    def get_tool_call_response():
        pass
    def get_streaming_tool_call_response():
        pass
    def get_raw_dict():
        pass

class openai(mock_data):
    @staticmethod
    def get_simple_text_response():
        loader = MockResponseLoader('openai')
        return loader.load_simple_text()

    @staticmethod
    def get_streaming_response():
        loader = MockResponseLoader('openai')
        return loader.load_streaming()

    @staticmethod
    def get_structured_output_response():
        loader = MockResponseLoader('openai')
        return loader.load_structured_output()
    @staticmethod
    def get_streaming_structured_output_response():
        loader = MockResponseLoader('openai')
        return loader.load_streaming_structured_output()
    
    @staticmethod
    def get_tool_call_response():
        loader = MockResponseLoader('openai')
        return loader.load_tool_call()
    @staticmethod
    def get_streaming_tool_call_response():
        loader = MockResponseLoader('openai')
        return loader.load_streaming_tool_call()

    @staticmethod
    def get_raw_dict(response_type: str):
        loader = MockResponseLoader('openai')
        return loader.load_raw_dict(response_type)

    @staticmethod
    def get_mcp_tool_call_response():
        loader = MockResponseLoader('openai')
        return loader.load_mcp_tool_call()

class anthropic(mock_data):
    @staticmethod
    def get_simple_text_response():
        loader = MockResponseLoader('anthropic')
        return loader.load_simple_text()

    @staticmethod
    def get_streaming_response():
        loader = MockResponseLoader('anthropic')
        return loader.load_streaming()

    @staticmethod
    def get_structured_output_response():
        loader = MockResponseLoader('anthropic')
        return loader.load_structured_output()
    @staticmethod
    def get_streaming_structured_output_response():
        loader = MockResponseLoader('anthropic')
        return loader.load_streaming_structured_output()
    
    @staticmethod
    def get_tool_call_response():
        loader = MockResponseLoader('anthropic')
        return loader.load_tool_call()
    @staticmethod
    def get_streaming_tool_call_response():
        loader = MockResponseLoader('anthropic')
        return loader.load_streaming_tool_call()
    
    @staticmethod
    def get_raw_dict(response_type: str):
        loader = MockResponseLoader('anthropic')
        return loader.load_raw_dict(response_type)

class google(mock_data):
    @staticmethod
    def get_simple_text_response():
        loader = MockResponseLoader('google')
        return loader.load_simple_text()

    @staticmethod
    def get_streaming_response():
        loader = MockResponseLoader('google')
        return loader.load_streaming()

    @staticmethod
    def get_structured_output_response():
        loader = MockResponseLoader('google')
        return loader.load_structured_output()
    @staticmethod
    def get_streaming_structured_output_response():
        loader = MockResponseLoader('google')
        return loader.load_streaming_structured_output()

    @staticmethod
    def get_tool_call_response():
        loader = MockResponseLoader('google')
        return loader.load_tool_call()
    @staticmethod
    def get_streaming_tool_call_response():
        loader = MockResponseLoader('google')
        return loader.load_streaming_tool_call()
    
    @staticmethod
    def get_raw_dict(response_type: str):
        loader = MockResponseLoader('google')
        return loader.load_raw_dict(response_type)

