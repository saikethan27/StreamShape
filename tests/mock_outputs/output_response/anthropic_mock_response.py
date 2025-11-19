"""
Anthropic Mock Response Loader
Load saved raw Anthropic API responses and simulate streaming exactly as LLM returns them.
"""
import os
import json
import time
from typing import Iterator, Dict, Any
from anthropic.types import (
    Message, 
    ContentBlock, 
    TextBlock, 
    ToolUseBlock,
    RawMessageStreamEvent,
    MessageStartEvent,
    MessageDeltaEvent,
    MessageStopEvent,
    ContentBlockStartEvent,
    ContentBlockDeltaEvent,
    ContentBlockStopEvent,
)
from anthropic.types.message import Usage


RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw_data", "anthropic")


def _construct_stream_event(event_data: Dict[str, Any]) -> RawMessageStreamEvent:
    """
    Construct the appropriate streaming event type based on event data.
    This maps the event type to the correct Anthropic SDK event class.
    """
    event_type = event_data.get("type")
    
    # Make a copy to avoid modifying the original
    event_copy = event_data.copy()
    
    # Handle content_block validation issues
    if event_type == "content_block_start" and "content_block" in event_copy:
        content_block = event_copy["content_block"]
        if content_block.get("type") == "thinking":
            # Fix null signature - Anthropic SDK expects empty string, not null
            if content_block.get("signature") is None:
                content_block["signature"] = ""
    
    try:
        if event_type == "message_start":
            return MessageStartEvent(**event_copy)
        elif event_type == "message_delta":
            return MessageDeltaEvent(**event_copy)
        elif event_type == "message_stop":
            return MessageStopEvent(**event_copy)
        elif event_type == "content_block_start":
            return ContentBlockStartEvent(**event_copy)
        elif event_type == "content_block_delta":
            return ContentBlockDeltaEvent(**event_copy)
        elif event_type == "content_block_stop":
            return ContentBlockStopEvent(**event_copy)
        else:
            # For other event types (like ping, thinking snapshots, etc.), return as dict
            # The Anthropic SDK doesn't have types for these custom events
            return event_copy
    except Exception as e:
        # If validation fails, return as dict for custom/non-standard events
        return event_data


def load_raw_response(response_type: str) -> Dict[str, Any]:
    """Load raw response from JSON file"""
    filepath = os.path.join(RAW_DATA_DIR, f"{response_type}.json")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw data file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_simple_text_response() -> Message:
    """
    Load and return simple text response as Message object.
    Simulates exactly what Anthropic API returns.
    """
    data = load_raw_response("simple_text")
    return Message(**data)


def get_streaming_response() -> Iterator[RawMessageStreamEvent]:
    """
    Load and yield streaming events exactly as Anthropic API returns them.
    Validates each event through official Anthropic SDK types.
    """
    data = load_raw_response("streaming")
    events = data.get("events", [])
    
    # Yield each event after validating with official Anthropic types
    for event in events:
        yield _construct_stream_event(event)
        time.sleep(0.002)  # Small delay to simulate network streaming


def get_structured_output_response() -> Message:
    """
    Load and return structured output response as Message object.
    Simulates exactly what Anthropic API returns with JSON output.
    """
    data = load_raw_response("structured_output")
    return Message(**data)
def get_streaming_structured_output_response() -> Iterator[RawMessageStreamEvent]:
    """
    Load and return streaming structured output events.
    Validates each event through official Anthropic SDK types.
    """
    data = load_raw_response("streaming_structured_output")
    events = data.get("chunks", [])

    for event in events:
        yield _construct_stream_event(event)
        time.sleep(0.002) 

def get_tool_call_response() -> Message:
    """
    Load and return tool call response as Message object.
    Simulates exactly what Anthropic API returns with tool use.
    """
    data = load_raw_response("tool_call")
    return Message(**data)

def get_streaming_tool_call_response() -> Iterator[RawMessageStreamEvent]:
    """
    Load and yield streaming tool call events.
    Validates each event through official Anthropic SDK types.
    """
    data = load_raw_response("streaming_tool_call")
    events = data.get("chunks", [])

    for event in events:
        yield _construct_stream_event(event)
        time.sleep(0.002) 

