# Usage Guide

Comprehensive guide to using all features of StreamShape.

## Table of Contents

1. [Basic Concepts](#basic-concepts)
2. [Method 1: Generate (Complete Text)](#method-1-generate-complete-text)
3. [Method 2: Stream (Streaming Text)](#method-2-stream-streaming-text)
4. [Method 3: Tool Call (Function Calling)](#method-3-tool-call-function-calling)
5. [Method 4: Structured Output (Complete)](#method-4-structured-output-complete)
6. [Method 5: Structured Streaming Output](#method-5-structured-streaming-output)
7. [Advanced Usage](#advanced-usage)

## Basic Concepts

### Initializing a Provider

```python
from streamshape import OpenAI

client = OpenAI(api_key="your-api-key")
```

### Common Parameters

All methods share these parameters:

- **model** (required): Model identifier (e.g., "gpt-4", "claude-3-opus")
- **system_prompt** (required): Instructions for the LLM's behavior
- **user_prompt** (required): The actual query or request
- **kwargs** (optional): Additional parameters like temperature, max_tokens, etc.

---

## Method 1: Generate (Complete Text)

Get a complete text response all at once (non-streaming).

### Basic Usage

```python
response = client.generate(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What is machine learning?"
)

print(response["data"])  # Access the text content
# response["raw_chunks"] contains the raw API response
```

### With Parameters

```python
response = client.generate(
    model="gpt-4",
    system_prompt="You are a creative writer.",
    user_prompt="Write a short poem about the ocean",
    temperature=0.9,        # Higher = more creative
    max_tokens=200,         # Limit response length
    top_p=0.95,            # Nucleus sampling
    frequency_penalty=0.5,  # Reduce repetition
    presence_penalty=0.3    # Encourage new topics
)
```

### Use Cases

✅ **Good for:**
- Simple Q&A
- Short responses
- When you need the complete answer before processing
- Batch processing multiple prompts

❌ **Not ideal for:**
- Long responses where you want to show progress
- Real-time user interfaces
- When you want to process output incrementally

### Example: Translation

```python
def translate_text(text, target_language):
    response = client.generate(
        model="gpt-4",
        system_prompt=f"You are a translator. Translate to {target_language}.",
        user_prompt=text,
        temperature=0.3  # Lower for more consistent translations
    )
    return response["data"]

result = translate_text("Hello, how are you?", "Spanish")
print(result)  # "Hola, ¿cómo estás?"
```

### Example: Code Review

```python
def review_code(code):
    response = client.generate(
        model="gpt-4",
        system_prompt="You are a senior software engineer. Review code for bugs and improvements.",
        user_prompt=f"Review this code:\n\n```python\n{code}\n```",
        temperature=0.5,
        max_tokens=500
    )
    return response["data"]

code = """
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
"""

review = review_code(code)
print(review)
```

---

## Method 2: Stream (Streaming Text)

Get text chunks as they're generated in real-time.

### Basic Usage

```python
for chunk in client.stream(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="Write a short story about a robot"
):
    print(chunk["data"], end="", flush=True)
    # chunk["raw_chunks"] contains the raw chunk object
```

### With Progress Indicator

```python
import sys

print("Generating response: ", end="")
response = ""

for chunk in client.stream(
    model="gpt-4",
    system_prompt="You are a storyteller.",
    user_prompt="Tell me a story",
    temperature=0.8
):
    response += chunk["data"]
    print(chunk["data"], end="", flush=True)
    sys.stdout.flush()

print("\n\nComplete response received!")
```

### Use Cases

✅ **Good for:**
- Long responses (articles, stories, essays)
- Real-time user interfaces
- Showing progress to users
- Reducing perceived latency

❌ **Not ideal for:**
- When you need the complete response before processing
- Batch processing
- Simple, short responses

### Example: Interactive Chat

```python
def chat_stream(user_message, conversation_history=""):
    system_prompt = f"""You are a friendly chatbot.
    
Previous conversation:
{conversation_history}
"""
    
    print("Bot: ", end="", flush=True)
    response = ""
    
    for chunk in client.stream(
        model="gpt-4",
        system_prompt=system_prompt,
        user_prompt=user_message,
        temperature=0.7
    ):
        response += chunk["data"]
        print(chunk["data"], end="", flush=True)
    
    print()  # New line
    return response

# Usage
history = ""
while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ['quit', 'exit']:
        break
    
    bot_response = chat_stream(user_input, history)
    history += f"\nUser: {user_input}\nBot: {bot_response}"
```

### Example: Progress Bar

```python
from tqdm import tqdm
import time

def stream_with_progress(prompt):
    chunks = []
    
    # Create progress bar
    with tqdm(desc="Generating", unit=" tokens") as pbar:
        for chunk in client.stream(
            model="gpt-4",
            system_prompt="You are a helpful assistant.",
            user_prompt=prompt
        ):
            chunks.append(chunk["data"])
            pbar.update(1)
            time.sleep(0.01)  # Small delay for visual effect
    
    return "".join(chunks)

result = stream_with_progress("Write a paragraph about AI")
print(f"\n\nResult: {result}")
```

---

## Method 3: Tool Call (Function Calling)

Let the LLM decide when and how to call functions.

### Basic Usage

```python
# Define tools
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g., San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
}]

# Call with tools
result = client.tool_call(
    model="gpt-4",
    system_prompt="You are a helpful assistant with access to weather data.",
    user_prompt="What's the weather like in Tokyo?",
    tools=tools
)

print(result["data"]["tool_name"])    # "get_weather"
print(result["data"]["arguments"])    # {"location": "Tokyo", "unit": "celsius"}
# result["raw_chunks"] contains the raw API response
```

### Multiple Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get current time in a timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string"}
                },
                "required": ["timezone"]
            }
        }
    }
]

result = client.tool_call(
    model="gpt-4",
    system_prompt="You are a helpful assistant with access to various tools.",
    user_prompt="What time is it in New York?",
    tools=tools
)
```

### Complete Tool Execution Example

```python
import json

# Define actual functions
def get_weather(location, unit="celsius"):
    # In real app, call weather API
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "condition": "Sunny",
        "unit": unit
    }

def calculate(expression):
    try:
        return {"result": eval(expression)}
    except:
        return {"error": "Invalid expression"}

# Map function names to actual functions
available_functions = {
    "get_weather": get_weather,
    "calculate": calculate
}

# Define tools for LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    }
]

