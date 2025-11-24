# Output Formats

Complete reference for the output structure of each method in StreamShape.

## Overview

All methods (except `structured_streaming_output`) return a consistent dictionary format with two keys:
- `data`: The actual content/result
- `raw_chunks`: The raw API response object

## Table of Contents

1. [Generate Method](#generate-method)
2. [Stream Method](#stream-method)
3. [Tool Call Method](#tool-call-method)
4. [Structured Output Method](#structured-output-method)
5. [Structured Streaming Output Method](#structured-streaming-output-method)

---

## Generate Method

Returns complete text response all at once.

### Output Structure

```json
{
    "data": "string - The generated text content",
    "raw_chunks": "object - Raw API response object"
}
```

### Example Usage

```python
from streamshape import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.generate(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What is Python?"
)

# Access the generated text
print(response["data"])
# Output: "Python is a high-level, interpreted programming language..."

# Access raw API response (for debugging)
print(response["raw_chunks"])
# Output: ChatCompletion(id='chatcmpl-...', choices=[...], ...)
```

### Complete Example Output

```json
{
    "data": "Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
    "raw_chunks": {
        "id": "chatcmpl-abc123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Python is a high-level, interpreted programming language..."
                },
                "finish_reason": "stop"
            }
        ]
    }
}
```

---

## Stream Method

Yields text chunks as they're generated in real-time.

### Output Structure (Per Chunk)

```json
{
    "data": "string - Text chunk (empty string if None)",
    "raw_chunks": "object - Raw streaming chunk object"
}
```

### Example Usage

```python
from streamshape import OpenAI

client = OpenAI(api_key="your-api-key")

for chunk in client.stream(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="Write a haiku about coding"
):
    # Access the text chunk
    print(chunk["data"], end="", flush=True)
    
    # Access raw chunk (for debugging)
    # print(chunk["raw_chunks"])
```

### Complete Example Output (Per Chunk)

**Chunk 1:**
```json
{
    "data": "Code",
    "raw_chunks": {
        "id": "chatcmpl-abc123",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "content": "Code"
                },
                "finish_reason": null
            }
        ]
    }
}
```

**Chunk 2:**
```json
{
    "data": " flows",
    "raw_chunks": {
        "id": "chatcmpl-abc123",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "delta": {
                    "content": " flows"
                },
                "finish_reason": null
            }
        ]
    }
}
```

**Chunk 3:**
```json
{
    "data": " like",
    "raw_chunks": {
        "id": "chatcmpl-abc123",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "delta": {
                    "content": " like"
                },
                "finish_reason": null
            }
        ]
    }
}
```

**Final Chunk:**
```json
{
    "data": "",
    "raw_chunks": {
        "id": "chatcmpl-abc123",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }
        ]
    }
}
```

### Collecting Full Response

```python
full_response = ""
for chunk in client.stream(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="Write a haiku"
):
    full_response += chunk["data"]
    print(chunk["data"], end="", flush=True)

print(f"\n\nComplete response: {full_response}")
```

---

## Tool Call Method

Returns function/tool call information.

### Output Structure

```json
{
    "data": {
        "tool_name": "string - Name of the tool/function to call",
        "arguments": "string - JSON string of arguments"
    },
    "raw_chunks": "object - Raw API response object"
}
```

### Example Usage

```python
from streamshape import OpenAI

client = OpenAI(api_key="your-api-key")

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
    }
}]

result = client.tool_call(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What's the weather in Paris?",
    tools=tools
)

# Access tool call data
print(result["data"]["tool_name"])
# Output: "get_weather"

print(result["data"]["arguments"])
# Output: '{"location": "Paris", "unit": "celsius"}'

# Parse arguments
import json
args = json.loads(result["data"]["arguments"])
print(args["location"])  # "Paris"
```

### Complete Example Output

```json
{
    "data": {
        "tool_name": "get_weather",
        "arguments": "{\"location\": \"Paris\", \"unit\": \"celsius\"}"
    },
    "raw_chunks": {
        "id": "chatcmpl-abc123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": null,
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "arguments": "{\"location\": \"Paris\", \"unit\": \"celsius\"}"
                            }
                        }
                    ]
                },
                "finish_reason": "tool_calls"
            }
        ]
    }
}
```

### Executing the Tool Call

```python
import json

# Define actual function
def get_weather(location, unit="celsius"):
    # In real app, call weather API
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "condition": "Sunny"
    }

# Get tool call from LLM
result = client.tool_call(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What's the weather in Paris?",
    tools=tools
)

# Execute the function
tool_name = result["data"]["tool_name"]
arguments = json.loads(result["data"]["arguments"])

if tool_name == "get_weather":
    weather_data = get_weather(**arguments)
    print(weather_data)
    # Output: {"location": "Paris", "temperature": 22, "condition": "Sunny"}
```

---

## Structured Output Method

Returns validated Pydantic objects all at once.

### Output Structure

```json
{
    "data": ["array - List of validated Pydantic objects"],
    "raw_chunks": "object - Raw API response object"
}
```

### Example Usage

```python
from streamshape import OpenAI
from pydantic import BaseModel
from typing import List

client = OpenAI(api_key="your-api-key")

# Define schema
class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    steps: List[str]
    prep_time_minutes: int

result = client.structured_output(
    model="gpt-4",
    system_prompt="You are a chef.",
    user_prompt="Give me 2 simple pasta recipes",
    output_schema=Recipe
)

# Access the list of validated objects
for recipe in result["data"]:
    print(f"Recipe: {recipe.name}")
    print(f"Ingredients: {', '.join(recipe.ingredients)}")
    print(f"Prep time: {recipe.prep_time_minutes} minutes")
    print()

# Access raw response (for debugging)
# print(result["raw_chunks"])
```

### Complete Example Output

```json
{
    "data": [
        {
            "name": "Spaghetti Aglio e Olio",
            "ingredients": [
                "400g spaghetti",
                "6 cloves garlic",
                "1/2 cup olive oil",
                "Red pepper flakes",
                "Fresh parsley",
                "Salt"
            ],
            "steps": [
                "Boil pasta in salted water until al dente",
                "Slice garlic thinly",
                "Heat olive oil and sauté garlic until golden",
                "Add red pepper flakes",
                "Toss pasta with garlic oil",
                "Garnish with parsley"
            ],
            "prep_time_minutes": 20
        },
        {
            "name": "Pasta Carbonara",
            "ingredients": [
                "400g spaghetti",
                "200g pancetta",
                "4 egg yolks",
                "100g Parmesan cheese",
                "Black pepper",
                "Salt"
            ],
            "steps": [
                "Cook pasta in salted water",
                "Fry pancetta until crispy",
                "Mix egg yolks with grated Parmesan",
                "Drain pasta, reserving pasta water",
                "Mix hot pasta with pancetta",
                "Remove from heat, add egg mixture",
                "Add pasta water to create creamy sauce",
                "Season with black pepper"
            ],
            "prep_time_minutes": 25
        }
    ],
    "raw_chunks": {
        "id": "chatcmpl-abc123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "[{\"name\": \"Spaghetti Aglio e Olio\", ...}, ...]"
                },
                "finish_reason": "stop"
            }
        ]
    }
}
```

### Accessing Individual Fields

```python
result = client.structured_output(
    model="gpt-4",
    system_prompt="You are a chef.",
    user_prompt="Give me 2 simple pasta recipes",
    output_schema=Recipe
)

# Get first recipe
first_recipe = result["data"][0]
print(first_recipe.name)                    # "Spaghetti Aglio e Olio"
print(first_recipe.ingredients[0])          # "400g spaghetti"
print(first_recipe.prep_time_minutes)       # 20

# Convert to dict
recipe_dict = first_recipe.model_dump()
print(recipe_dict)
# Output: {"name": "Spaghetti Aglio e Olio", "ingredients": [...], ...}

# Convert to JSON
recipe_json = first_recipe.model_dump_json()
print(recipe_json)
# Output: '{"name": "Spaghetti Aglio e Olio", ...}'
```

### Complex Schema Example

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int = Field(gt=0, lt=150)
    email: str
    address: Address
    hobbies: List[str]
    phone: Optional[str] = None

result = client.structured_output(
    model="gpt-4",
    system_prompt="Generate fictional person data.",
    user_prompt="Create 3 people with complete information",
    output_schema=Person
)
```

**Output structure:**
```json
{
    "data": [
        {
            "name": "John Doe",
            "age": 32,
            "email": "john@example.com",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "country": "USA"
            },
            "hobbies": ["reading", "hiking", "photography"],
            "phone": "+1-555-0123"
        }
    ],
    "raw_chunks": {
        "id": "chatcmpl-abc123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4"
    }
}
```

---

## Structured Streaming Output Method

Yields validated Pydantic objects as they're generated (streaming) with token usage tracking.

### Output Structure (Per Chunk)

```python
{
    "data": BaseModel or None,  # Validated Pydantic object (None for final chunk)
    "usage": dict,              # Token usage statistics (populated in final chunk)
    "finished": bool,           # True for final chunk
    "raw_chunks": list          # List of raw response chunks (only in final chunk)
}
```

### Example Usage

```python
from streamshape import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key="your-api-key")

class Task(BaseModel):
    title: str
    priority: str
    estimated_hours: int
    description: str

final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 5 tasks for building a website",
    output_schema=Task
):
    # Extract data and usage
    task = result.get("data")
    usage = result.get("usage")
    
    # Store usage data if present
    if usage:
        final_usage = usage
    
    # Skip final chunk (no data, just usage)
    if not task:
        continue
    
    print(f"📋 {task.title}")
    print(f"   Priority: {task.priority}")
    print(f"   Hours: {task.estimated_hours}")
    print(f"   Description: {task.description}")
    print()

# Display token usage
if final_usage:
    print(f"📊 Token Usage:")
    print(f"   Prompt tokens: {final_usage.get('prompt_tokens')}")
    print(f"   Completion tokens: {final_usage.get('completion_tokens')}")
    print(f"   Total tokens: {final_usage.get('total_tokens')}")
```

### Complete Example Output (Per Yielded Chunk)

**First chunk (with data):**
```json
{
    "data": {
        "title": "Design Homepage Layout",
        "priority": "high",
        "estimated_hours": 8,
        "description": "Create wireframes and mockups for the main landing page"
    },
    "usage": {},
    "finished": false
}
```

**Second chunk (with data):**
```json
{
    "data": {
        "title": "Set Up Database Schema",
        "priority": "high",
        "estimated_hours": 6,
        "description": "Design and implement database tables for user data and content"
    },
    "usage": {},
    "finished": false
}
```

**Third chunk (with data):**
```json
{
    "data": {
        "title": "Implement User Authentication",
        "priority": "high",
        "estimated_hours": 12,
        "description": "Build login, registration, and password reset functionality"
    },
    "usage": {},
    "finished": false
}
```

**Final chunk (with usage, no data):**
```json
{
    "data": null,
    "usage": {
        "prompt_tokens": 45,
        "completion_tokens": 320,
        "total_tokens": 365,
        "completion_tokens_details": {
            "reasoning_tokens": 0,
            "accepted_prediction_tokens": null,
            "rejected_prediction_tokens": null
        },
        "prompt_tokens_details": {
            "cached_tokens": 0,
            "audio_tokens": null
        }
    },
    "finished": true,
    "raw_chunks": [...]
}
```

### Collecting All Objects

```python
from pydantic import BaseModel
from typing import List

class Task(BaseModel):
    title: str
    priority: str
    estimated_hours: int

# Collect all tasks
all_tasks: List[Task] = []
final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 5 tasks for building a website",
    output_schema=Task
):
    # Extract data and usage
    task = result.get("data")
    usage = result.get("usage")
    
    # Store usage data
    if usage:
        final_usage = usage
    
    # Skip if no data
    if not task:
        continue
    
    all_tasks.append(task)
    print(f"Received task: {task.title}")

print(f"\nTotal tasks: {len(all_tasks)}")

# Access collected tasks
for i, task in enumerate(all_tasks, 1):
    print(f"{i}. {task.title} ({task.priority})")

# Display usage
if final_usage:
    print(f"\n📊 Total tokens: {final_usage.get('total_tokens')}")
```

### Real-time Processing Example

```python
from pydantic import BaseModel
import time

class Article(BaseModel):
    title: str
    category: str
    word_count: int
    summary: str

def process_article(article: Article):
    """Process each article as it arrives"""
    print(f"\n📰 Processing: {article.title}")
    print(f"   Category: {article.category}")
    print(f"   Words: {article.word_count}")
    
    # Simulate saving to database
    time.sleep(0.5)
    print(f"   ✅ Saved to database")

# Process articles in real-time
final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a content writer.",
    user_prompt="Write 3 blog article ideas about AI",
    output_schema=Article
):
    # Extract data and usage
    article = result.get("data")
    usage = result.get("usage")
    
    # Store usage data
    if usage:
        final_usage = usage
    
    # Skip if no data
    if not article:
        continue
    
    process_article(article)

