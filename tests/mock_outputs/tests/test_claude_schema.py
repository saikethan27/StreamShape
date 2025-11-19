import anthropic
import json
from typing import Dict, Any, List
import sys
import os

# Add project root to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from providers_schema.anthropic_schema import (
    ClaudeMessage, ClaudeUsage, ClaudeContentBlock,
    ClaudeTextBlock, ClaudeToolUseBlock, ClaudeStreamingEvent,
    ClaudeThinkingBlock
)

from mock_outputs.mock_data import anthropic

# Schema validation helper
def validate_and_parse_message(raw_response: Dict[str, Any]) -> ClaudeMessage:
    """Validate and parse API response using ClaudeMessage schema"""
    try:
        parsed_message = ClaudeMessage(**raw_response)
        print("OK Schema validation successful")
        return parsed_message
    except Exception as e:
        print(f"ERROR Schema validation failed: {e}")
        raise

# Streaming event validation helper
def validate_and_parse_streaming_event(event_data: Dict[str, Any]) -> ClaudeStreamingEvent:
    """Validate and parse streaming event using ClaudeStreamingEvent schema"""
    try:
        parsed_event = ClaudeStreamingEvent(**event_data)
        return parsed_event
    except Exception as e:
        print(f"ERROR Schema validation failed: {e}")
        raise

# Simple text response test
def test_simple_text():
    """Test basic text response"""
    print("=== Testing Simple Text Response ===")


    message = anthropic.get_simple_text_response()

    # Convert to dict and validate with schema
    print("\n--- Raw API Response ---")
    raw_dict = message.model_dump()
    print(f"Raw type: {type(message)}")
    print(f"Raw dict keys: {raw_dict.keys()}")

    # Parse through our schema
    print("\n--- Validating with ClaudeMessage Schema ---")
    validated_message = validate_and_parse_message(raw_dict)

    # Display parsed data
    print(f"\nOK Validated Message ID: {validated_message.id}")
    print(f"OK Validated Type: {validated_message.type}")
    print(f"OK Validated Role: {validated_message.role}")
    print(f"OK Validated Model: {validated_message.model}")
    print(f"OK Validated Stop Reason: {validated_message.stop_reason}")

    # Validate Usage
    if validated_message.usage:
        print(f"\nOK Usage validated:")
        print(f"  - Input tokens: {validated_message.usage.input_tokens}")
        print(f"  - Output tokens: {validated_message.usage.output_tokens}")

    # Validate Content Blocks
    print(f"\nOK Content blocks count: {len(validated_message.content)}")
    for i, block in enumerate(validated_message.content):
        print(f"\nOK Content Block {i+1}:")
        print(f"  - Type: {block.type}")
        if block.type == "thinking" and hasattr(block, 'thinking'):
            thinking_preview = block.thinking[:100] + "..." if block.thinking and len(block.thinking) > 100 else block.thinking
            print(f"  - Thinking: {thinking_preview}")
        elif block.type == "text" and hasattr(block, 'text'):
            print(f"  - Text: {block.text[:100]}..." if len(block.text) > 100 else f"  - Text: {block.text}")
    print()

# Streaming response test
def test_streaming():
    """Test streaming response"""
    print("=== Testing Streaming Response ===")


    print("\n--- Validating Streaming Events with ClaudeStreamingEvent Schema ---")
    event_count = 0
    text_content = []
    stream = anthropic.get_streaming_response()
    print("Streaming response:")
    for event in stream:
        # Events are already dicts from mock response
        event_dict = event if isinstance(event, dict) else event.__dict__

        # Validate with schema
        validated_event = validate_and_parse_streaming_event(event_dict)

        # Track event types
        event_count += 1

        # Display validated event details
        event_type = event_dict.get('type')
        if event_type == "content_block_delta":
            if hasattr(validated_event, 'delta') and validated_event.delta:
                if validated_event.delta.type == "text":
                    text_content.append(validated_event.delta.text)
                    print(validated_event.delta.text, end="", flush=True)
        elif event_type == "message_delta":
            if hasattr(validated_event, 'message') and validated_event.message:
                print(f"\nOK Final message validated")
        elif event_type == "content_block_start":
            print(f"OK Content block started at index {validated_event.index}")
        elif event_type == "content_block_stop":
            print(f"OK Content block stopped at index {validated_event.index}")

    print(f"\nOK Total events processed: {event_count}")
    print(f"OK Schema validation completed successfully\n")


# Structured output test
def test_structured_output():
    """Test structured JSON output"""
    print("=== Testing Structured Output ===")


    message = anthropic.get_structured_output_response()

    # Validate with schema
    print("\n--- Validating with ClaudeMessage Schema ---")
    raw_dict = message.model_dump()
    validated_message = validate_and_parse_message(raw_dict)

    print(f"\nOK Message validated successfully")
    print(f"OK Content blocks: {len(validated_message.content)}")

    # Extract and parse JSON from text
    for block in validated_message.content:
        if block.type == "text" and block.text:
            try:
                structured_data = json.loads(block.text)
                print(f"\nOK Structured response parsed: {json.dumps(structured_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"\nOK Raw text response: {block.text}")
    print()

# Tool calling test
def test_tool_calling():
    """Test tool/function calling"""
    print("=== Testing Tool Calling ===")


    # Define a simple calculator tool
    tools = [{
        "name": "calculator",
        "description": "Perform basic arithmetic operations",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["operation", "a", "b"]
        }
    }]

    message = anthropic.get_tool_call_response()

    # Validate with schema
    print("\n--- Validating with ClaudeMessage Schema ---")
    raw_dict = message.model_dump()
    validated_message = validate_and_parse_message(raw_dict)

    print(f"\nOK Message validated successfully")
    print(f"OK Content blocks: {len(validated_message.content)}")

    for i, block in enumerate(validated_message.content):
        print(f"\nOK Block {i+1} - Type: {block.type}")
        if block.type == "text" and block.text:
            print(f"  - Text: {block.text}")
        elif block.type == "tool_use":
            print(f"  - Tool name: {block.name}")
            print(f"  - Tool ID: {block.id}")
            print(f"  - Tool input: {block.input}")
    print()




# Token usage test
def test_token_usage():
    """Test token usage tracking"""
    print("=== Testing Token Usage ===")

    message = anthropic.get_simple_text_response()

    # Validate with schema
    print("\n--- Validating with ClaudeMessage Schema ---")
    raw_dict = message.model_dump()
    validated_message = validate_and_parse_message(raw_dict)

    # Validate usage object
    print(f"\nOK Usage object validated:")
    if validated_message.usage:
        usage = validated_message.usage
        print(f"  - Input tokens: {usage.input_tokens}")
        print(f"  - Output tokens: {usage.output_tokens}")
        print(f"  - Total tokens: {usage.input_tokens + usage.output_tokens}")
        if usage.cache_creation_input_tokens:
            print(f"  - Cache creation tokens: {usage.cache_creation_input_tokens}")
        if usage.cache_read_input_tokens:
            print(f"  - Cache read tokens: {usage.cache_read_input_tokens}")
    print(f"\nOK Stop reason: {validated_message.stop_reason}\n")

# Main test runner
def run_all_tests():
    """Run all test functions"""
    print("Starting comprehensive Anthropic API tests...\n")
    print("Testing schema validation with ClaudeMessage, ClaudeUsage, and ClaudeContentBlock\n")

    test_simple_text()
    test_streaming()
    test_structured_output()
    test_tool_calling()
    test_token_usage()

    print("\n" + "="*60)
    print("All tests completed successfully!")
    print("All API responses validated against Anthropic schema")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()