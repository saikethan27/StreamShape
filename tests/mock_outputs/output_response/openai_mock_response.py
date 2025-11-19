"""
OpenAI Mock Response Loader
Load saved raw OpenAI API responses and simulate streaming exactly as LLM returns them.
"""
import os
import json
from typing import Iterator, Dict, Any
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice, ChoiceDelta
import time

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw_data", "openai")


def load_raw_response(response_type: str) -> Dict[str, Any]:
    """Load raw response from JSON file"""
    filepath = os.path.join(RAW_DATA_DIR, f"{response_type}.json")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw data file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_simple_text_response() -> ChatCompletion:
    """
    Load and return simple text response as ChatCompletion object.
    Simulates exactly what OpenAI API returns.
    """
    data = load_raw_response("simple_text")
    return ChatCompletion(**data)


def get_streaming_response() -> Iterator[ChatCompletionChunk]:
    """
    Load and yield streaming chunks as ChatCompletionChunk objects.
    Simulates exactly what OpenAI streaming API returns.
    """
    data = load_raw_response("streaming")
    chunks = data.get("chunks", [])
    
    for chunk_data in chunks:
        time.sleep(0.002)
        yield ChatCompletionChunk(**chunk_data)


def get_structured_output_response() -> ChatCompletion:
    """
    Load and return structured output response as ChatCompletion object.
    Simulates exactly what OpenAI API returns with JSON schema.
    """
    data = load_raw_response("structured_output")
    return ChatCompletion(**data)

def get_streaming_structured_output_response() -> Iterator[ChatCompletionChunk]:
    """
    Load and yield streaming chunks as ChatCompletionChunk objects.
    Simulates exactly what OpenAI streaming API returns.
    """
    data = load_raw_response("streaming_structured_output")
    chunks = data.get("chunks", [])
    
    for chunk_data in chunks:
        time.sleep(0.002)
        yield ChatCompletionChunk(**chunk_data)

def get_tool_call_response() -> ChatCompletion:
    """
    Load and return tool call response as ChatCompletion object.
    Simulates exactly what OpenAI API returns with function calling.
    """
    data = load_raw_response("tool_call")
    return ChatCompletion(**data)

def get_streaming_tool_call_response() -> Iterator[ChatCompletionChunk]:
    """
    Load and yield streaming chunks as ChatCompletionChunk objects.
    Simulates exactly what OpenAI streaming API returns.
    """
    data = load_raw_response("streaming_tool_call")
    chunks = data.get("chunks", [])
    
    for chunk_data in chunks:
        time.sleep(0.002)
        yield ChatCompletionChunk(**chunk_data)
def get_mcp_tool_call_response() -> ChatCompletion:
    """
    Load and return MCP tool call response as ChatCompletion object.
    Simulates exactly what OpenAI API returns for MCP tools.
    """
    data = load_raw_response("mcp_tool_call")
    return ChatCompletion(**data)


def get_raw_dict(response_type: str) -> Dict[str, Any]:
    """
    Get raw dictionary without converting to OpenAI objects.
    Useful for testing normalizers directly.
    """
    return load_raw_response(response_type)


# Example usage
if __name__ == "__main__":
    print("=== Loading Simple Text Response ===")
    response = get_simple_text_response()
    print(f"Type: {type(response)}")
    print(f"Content: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    print(f"Usage: {response.usage}")
    
    print("\n=== Loading Streaming Response ===")
    print("Streaming chunks:")
    for i, chunk in enumerate(get_streaming_response()):
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")
    
    print("\n=== Loading Structured Output ===")
    structured = get_structured_output_response()
    print(f"Content: {structured.choices[0].message.content}")
    
    print("\n=== Loading Tool Call Response ===")
    tool_response = get_tool_call_response()
    if tool_response.choices[0].message.tool_calls:
        for tc in tool_response.choices[0].message.tool_calls:
            print(f"Tool: {tc.function.name}")
            print(f"Arguments: {tc.function.arguments}")
    
    print("\n=== Loading Raw Dict ===")
    raw = get_raw_dict("simple_text")
    print(f"Raw dict keys: {raw.keys()}")
