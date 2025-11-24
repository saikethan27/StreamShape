# Migration Guide: Streaming Structured Output with Usage Data

## Overview

The `structured_streaming_output()` method has been updated to return dictionaries with usage data instead of yielding Pydantic objects directly. This change enables token usage tracking for streaming structured outputs.

## What Changed

### Before (Old Format)

```python
from pydantic import BaseModel

class Task(BaseModel):
    title: str
    priority: str

# Old format - yielded Pydantic objects directly
for task in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 5 tasks",
    output_schema=Task
):
    # task was a Task object directly
    print(f"{task.title} - {task.priority}")
```

### After (New Format)

```python
from pydantic import BaseModel

class Task(BaseModel):
    title: str
    priority: str

# New format - yields dictionaries with data, usage, and finished keys
final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a project manager.",
    user_prompt="Create 5 tasks",
    output_schema=Task
):
    # Extract data and usage from result dictionary
    task = result.get("data")
    usage = result.get("usage")
    
    # Store usage data if present
    if usage:
        final_usage = usage
    
    # Skip final chunk (no data, just usage)
    if not task:
        continue
    
    print(f"{task.title} - {task.priority}")

# Display token usage
if final_usage:
    print(f"\nTokens used: {final_usage.get('total_tokens')}")
```

## New Return Format

Each yielded result is now a dictionary with these keys:

```python
{
    "data": BaseModel or None,  # Validated Pydantic object (None for final chunk)
    "usage": dict,              # Token usage statistics (populated in final chunk)
    "finished": bool,           # True for final chunk
    "raw_chunks": list          # List of raw response chunks (only in final chunk)
}
```

### Usage Data Structure

The `usage` dictionary contains:

```python
{
    "prompt_tokens": int,           # Tokens in the prompt
    "completion_tokens": int,       # Tokens in the completion
    "total_tokens": int,            # Total tokens used
    "completion_tokens_details": {  # Detailed breakdown
        "reasoning_tokens": int,
        "accepted_prediction_tokens": int or None,
        "rejected_prediction_tokens": int or None
    },
    "prompt_tokens_details": {      # Prompt token details
        "cached_tokens": int,
        "audio_tokens": int or None
    }
}
```

## Migration Steps

### Step 1: Update Variable Names

Change from direct object access to dictionary access:

```python
# Before
for task in client.structured_streaming_output(...):
    print(task.title)

# After
for result in client.structured_streaming_output(...):
    task = result.get("data")
    if task:
        print(task.title)
```

### Step 2: Add Usage Tracking (Optional)

If you want to track token usage:

```python
final_usage = None

for result in client.structured_streaming_output(...):
    task = result.get("data")
    usage = result.get("usage")
    
    if usage:
        final_usage = usage
    
    if task:
        print(task.title)

if final_usage:
    print(f"Total tokens: {final_usage.get('total_tokens')}")
```

### Step 3: Handle Final Chunk

The final chunk has no data, only usage information. Make sure to skip it:

```python
for result in client.structured_streaming_output(...):
    task = result.get("data")
    
    # Skip final chunk
    if not task:
        continue
    
    # Process task
    print(task.title)
```

## Complete Migration Example

### Before

```python
from pydantic import BaseModel
from typing import List

class Article(BaseModel):
    title: str
    category: str
    word_count: int

articles = []

for article in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a content writer.",
    user_prompt="Write 5 article ideas",
    output_schema=Article
):
    articles.append(article)
    print(f"Received: {article.title}")

print(f"Total: {len(articles)} articles")
```

### After

```python
from pydantic import BaseModel
from typing import List

class Article(BaseModel):
    title: str
    category: str
    word_count: int

articles = []
final_usage = None

for result in client.structured_streaming_output(
    model="gpt-4",
    system_prompt="You are a content writer.",
    user_prompt="Write 5 article ideas",
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
    
    articles.append(article)
    print(f"Received: {article.title}")

print(f"Total: {len(articles)} articles")

# Display usage
if final_usage:
    print(f"Tokens used: {final_usage.get('total_tokens')}")
    print(f"  Prompt: {final_usage.get('prompt_tokens')}")
    print(f"  Completion: {final_usage.get('completion_tokens')}")
```

## Benefits of New Format

1. **Token Usage Tracking**: Monitor API costs in real-time
2. **Consistency**: Matches the format of other streaming methods
3. **Debugging**: Access raw chunks for troubleshooting
4. **Flexibility**: Can add more metadata in future without breaking changes

## Backward Compatibility

This is a **breaking change**. Code using the old format will need to be updated. However, the migration is straightforward:

1. Change loop variable to `result`
2. Extract `data` from `result.get("data")`
3. Add null check: `if not data: continue`
4. Optionally track usage with `result.get("usage")`

## Need Help?

- See [Usage Guide](usage.md) for complete examples
- See [Output Formats](output-formats.md) for detailed format reference
- See [API Reference](api-reference.md) for method documentation

## Technical Details

### Why This Change?

Previously, `structured_streaming_output()` was the only method that didn't return usage data. This made it difficult to:
- Track token consumption for cost monitoring
- Debug API usage patterns
- Implement rate limiting based on token usage

The new format enables these features while maintaining consistency with other methods.

### How It Works

The library now:
1. Passes `stream_options={"include_usage": true}` to LiteLLM
2. Captures usage data from the final streaming chunk
3. Yields it in a structured format alongside the data

This works with all supported providers that support streaming usage data (OpenAI, Anthropic, Google Gemini, etc.).