# Get tool call from LLM
result = client.tool_call(
    model="gpt-4",
    system_prompt="You are a helpful assistant.",
    user_prompt="What's 25 * 4 and what's the weather in Paris?",
    tools=tools
)

# Execute the function
tool_data = result["data"]
if tool_data["tool_name"] in available_functions:
    function_to_call = available_functions[tool_data["tool_name"]]
    arguments = json.loads(tool_data["arguments"])
    function_result = function_to_call(**arguments)
    print(f"Function result: {function_result}")
```

### Use Cases

✅ **Good for:**
- Integrating with external APIs
- Database queries
- Calculations
- File operations
- Multi-step workflows

---

## Method 4: Structured Output (Complete)

Get validated Pydantic objects all at once (non-streaming).

### Basic Usage

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    occupation: str

result = client.structured_output(
    model="gpt-4",
    system_prompt="You are a data generator.",
    user_prompt="Generate 3 fictional people",
    output_schema=Person
)

for person in result["data"]:
    print(f"{person.name}, {person.age}, {person.occupation}")
# result["raw_chunks"] contains the raw API response
```

### Complex Schema

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class Contact(BaseModel):
    email: str
    phone: Optional[str] = None

class Employee(BaseModel):
    id: int
    name: str
    department: str
    salary: float = Field(gt=0, description="Annual salary in USD")
    address: Address
    contact: Contact
    skills: List[str]

result = client.structured_output(
    model="gpt-4",
    system_prompt="You are an HR system. Generate realistic employee data.",
    user_prompt="Create 2 software engineer employees",
    output_schema=Employee,
    temperature=0.7
)

for emp in result["data"]:
    print(f"\n{emp.name} ({emp.department})")
    print(f"  Salary: ${emp.salary:,.2f}")
    print(f"  Location: {emp.address.city}, {emp.address.country}")
    print(f"  Skills: {', '.join(emp.skills)}")
    print(f"  Contact: {emp.contact.email}")
```

### With Validation

```python
from pydantic import BaseModel, Field, validator

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, description="Price in USD")
    category: str
    in_stock: bool
    
    @validator('category')
    def validate_category(cls, v):
        allowed = ['electronics', 'clothing', 'food', 'books']
        if v.lower() not in allowed:
            raise ValueError(f'Category must be one of {allowed}')
        return v.lower()

result = client.structured_output(
    model="gpt-4",
    system_prompt="You are a product catalog system.",
    user_prompt="Generate 5 products for an online store",
    output_schema=Product
)

for product in result["data"]:
    status = "✅ In Stock" if product.in_stock else "❌ Out of Stock"
    print(f"{product.name} - ${product.price:.2f} ({product.category}) {status}")
```

### Use Cases

✅ **Good for:**
- Data extraction from text
- Generating structured data
- Form filling
- Database inserts
- API responses
- When you need all data before processing

❌ **Not ideal for:**
- Real-time updates
- Very large datasets (use streaming instead)
- When you want to show progress

### Example: Extract Information

```python
from pydantic import BaseModel
from typing import List

class Company(BaseModel):
    name: str
    industry: str
    founded_year: int
    headquarters: str
    key_products: List[str]

text = """
Apple Inc. is a technology company founded in 1976, headquartered in Cupertino, California.
They are known for products like iPhone, iPad, Mac computers, and Apple Watch.
"""

result = client.structured_output(
    model="gpt-4",
    system_prompt="Extract company information from text.",
    user_prompt=f"Extract company details:\n\n{text}",
    output_schema=Company
)