if final_usage:
    print(f"\n📊 Token Usage: {final_usage.get('total_tokens')} tokens")
```

---

## Comparison Table

| Method | Returns | Data Access | Raw Access | Usage Tracking | Streaming |
|--------|---------|-------------|------------|----------------|-----------|
| `generate()` | `dict` | `result["data"]` | `result["raw_chunks"]` | ❌ | ❌ |
| `stream()` | `dict` (per chunk) | `chunk["data"]` | `chunk["raw_chunks"]` | ❌ | ✅ |
| `tool_call()` | `dict` | `result["data"]` | `result["raw_chunks"]` | ❌ | ❌ |
| `structured_output()` | `dict` | `result["data"]` | `result["raw_chunks"]` | ❌ | ❌ |
| `structured_streaming_output()` | `dict` (per chunk) | `result["data"]` | `result["raw_chunks"]` | ✅ | ✅ |

---

## Migration from Old Format

If you're upgrading from an older version, here's how to update your code:

### Generate Method

```python
# Old format
response = client.generate(...)
print(response)  # Was a string

# New format
result = client.generate(...)
print(result["data"])  # Now access via ["data"]
```

### Stream Method

```python
# Old format
for chunk in client.stream(...):
    print(chunk, end="")  # Was a string

# New format
for chunk in client.stream(...):
    print(chunk["data"], end="")  # Now access via ["data"]
