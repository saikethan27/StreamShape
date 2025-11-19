"""
Google Gemini Mock Response Loader
Load saved raw Google Gemini API responses and simulate streaming exactly as LLM returns them.
"""
import os
import json
from typing import Iterator, Dict, Any
import time
from google.genai import types

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw_data", "google")


def load_raw_response(response_type: str) -> Dict[str, Any]:
    """Load raw response from JSON file"""
    filepath = os.path.join(RAW_DATA_DIR, f"{response_type}.json")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw data file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_simple_text_response() -> types.GenerateContentResponse:
    """
    Load and return simple text response using official Google GenAI types.
    Simulates exactly what Google Gemini API returns.
    """
    data = load_raw_response("simple_text")
    return types.GenerateContentResponse(**data)


def get_streaming_response() -> Iterator[types.GenerateContentResponse]:
    """
    Load and yield streaming chunks using official Google GenAI types.
    Simulates exactly what Google Gemini streaming API returns.
    """
    data = load_raw_response("streaming")
    # streaming.json is a list of chunks, not a dict with "chunks" key
    chunks = data if isinstance(data, list) else data.get("chunks", [])

    for chunk_data in chunks:
        time.sleep(0.2)
        yield types.GenerateContentResponse(**chunk_data)


def get_structured_output_response() -> types.GenerateContentResponse:
    """
    Load and return structured output response using official Google GenAI types.
    Simulates exactly what Google Gemini API returns with JSON schema.
    """
    data = load_raw_response("structured_output")
    return types.GenerateContentResponse(**data)
def get_streaming_structured_output_response() -> Iterator[types.GenerateContentResponse]:
    """
    Load and yield streaming_structured_output chunks using official Google GenAI types.
    Simulates exactly what Google Gemini streaming_structured_output API returns.
    """
    data = load_raw_response("streaming_structured_output")
    # streaming_structured_output.json is a list of chunks, not a dict with "chunks" key
    chunks = data if isinstance(data, list) else data.get("chunks", [])

    for chunk_data in chunks:
        time.sleep(0.2)
        yield types.GenerateContentResponse(**chunk_data)

def get_tool_call_response() -> types.GenerateContentResponse:
    """
    Load and return tool call response using official Google GenAI types.
    Simulates exactly what Google Gemini API returns with function calling.
    """
    data = load_raw_response("tool_call")
    return types.GenerateContentResponse(**data)

def get_streaming_tool_call_response() -> Iterator[types.GenerateContentResponse]:
    """
    Load and yield streaming_tool_call chunks using official Google GenAI types.
    Simulates exactly what Google Gemini streaming_tool_call API returns.
    """
    data = load_raw_response("streaming_tool_call")
    # streaming_tool_call_response.json is a list of chunks, not a dict with "chunks" key
    chunks = data if isinstance(data, list) else data.get("chunks", [])

    for chunk_data in chunks:
        time.sleep(0.2)
        yield types.GenerateContentResponse(**chunk_data)

def get_raw_dict(response_type: str) -> Dict[str, Any]:
    """
    Get raw dictionary without converting to mock objects.
    Useful for testing normalizers directly.
    """
    return load_raw_response(response_type)



def _extract_function_calls(response: types.GenerateContentResponse) -> list:
    """
    Extract function calls from response candidates.
    Returns list of function call information.
    """
    function_calls = []

    # Extract function calls from the candidates
    for candidate in response.candidates:
        if hasattr(candidate, 'content') and candidate.content:
            parts = candidate.content.parts if hasattr(candidate.content, 'parts') else []
            for part in parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append(part.function_call)

    return function_calls


# Example usage
if __name__ == "__main__":
    print("=== Loading Simple Text Response ===")
    response = get_simple_text_response()
    print(f"Type: {type(response)}")
    print(f"Text: {response.text}")
    print(f"Candidates count: {len(response.candidates)}")
    print(f"Usage metadata: {response.usage_metadata}")
    
    print("\n=== Loading Streaming Response ===")
    print("Streaming chunks:")
    for i, chunk in enumerate(get_streaming_response()):
        print(f"Chunk {i}: {chunk.text}", end="", flush=True)
    print("\n")
    
    print("\n=== Loading Structured Output ===")
    structured = get_structured_output_response()
    print(f"Text: {structured.text}")
    
    print("\n=== Loading Tool Call Response ===")
    tool_response = get_tool_call_response()
    print(f"Text: {tool_response.text}")
    function_calls = _extract_function_calls(tool_response)
    if function_calls:
        print(f"Function calls found: {len(function_calls)}")
        for fc in function_calls:
            # fc is now a FunctionCall object, not a dict
            print(f"  Function: {fc.name}")
            print(f"  Args: {fc.args}")
    else:
        print("No function calls found")
    
    print("\n=== Loading Raw Dict ===")
    raw = get_raw_dict("simple_text")
    print(f"Raw dict keys: {raw.keys()}")
    
    print("\n=== Loading Streaming Tool Call Response ===")
    print("Streaming tool call chunks:")
    for i, chunk in enumerate(get_streaming_tool_call_response()):
        print(f"Chunk {i}: {chunk.text}", end="", flush=True)
    print("\n")
    
    print("\n=== Loading Streaming Structured Output Response ===")
    print("Streaming structured output chunks:")
    for i, chunk in enumerate(get_streaming_structured_output_response()):
        print(f"Chunk {i}: {chunk.text}", end="", flush=True)
        function_calls = _extract_function_calls(tool_response)
        if function_calls:
            print(f"Function calls found: {len(function_calls)}")
            for fc in function_calls:
                # fc is now a FunctionCall object, not a dict
                print(f"  Function: {fc.name}")
                print(f"  Args: {fc.args}")
        else:
            print("No function calls found")
    print("\n")
