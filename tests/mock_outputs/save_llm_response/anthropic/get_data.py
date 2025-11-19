import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize client
client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
)
model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
# model = "claude-sonnet-4-5"
# model_2 = "claude-haiku-4-5"
# Directory for saving raw data
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..","..","raw_data", "anthropic")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

def save_raw_response(response_type: str, data: dict):
    """Save raw API response to JSON file"""

    filename = f"{response_type}.json"
    filepath = os.path.join(RAW_DATA_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Saved raw response to: {filepath}")
    return filepath

# --- 1️⃣ Plain text call ---
def simple_text_call(prompt: str, model: str = model_2):
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Save raw response
    save_raw_response("simple_text", message.model_dump())
    
    # Extract text from content blocks (handle thinking blocks)
    for block in message.content:
        if block.type == "text":
            return block.text
    return None

# --- 2️⃣ Streaming text call ---
def streaming_call(prompt: str, model: str = model_2):
    print("--- Streaming Output ---")
    
    stream_events = []
    
    # Use the raw stream to capture all events
    with client.messages.stream(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        # Iterate through ALL raw events from the stream
        for event in stream:
            stream_events.append(event.model_dump())
            # Save each event exactly as received
            # event_dict = {
            #     "type": event.type if hasattr(event, 'type') else str(type(event).__name__),
            #     "data": event.model_dump() if hasattr(event, 'model_dump') else str(event)
            # }
            # stream_events.append(event_dict)
            
            # Print text chunks for visual feedback
            if hasattr(event, 'type'):
                if event.type == "content_block_delta":
                    if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                        print(event.delta.text, end="", flush=True)
    
    # Save all streaming events exactly as received
    save_raw_response("streaming", {"events": stream_events})
    
    print("\n--- Stream End ---")

# --- 3️⃣ Structured output (JSON schema enforced) ---
def structured_output_call(prompt: str, model: str = model):
    instruction = f"{prompt}\n\nProvide weather information for exactly 5 major cities. Return a JSON object with a 'cities' array. Each city object should have 'city' (name), 'temperature_c' (number), and 'condition' (string) fields. Example format: {{\"cities\": [{{\"city\": \"Tokyo\", \"temperature_c\": 15, \"condition\": \"Cloudy\"}}]}}"
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": instruction}]
    )
    
    # Save raw response
    save_raw_response("structured_output", message.model_dump())
    
    # Extract and parse JSON from response
    # Find text block in content
    content = None
    for block in message.content:
        if block.type == "text":
            content = block.text
            break
    
    if not content:
        return {"error": "No text content in response"}
    
    # Try to find JSON in the response
    try:
        # Anthropic may wrap JSON in markdown code blocks
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        data = json.loads(json_str)
        return data
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Failed to parse JSON: {e}")
        return {"raw_response": content}


def streaming_structured_output_call(prompt: str, model: str = model):
    print("--- Streaming Structured Output ---")

    stream_events = []
    text_buffer = []
    instruction = f"{prompt}\n\nProvide weather information for exactly 5 major cities. Return a JSON object with a 'cities' array. Each city object should have 'city' (name), 'temperature_c' (number), and 'condition' (string) fields. Example format: {{\"cities\": [{{\"city\": \"Tokyo\", \"temperature_c\": 15, \"condition\": \"Cloudy\"}}]}}"

    with client.messages.stream(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": instruction}]
    ) as stream:
        for event in stream:
            stream_events.append(event.model_dump())
            if getattr(event, "type", None) == "content_block_delta":
                delta = getattr(event, "delta", None)
                if delta and getattr(delta, "text", None):
                    text_buffer.append(delta.text)
                    print(delta.text, end="", flush=True)

    save_raw_response("streaming_structured_output", {"events": stream_events})

    print("\n--- Stream End ---")
    payload = "".join(text_buffer).strip()
    if not payload:
        return {}

    try:
        if "```json" in payload:
            json_str = payload.split("```json")[1].split("```")[0].strip()
        elif "```" in payload:
            json_str = payload.split("```")[1].split("```")[0].strip()
        else:
            json_str = payload
        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError) as exc:
        print(f"Failed to parse streaming JSON: {exc}")
        return {"raw_response": payload}

# --- 4️⃣ Tool call (function call) ---
def tool_call_example(prompt: str, model: str = model):
    tools = [
        {
            "name": "get_weather",
            "description": "Get weather info for a city.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        }
    ]

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=tools
    )

    # Save raw response
    save_raw_response("tool_call", message.model_dump())

    # Check if tool was called
    for content_block in message.content:
        if content_block.type == "tool_use":
            print(f"Tool called: {content_block.name}({content_block.input})")
            # Simulate tool result
            return {
                "city": content_block.input.get("city"),
                "temperature": 25,
                "condition": "Sunny"
            }
    
    # If no tool was called, return text response
    for block in message.content:
        if block.type == "text":
            return block.text
    return None


def streaming_tool_call_example(prompt: str, model: str = model):
    tools = [
        {
            "name": "get_weather",
            "description": "Get weather info for a city.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        }
    ]

    print("--- Streaming Tool Call ---")
    stream_events = []
    partial_calls = {}

    with client.messages.stream(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=tools
    ) as stream:
        for event in stream:
            stream_events.append(event.model_dump())

            event_type = getattr(event, "type", None)
            if event_type == "content_block_delta":
                delta = getattr(event, "delta", None)
                if delta and getattr(delta, "text", None):
                    print(delta.text, end="", flush=True)

                partial_json = getattr(delta, "partial_json", None)
                if partial_json is not None:
                    call_state = partial_calls.setdefault(event.index, {"name": None, "arguments": ""})
                    call_state["arguments"] += partial_json

            elif event_type == "content_block_start":
                block = getattr(event, "content_block", None)
                if block and block.type == "tool_use":
                    partial_calls[event.index] = {
                        "name": block.name,
                        "arguments": ""
                    }

    save_raw_response("streaming_tool_call", {"events": stream_events})

    print("\n--- Stream End ---")
    results = []
    for data in partial_calls.values():
        if not data.get("name"):
            continue
        arguments_raw = data.get("arguments", "{}")
        try:
            parsed_args = json.loads(arguments_raw)
        except json.JSONDecodeError:
            parsed_args = {"raw": arguments_raw}

        if data["name"] == "get_weather" and isinstance(parsed_args, dict) and "city" in parsed_args:
            print(f"Tool called: get_weather({parsed_args})")
            results.append({"city": parsed_args.get("city"), "temperature": 25, "condition": "Sunny"})
        else:
            results.append({"tool": data["name"], "arguments": parsed_args})

    return results

# Example usage
if __name__ == "__main__":
    print("\n=== Simple Text ===")
    print(simple_text_call("Tell me a joke about AI."))

    print("\n=== Streaming ===")
    streaming_call("Explain quantum computing simply.")

    print("\n=== Structured Output ===")
    print(structured_output_call("What's the weather in Tokyo?"))

    print("\n=== Streaming Structured Output ===")
    print(streaming_structured_output_call("Stream the weather in Paris."))

    print("\n=== Tool Call ===")
    print(tool_call_example("Get me the weather in Berlin."))

    print("\n=== Streaming Tool Call ===")
    print(streaming_tool_call_example("Stream the weather request for Rome."))
