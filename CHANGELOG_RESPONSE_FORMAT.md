# Response Format Update - Changelog

## Summary
Updated all methods (`generate`, `stream`, `tool_call`, `structured_output`) to return a consistent JSON format with `data` and `raw_chunks` fields. The `structured_streaming_output` method remains unchanged as requested.

## Changes Made

### 1. `src/base.py` - Core Methods Updated

#### `generate()` method
**Before:**
```python
return response.choices[0].message.content  # Returns string
```

**After:**
```python
return {
    "data": response.choices[0].message.content,
    "raw_chunks": response
}
```

#### `stream()` method
**Before:**
```python
yield delta.content  # Yields string chunks
```

**After:**
```python
yield {
    "data": content,  # Empty string if None
    "raw_chunks": chunk
}
```

#### `tool_call()` method
**Before:**
```python
return {
    "tool_name": tool_call.function.name,
    "arguments": tool_call.function.arguments
}
```

**After:**
```python
return {
    "data": {
        "tool_name": tool_call.function.name,
        "arguments": tool_call.function.arguments
    },
    "raw_chunks": response
}
```

#### `structured_output()` method
**Before:**
```python
return validated_objects  # Returns List[BaseModel]
```

**After:**
```python
return {
    "data": validated_objects,
    "raw_chunks": response
}
```

#### `structured_streaming_output()` method
**NOT CHANGED** - Still yields `BaseModel` objects directly as requested.

### 2. Test Files Updated

#### `tests/test_base_provider.py`
- Updated all test assertions to check for dict structure with `data` and `raw_chunks` keys
- Updated stream tests to verify chunk structure
- Updated tool_call tests to access nested data structure
- All 19 tests passing

#### `tests/test_normalizer.py`
- Updated all provider tests to access `result["data"]` instead of direct result
- Updated streaming tests to extract data from chunks
- Updated structured output tests to access `result["data"]`
- All 14 tests passing

#### `tests/__init__.py`
- Fixed import error by removing invalid `import parse_output`

### 3. Documentation Updated

#### `docs/usage.md`
- Updated all code examples to use new response format
- Added comments showing how to access `data` and `raw_chunks`
- Updated 14+ code examples across all methods

#### `docs/examples.md`
- Updated all real-world examples
- Updated integration examples (Slack, Discord, FastAPI, Streamlit)
- Updated data extraction, code generation, and customer support examples
- Updated 15+ code examples

#### `docs/quickstart.md`
- Updated quick start examples for all 5 methods
- Added clear examples showing the new format
- Updated 6+ code examples

### 4. Real Usage Files Updated

#### `real_use/all_methods_usage.py`
- Updated `test_generate()` to access `result["data"]`
- Updated `test_stream()` to access `chunk["data"]`
- Updated `test_tool_call()` to access `result["data"]["tool_name"]`
- Updated `test_structured_output()` to access `result["data"]`

#### `real_use/structured_output_usage.py`
- Updated both test functions to use new format
- Updated comparison examples

#### `real_use/streaming_structured_output_usage.py`
- No changes needed (already uses the correct format for streaming)

## Benefits of This Change

1. **Consistency**: All methods now return the same structure
2. **Access to Raw Data**: Users can access the raw API response if needed
3. **Backward Compatible Path**: Easy to migrate by accessing `result["data"]`
4. **Better Debugging**: Raw chunks available for troubleshooting
5. **Streaming Clarity**: Stream chunks now clearly separate data from metadata

## Migration Guide for Users

### For `generate()`:
```python
# Old way
response = client.generate(...)
print(response)  # string

# New way
result = client.generate(...)
print(result["data"])  # string
print(result["raw_chunks"])  # raw API response
```

### For `stream()`:
```python
# Old way
for chunk in client.stream(...):
    print(chunk, end="")  # string

# New way
for chunk in client.stream(...):
    print(chunk["data"], end="")  # string
    # chunk["raw_chunks"] available if needed
```

### For `tool_call()`:
```python
# Old way
result = client.tool_call(...)
print(result["tool_name"])

# New way
result = client.tool_call(...)
print(result["data"]["tool_name"])
print(result["raw_chunks"])  # raw API response
```

### For `structured_output()`:
```python
# Old way
objects = client.structured_output(...)
for obj in objects:
    print(obj.field)

# New way
result = client.structured_output(...)
for obj in result["data"]:
    print(obj.field)
# result["raw_chunks"] available if needed
```

### For `structured_streaming_output()`:
**NO CHANGE** - Still works the same way:
```python
for obj in client.structured_streaming_output(...):
    print(obj.field)  # BaseModel object
```

## Test Results

All tests passing:
- `tests/test_base_provider.py`: 19/19 ✅
- `tests/test_normalizer.py`: 14/14 ✅
- Total: 33/33 tests passing ✅

## Files Modified

1. `src/base.py` - Core implementation
2. `tests/test_base_provider.py` - Unit tests
3. `tests/test_normalizer.py` - Integration tests
4. `tests/__init__.py` - Fixed import
5. `docs/usage.md` - Usage documentation
6. `docs/examples.md` - Example documentation
7. `docs/quickstart.md` - Quick start guide
8. `real_use/all_methods_usage.py` - Real usage examples
9. `real_use/structured_output_usage.py` - Structured output examples

## Notes

- The `structured_streaming_output` method was intentionally left unchanged as per requirements
- All documentation has been updated to reflect the new format
- All tests have been updated and are passing
- Real usage examples have been updated to demonstrate the new format
