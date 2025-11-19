import os
import json
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize client
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)
model = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash-exp")

# Directory for saving raw data
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..","..","raw_data", "google")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

def save_raw_response(response_type: str, data: dict):
    """Save raw API response to JSON file"""

    filename = f"{response_type}.json"
    filepath = os.path.join(RAW_DATA_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Saved raw response to: {filepath}")
    return filepath


def _extract_chunk_text(chunk):
    if not chunk:
        return ""
    text = getattr(chunk, "text", None)
    if text:
        return text
    if hasattr(chunk, "candidates") and chunk.candidates:
        candidate = chunk.candidates[0]
        if candidate.content and candidate.content.parts:
            part_texts = [getattr(part, "text", "") for part in candidate.content.parts]
            return "".join(filter(None, part_texts))
    return ""

# --- 1️⃣ Plain text call ---
def simple_text_call(prompt: str, model_name: str = model):
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    
    # Save raw response (convert to dict-like structure)
    save_raw_response("simple_text",response.model_dump() )
    
    print(response.text)

# --- 2️⃣ Streaming text call ---
def streaming_call(prompt: str, model_name: str = model):
    print("--- Streaming Output ---")
    
    chunks = []
    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=prompt
    ):
        chunks.append(chunk.model_dump())
        print(chunk.text, end="", flush=True)
    
    # Save all chunks
    save_raw_response("streaming", chunks)
    
    print("\n--- Stream End ---")

# --- 3️⃣ Structured output (JSON schema enforced) ---
def structured_output_call(prompt: str, model_name: str = model):
    enhanced_prompt = f"{prompt}\n\nProvide weather information for exactly 5 major cities. Each entry should have city name, temperature in Celsius, and weather condition."
    response = client.models.generate_content(
        model=model_name,
        contents=enhanced_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "cities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string"},
                                "temperature_c": {"type": "number"},
                                "condition": {"type": "string"}
                            },
                            "required": ["city", "temperature_c", "condition"]
                        }
                    }
                },
                "required": ["cities"]
            }
        )
    )
    
    # Save raw response
    save_raw_response("structured_output", response.model_dump())
    
    data = json.loads(response.text)
    return data


def streaming_structured_output_call(prompt: str, model_name: str = model):
    enhanced_prompt = f"{prompt}\n\nProvide weather information for exactly 5 major cities. Each entry should have city name, temperature in Celsius, and weather condition."
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "cities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"},
                            "temperature_c": {"type": "number"},
                            "condition": {"type": "string"}
                        },
                        "required": ["city", "temperature_c", "condition"]
                    }
                }
            },
            "required": ["cities"]
        }
    )

    print("--- Streaming Structured Output ---")
    chunks = []
    buffer = []

    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=enhanced_prompt,
        config=config
    ):
        chunks.append(chunk.model_dump())
        text = _extract_chunk_text(chunk)
        if text:
            buffer.append(text)
            print(text, end="", flush=True)

    save_raw_response("streaming_structured_output", chunks)

    print("\n--- Stream End ---")
    payload = "".join(buffer).strip()
    if not payload:
        return {}

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        print("⚠️ Unable to decode structured output stream into JSON.")
        return {"raw": payload}

# --- 4️⃣ Tool call (function call) ---
def tool_call_example(prompt: str, model_name: str = model):
    # Define tool
    get_weather_tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_weather",
                description="Get weather info for a city.",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "The city name"}
                    },
                    "required": ["city"]
                }
            )
        ]
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[get_weather_tool]
        )
    )

    # Save raw response
    save_raw_response("tool_call",response.model_dump())

    # Check if tool was called
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    print(f"Tool called: {fc.name}({dict(fc.args)})")
                    # Simulate tool result
                    return {
                        "city": fc.args.get("city"),
                        "temperature": 25,
                        "condition": "Sunny"
                    }
    
    # If no tool was called, return text response
    return response.text if hasattr(response, 'text') else str(response)


def streaming_tool_call_example(prompt: str, model_name: str = model):
    get_weather_tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_weather",
                description="Get weather info for a city.",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "The city name"}
                    },
                    "required": ["city"]
                }
            )
        ]
    )

    print("--- Streaming Tool Call ---")
    chunks = []
    collected_calls = []

    def _collect_calls(chunk_obj):
        candidates = getattr(chunk_obj, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            parts = getattr(content, "parts", None) or []
            for part in parts:
                function_call = getattr(part, "function_call", None)
                if function_call:
                    collected_calls.append(function_call)

        function_calls = getattr(chunk_obj, "function_calls", None)
        if function_calls:
            collected_calls.extend(function_calls)

    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(tools=[get_weather_tool])
    ):
        chunks.append(chunk.model_dump())
        text = _extract_chunk_text(chunk)
        if text:
            print(text, end="", flush=True)
        _collect_calls(chunk)

    save_raw_response("streaming_tool_call", {"chunks": chunks})
    print("\n--- Stream End ---")

    results = []
    for call in collected_calls:
        name = getattr(call, "name", None)
        args_mapping = getattr(call, "args", {})
        args = dict(args_mapping) if hasattr(args_mapping, "items") else args_mapping
        if name == "get_weather" and isinstance(args, dict) and "city" in args:
            print(f"Tool called: get_weather({args})")
            results.append({"city": args.get("city"), "temperature": 25, "condition": "Sunny"})
        else:
            results.append({"tool": name, "arguments": args})

    return results

# Example usage
if __name__ == "__main__":
    print("\n=== Simple Text ===")
    simple_text_call("Tell me a joke about AI.")

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
