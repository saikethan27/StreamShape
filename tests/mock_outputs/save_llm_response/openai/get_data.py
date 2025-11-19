import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize client (base_url can be customized)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)
model = os.getenv("OPENAI_MODEL")

# Directory for saving raw data
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..","..", "raw_data", "openai")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

def save_raw_response(response_type: str, data: dict):
    """Save raw API response to JSON file"""
    filename = f"{response_type}.json"
    filepath = os.path.join(RAW_DATA_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Saved raw response to: {filepath}")
    return filepath


def _extract_delta_text(content):
    """Normalize streamed delta content into plain text."""
    if not content:
        return ""
    if isinstance(content, str):
        return content

    text_parts = []
    try:
        iterator = content if isinstance(content, (list, tuple)) else [content]
        for part in iterator:
            if part is None:
                continue
            text_value = getattr(part, "text", None)
            if text_value:
                text_parts.append(text_value)
            elif isinstance(part, dict) and part.get("text"):
                text_parts.append(part["text"])
    except TypeError:
        pass

    return "".join(text_parts)
# --- 1️⃣ Plain text call ---
def simple_text_call(prompt: str, model: str = model):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Save raw response
    save_raw_response("simple_text", response.model_dump())
    
    return response.choices[0].message.content

# --- 2️⃣ Streaming text call ---
def streaming_call(prompt: str, model: str = model):
    print("--- Streaming Output ---")
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    chunks = []
    for chunk in stream:
        chunks.append(chunk.model_dump())
        if chunk.choices:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
    
    # Save all chunks
    save_raw_response("streaming", {"chunks": chunks})
    
    print("\n--- Stream End ---")

# --- 3️⃣ Structured output (JSON schema enforced) ---
def structured_output_call(prompt: str, model: str = model):
    schema = {
        "name": "weather_cities",
        "schema": {
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
                    },
                    "description": "List of cities with weather information"
                }
            },
            "required": ["cities"]
        }
    }

    enhanced_prompt = f"{prompt}\n\nProvide weather information for exactly 5 major cities. Each entry should have city name, temperature in Celsius, and weather condition."
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": enhanced_prompt}],
        response_format={"type": "json_schema", "json_schema": schema}
    )

    # Save raw response
    save_raw_response("structured_output", response.model_dump())

    data = json.loads(response.choices[0].message.content)
    return data


def streaming_structured_output_call(prompt: str, model: str = model):
    schema = {
        "name": "weather_cities",
        "schema": {
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
                    },
                    "description": "List of cities with weather information"
                }
            },
            "required": ["cities"]
        }
    }

    print("--- Streaming Structured Output ---")
    enhanced_prompt = f"{prompt}\n\nProvide weather information for exactly 5 major cities. Each entry should have city name, temperature in Celsius, and weather condition."
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": enhanced_prompt}],
        response_format={"type": "json_schema", "json_schema": schema},
        stream=True
    )

    chunks = []
    buffer = []
    for chunk in stream:
        chunks.append(chunk.model_dump())
        if chunk.choices:
            delta = chunk.choices[0].delta
            if delta.content:
                piece = _extract_delta_text(delta.content)
                if piece:
                    buffer.append(piece)
                    print(piece, end="", flush=True)

    save_raw_response("streaming_structured_output", {"chunks": chunks})

    print("\n--- Stream End ---")
    payload = "".join(buffer).strip()
    if not payload:
        return {}

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        print("⚠️ Unable to decode structured output stream into JSON.")
        return {"raw": payload}

# --- 4️⃣ Tool call (function call simulation) ---
def tool_call_example(prompt: str, model: str = model):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather info for a city.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
        tool_choice="auto"
    )

    # Save raw response
    save_raw_response("tool_call", response.model_dump())

    message = response.choices[0].message

    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "get_weather":
                args = json.loads(tool_call.function.arguments)
                print(f"Tool called: get_weather({args})")
                # Simulate tool result
                return {"city": args["city"], "temperature": 25, "condition": "Sunny"}
    else:
        return message.content


def streaming_tool_call_example(prompt: str, model: str = model):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather info for a city.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    print("--- Streaming Tool Call ---")
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}] ,
        tools=tools,
        tool_choice="auto",
        stream=True
    )

    chunks = []
    partial_calls = {}
    for chunk in stream:
        chunks.append(chunk.model_dump())
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta
        if delta.content:
            text_piece = _extract_delta_text(delta.content)
            if text_piece:
                print(text_piece, end="", flush=True)

        tool_deltas = getattr(delta, "tool_calls", None)
        if not tool_deltas:
            continue

        for tool_delta in tool_deltas:
            index = getattr(tool_delta, "index", 0)
            call = partial_calls.setdefault(index, {"name": None, "arguments": ""})

            function_data = getattr(tool_delta, "function", None)
            if isinstance(tool_delta, dict):
                function_data = tool_delta.get("function")
                index = tool_delta.get("index", index)
                call = partial_calls.setdefault(index, {"name": None, "arguments": ""})

            if function_data:
                name = getattr(function_data, "name", None) or (function_data.get("name") if isinstance(function_data, dict) else None)
                if name:
                    call["name"] = name

                arguments = getattr(function_data, "arguments", None)
                if isinstance(function_data, dict):
                    arguments = function_data.get("arguments")
                if arguments:
                    call["arguments"] += arguments

    save_raw_response("streaming_tool_call", {"chunks": chunks, "tool_calls": partial_calls})
    print("\n--- Stream End ---")

    results = []
    for _, data in sorted(partial_calls.items()):
        if not data["name"]:
            continue
        arguments = data.get("arguments", "{}")
        try:
            parsed_args = json.loads(arguments)
        except json.JSONDecodeError:
            parsed_args = {"raw": arguments}

        if data["name"] == "get_weather" and "city" in parsed_args:
            print(f"Tool called: get_weather({parsed_args})")
            results.append({"city": parsed_args["city"], "temperature": 25, "condition": "Sunny"})
        else:
            results.append({"tool": data["name"], "arguments": parsed_args})

    return results

# --- 5️⃣ MCP tool call (Model Context Protocol) ---
def mcp_tool_call_example(prompt: str, model: str = model):
    """
    MCP (Model Context Protocol) servers use OpenAI-compatible API format.
    This example demonstrates calling MCP tools which follow the same pattern.
    """
    # MCP tools follow OpenAI function calling format
    mcp_tools = [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read contents of a file from the filesystem.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The file path to read"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "List contents of a directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The directory path to list"
                        }
                    },
                    "required": ["path"]
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        tools=mcp_tools,
        tool_choice="auto"
    )

    # Save raw response
    save_raw_response("mcp_tool_call", response.model_dump())

    message = response.choices[0].message

    if message.tool_calls:
        results = []
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            print(f"MCP Tool called: {tool_call.function.name}({args})")
            
            # Simulate MCP tool results
            if tool_call.function.name == "read_file":
                results.append({
                    "tool": "read_file",
                    "path": args["path"],
                    "content": "Mock file content..."
                })
            elif tool_call.function.name == "list_directory":
                results.append({
                    "tool": "list_directory",
                    "path": args["path"],
                    "files": ["file1.txt", "file2.py", "folder/"]
                })
        return results
    else:
        return message.content

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

    print("\n=== MCP Tool Call ===")
    print(mcp_tool_call_example("List the files in the current directory."))