company = result["data"][0]
print(f"Company: {company.name}")
print(f"Industry: {company.industry}")
print(f"Founded: {company.founded_year}")
print(f"HQ: {company.headquarters}")
print(f"Products: {', '.join(company.key_products)}")
```

---

## Method 5: Structured Streaming Output

Get validated Pydantic objects as they're generated (streaming) with token usage tracking.

### Basic Usage

```python
from pydantic import BaseModel

class Task(BaseModel):
    title: str
    priority: str
    estimated_hours: int

final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 10 tasks for building a mobile app",
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
    
    print(f"📋 {task.title} (Priority: {task.priority}, {task.estimated_hours}h)")

# Display token usage
if final_usage:
    print(f"\n📊 Tokens used: {final_usage.get('total_tokens')}")
```

### With Progress Updates

```python
from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    title: str
    summary: str
    category: str
    word_count: int

print("Generating articles...")
count = 0
final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a content writer.",
    user_prompt="Write 5 blog article ideas about AI",
    output_schema=Article,
    temperature=0.8
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
    
    count += 1
    print(f"\n[{count}] {article.title}")
    print(f"    Category: {article.category}")
    print(f"    Summary: {article.summary[:100]}...")
    print(f"    Words: {article.word_count}")

print(f"\n✅ Generated {count} articles!")
if final_usage:
    print(f"📊 Token Usage:")
    print(f"   - Prompt tokens: {final_usage.get('prompt_tokens')}")
    print(f"   - Completion tokens: {final_usage.get('completion_tokens')}")
    print(f"   - Total tokens: {final_usage.get('total_tokens')}")
```

### Use Cases

✅ **Good for:**
- Large datasets
- Real-time dashboards
- Progressive data loading
- User feedback during generation
- Processing data as it arrives

❌ **Not ideal for:**
- When you need all data before processing
- Simple, small datasets
- Batch operations

### Example: Real-time Data Processing

```python
from pydantic import BaseModel
import time

class SalesLead(BaseModel):
    company_name: str
    contact_person: str
    email: str
    industry: str
    potential_value: float

# Simulate processing each lead as it arrives
def process_lead(lead: SalesLead):
    # Add to CRM, send email, etc.
    print(f"  ✉️  Sending welcome email to {lead.email}")
    print(f"  💰 Potential value: ${lead.potential_value:,.2f}")
    time.sleep(0.5)  # Simulate processing

print("Generating and processing leads in real-time...\n")
final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a sales lead generator.",
    user_prompt="Generate 5 B2B sales leads for a SaaS company",
    output_schema=SalesLead
):
    # Extract data and usage
    lead = result.get("data")
    usage = result.get("usage")
    
    # Store usage data
    if usage:
        final_usage = usage
    
    # Skip if no data
    if not lead:
        continue
    
    print(f"📊 New lead: {lead.company_name} ({lead.industry})")
    process_lead(lead)
    print()

if final_usage:
    print(f"📊 Total tokens used: {final_usage.get('total_tokens')}")
```

---

## Advanced Usage

### Error Handling

```python
from streamshape.exceptions import (
    ValidationError,
    APIError,
    NetworkError
)

try:
    response = client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt="Hello"
    )
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except APIError as e:
    print(f"API error: {e}")
    print(f"Provider: {e.provider}")
except NetworkError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Logic

```python
import time

def generate_with_retry(client, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.generate(**kwargs)
        except APIError as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    
response = generate_with_retry(
    client,
    model="gpt-4",
    system_prompt="You are helpful.",
    user_prompt="Hello"
)
```

### Batch Processing

```python
def process_batch(prompts, batch_size=5):
    results = []
    
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}...")
        
        for prompt in batch:
            result = client.generate(
                model="gpt-4",
                system_prompt="You are helpful.",
                user_prompt=prompt,
                temperature=0.7
            )
            results.append(result)
    
    return results

prompts = [
    "What is Python?",
    "What is JavaScript?",
    "What is Go?",
    # ... more prompts
]

results = process_batch(prompts)
```

### Context Management

```python
class LLMSession:
    def __init__(self, client, system_prompt):
        self.client = client
        self.system_prompt = system_prompt
        self.history = []
    
    def send(self, message):
        # Build context from history
        context = "\n".join([
            f"User: {h['user']}\nAssistant: {h['assistant']}"
            for h in self.history
        ])
        
        full_prompt = f"{context}\nUser: {message}" if context else message
        
        result = self.client.generate(
            model="gpt-4",
            system_prompt=self.system_prompt,
            user_prompt=full_prompt
        )
        
        response = result["data"]
        self.history.append({"user": message, "assistant": response})
        return response

# Usage
session = LLMSession(client, "You are a helpful coding assistant.")
print(session.send("How do I create a list in Python?"))
print(session.send("How do I add items to it?"))  # Has context from previous
```

## Next Steps

- **Examples**: See [Examples](examples.md) for more real-world use cases
- **API Reference**: Check [API Reference](api-reference.md) for complete documentation
- **Best Practices**: Read [Best Practices](best-practices.md) for optimization tips

