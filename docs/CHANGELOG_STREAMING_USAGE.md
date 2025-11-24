# Changelog: Streaming Structured Output with Usage Tracking

## Version: Latest

### Date: 2024

## Summary

Added token usage tracking to `structured_streaming_output()` method. The method now returns dictionaries with usage data instead of yielding Pydantic objects directly.

## Changes

### 1. API Changes

#### `structured_streaming_output()` Return Format

**Before:**
```python
Iterator[BaseModel]  # Yielded Pydantic objects directly
```

**After:**
```python
Iterator[Dict[str, Any]]  # Yields dictionaries with data, usage, finished, raw_chunks
```

### 2. New Features

#### Token Usage Tracking

The method now includes token usage statistics in the final chunk:

```python
{
    "data": None,
    "usage": {
        "prompt_tokens": 28,
        "completion_tokens": 168,
        "total_tokens": 196,
        "completion_tokens_details": {...},
        "prompt_tokens_details": {...}
    },
    "finished": True,
    "raw_chunks": [...]
}
```

#### Stream Options

Automatically adds `stream_options={"include_usage": true}` to all streaming requests to enable usage tracking across all supported providers.

### 3. Implementation Details

#### Modified Files

1. **`src/streamshape/base.py`**
   - Updated `_call_litellm()` to add `stream_options` parameter
   - Changed `structured_streaming_output()` return type from `Iterator[BaseModel]` to `Iterator[Dict[str, Any]]`
   - Updated docstring to document new return format

2. **`src/streamshape/parser_integration.py`**
   - No functional changes (yields dictionaries from `read_tokens` unchanged)

3. **`src/streamshape/streaming_structured_output_parser/parse_llm_output.py`**
   - Already supported usage extraction from streaming chunks
   - No changes needed

4. **`example/streaming_structured_output_usage.py`**
   - Updated all three test functions to handle new dictionary format
   - Added usage data display

### 4. Documentation Updates

Updated the following documentation files:

1. **`docs/api-reference.md`**
   - Updated `structured_streaming_output()` method signature and return type
   - Updated examples to show new format
   - Updated comparison table

2. **`docs/usage.md`**
   - Updated all `structured_streaming_output()` examples
   - Added usage tracking examples

3. **`docs/output-formats.md`**
   - Completely rewrote the "Structured Streaming Output Method" section
   - Added detailed output structure documentation
   - Updated migration guide
   - Updated comparison table

4. **`docs/README.md`**
   - Added link to migration guide
   - Updated feature list

5. **`docs/MIGRATION_STREAMING_USAGE.md`** (NEW)
   - Complete migration guide for users upgrading
   - Before/after examples
   - Step-by-step migration instructions

6. **`docs/CHANGELOG_STREAMING_USAGE.md`** (NEW)
   - This file - detailed changelog

## Breaking Changes

⚠️ **This is a breaking change** for users of `structured_streaming_output()`.

### Migration Required

Old code:
```python
for task in client.structured_streaming_output(...):
    print(task.title)
```

New code:
```python
for result in client.structured_streaming_output(...):
    task = result.get("data")
    if task:
        print(task.title)
```

See [MIGRATION_STREAMING_USAGE.md](MIGRATION_STREAMING_USAGE.md) for complete migration guide.

## Benefits

1. **Cost Monitoring**: Track token usage for each streaming request
2. **Consistency**: All methods now return dictionaries with consistent structure
3. **Debugging**: Access raw chunks for troubleshooting
4. **Future-Proof**: Easy to add more metadata without breaking changes

## Provider Support

Token usage tracking works with all providers that support streaming usage data:

- ✅ OpenAI (GPT-4, GPT-3.5, etc.)
- ✅ Google Gemini (with `stream_options`)
- ✅ Anthropic Claude (with `stream_options`)
- ✅ OpenRouter (depends on underlying model)
- ✅ xAI Grok (with `stream_options`)
- ✅ OpenAI-compatible endpoints (if they support `stream_options`)

## Example Output

```
================================================================================
Testing Google Gemini Streaming Structured Output
================================================================================

📝 Model: gemini-flash-lite-latest
📝 Prompt: Give me 3 jokes on Computer Science

🔄 Streaming jokes...

Joke #1:
  Setup: Why do programmers prefer dark mode?
  Punchlines:
    - (under: Because light attracts bugs.)
  Rating: 5/10

Joke #2:
  Setup: Why was the JavaScript developer sad?
  Punchlines:
    - (under: Because he didn't Node how to Express himself.)
  Rating: 4/10

Joke #3:
  Setup: What is the object-oriented way to become wealthy?
  Punchlines:
    - (under: Inheritance.)
  Rating: 5/10

✅ Stream completed
================================================================================
✅ Successfully received 3 jokes!
📊 Token Usage:
   - Prompt tokens: 28
   - Completion tokens: 168
   - Total tokens: 196
================================================================================
```

## Technical Implementation

### How It Works

1. **Request Phase**: When `structured_streaming_output()` is called, the library adds `stream_options={"include_usage": true}` to the LiteLLM request.

2. **Streaming Phase**: As chunks arrive:
   - Data chunks contain Pydantic objects: `{"data": obj, "usage": {}, "finished": False}`
   - Usage data is captured from chunks that include it

3. **Final Phase**: After all data is streamed:
   - Final chunk contains usage: `{"data": None, "usage": {...}, "finished": True, "raw_chunks": [...]}`

### LiteLLM Integration

The library leverages LiteLLM's `stream_options` parameter, which is supported by OpenAI's streaming API and compatible providers. LiteLLM normalizes this across different providers.

## Testing

Tested with:
- ✅ Google Gemini (gemini-flash-lite-latest)
- ✅ Streaming structured output with multiple objects
- ✅ Usage data extraction and display
- ✅ Backward compatibility (with code changes)

## Future Enhancements

Potential future improvements:
- Add usage tracking to regular `stream()` method
- Add cumulative usage tracking across multiple requests
- Add usage callbacks for real-time monitoring
- Add cost estimation based on provider pricing

## References

- [LiteLLM Stream Options Documentation](https://docs.litellm.ai/docs/completion/input#stream_options)
- [OpenAI Streaming Documentation](https://platform.openai.com/docs/api-reference/streaming)
- [Migration Guide](MIGRATION_STREAMING_USAGE.md)