def get_raw_dict(response_type: str) -> Dict[str, Any]:
    """
    Get raw dictionary without converting to Anthropic objects.
    Useful for testing normalizers directly.
    """
    return load_raw_response(response_type)





# Example usage
if __name__ == "__main__":
    print("=== Loading Simple Text Response ===")
    response = get_simple_text_response()
    print(f"Type: {type(response)}")
    print(f"Model: {response.model}")
    print(f"Stop Reason: {response.stop_reason}")
    
    # Handle thinking and text blocks
    print("\nContent blocks:")
    for block in response.content:
        print(f"  Block type: {block.type}")
        if block.type == "text":
            print(f"  Text: {block.text[:100]}...")
        elif block.type == "thinking":
            print(f"  Thinking: {block.thinking[:100] if hasattr(block, 'thinking') else 'N/A'}...")
    
    print(f"Usage: {response.usage}")
    
    print("\n=== Loading Streaming Response ===")
    print("Streaming chunks:")
    for event in get_streaming_response():
        # Events are now typed objects, not dicts
        event_type = event.type if hasattr(event, 'type') else type(event).__name__

        # Display relevant data based on event type
        if event_type == "content_block_delta":
            if hasattr(event, 'delta'):
                delta = event.delta
                if hasattr(delta, 'type'):
                    # Handle text deltas
                    if delta.type == "text_delta" and hasattr(delta, 'text'):
                        print(f"{delta.text}", end="", flush=True)
                    # Handle thinking deltas - skip them in streaming output
                    elif delta.type == "thinking_delta":
                        pass
        elif event_type in ["message_start", "content_block_start", "content_block_stop", "message_delta", "message_stop"]:
            # Only print important event types
            print(f"\n[{event_type}]", end="")
        elif isinstance(event, dict):
            # Handle custom events like "thinking" that aren't official SDK types
            if event.get("type") == "thinking":
                pass
    print("\n")
    
    print("\n=== Loading Structured Output ===")
    structured = get_structured_output_response()
    
    print("\n=== Loading Tool Call Response ===")
    tool_response = get_tool_call_response()
    
    print("\n=== Loading Streaming Structured Output Response ===")
    print("Streaming structured output chunks:")
    for event in get_streaming_structured_output_response():
        event_type = event.type if hasattr(event, 'type') else type(event).__name__
        if event_type == "content_block_delta":
            if hasattr(event, 'delta'):
                delta = event.delta
                if hasattr(delta, 'type'):
                    if delta.type == "text_delta" and hasattr(delta, 'text'):
                        print(f"{delta.text}", end="", flush=True)
                    elif delta.type == "thinking_delta":
                        pass
        elif event_type in ["message_start", "content_block_start", "content_block_stop", "message_delta", "message_stop"]:
            print(f"\n[{event_type}]", end="")
        elif isinstance(event, dict):
            if event.get("type") == "thinking":
                pass
    print("\n")
    
    print("\n=== Loading Streaming Tool Call Response ===")
    print("Streaming tool call chunks:")
    for event in get_streaming_tool_call_response():
        event_type = event.type if hasattr(event, 'type') else type(event).__name__
        if event_type == "content_block_delta":
            if hasattr(event, 'delta'):
                delta = event.delta
                if hasattr(delta, 'type'):
                    if delta.type == "text_delta" and hasattr(delta, 'text'):
                        print(f"{delta.text}", end="", flush=True)
                    elif delta.type == "thinking_delta":
                        pass
        elif event_type in ["message_start", "content_block_start", "content_block_stop", "message_delta", "message_stop"]:
            print(f"\n[{event_type}]", end="")
        elif isinstance(event, dict):
            if event.get("type") == "thinking":
                pass
    print("\n")
    
    print("\n=== Loading Raw Dict ===")
    raw = get_raw_dict("simple_text")
    print(f"Raw dict keys: {raw.keys()}")