```

### Tool Call Method

```python
# Old format
result = client.tool_call(...)
print(result["tool_name"])  # Direct access

# New format
result = client.tool_call(...)
print(result["data"]["tool_name"])  # Nested under ["data"]
```

### Structured Output Method

```python
# Old format
objects = client.structured_output(...)
for obj in objects:  # Was a list
    print(obj.field)

# New format
result = client.structured_output(...)
for obj in result["data"]:  # Now access via ["data"]
    print(obj.field)
```

### Structured Streaming Output Method

```python
# Old format
for obj in client.structured_streaming_output(...):
    print(obj.field)  # Was a direct Pydantic object

# New format
for result in client.structured_streaming_output(...):
    obj = result.get("data")  # Now access via ["data"]
    usage = result.get("usage")  # Token usage available
    
    if obj:  # Skip final chunk with just usage
        print(obj.field)
```

---

## Benefits of New Format

1. **Consistency**: All methods now use the same dictionary structure
2. **Token Tracking**: `structured_streaming_output()` now includes usage data for cost monitoring
3. **Debugging**: Access raw API responses when needed
4. **Flexibility**: Can inspect metadata without parsing raw responses
5. **Future-proof**: Easy to add new fields without breaking changes

## See Also

- [Usage Guide](usage.md) - Detailed usage examples
- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - Real-world use cases
- [CHANGELOG_RESPONSE_FORMAT.md](../CHANGELOG_RESPONSE_FORMAT.md) - Detailed changelog

