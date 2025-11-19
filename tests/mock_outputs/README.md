# Mock Data for Testing

This directory contains mock response data from AI providers for testing the normalizer without making actual API calls.

## Directory Structure

```
mock_outputs/
├── anthropic/
│   ├── plain_text.json          # Simple text response
│   ├── tool_call.json            # Response with tool/function call
│   ├── streaming_text.jsonl      # Streaming text response (one event per line)
│   └── streaming_tool_call.jsonl # Streaming tool call response
└── google/
    ├── plain_text.json          # Simple text response
    ├── tool_call.json            # Response with function call
    ├── streaming_text.jsonl      # Streaming text response (one chunk per line)
    └── streaming_tool_call.jsonl # Streaming function call response
```

## File Formats

- **`.json` files**: Complete response objects from the provider
- **`.jsonl` files**: JSON Lines format - one JSON object per line representing streaming events/chunks

## Data Sources

All mock data is based on actual API responses from:
- **Anthropic Claude API**: claude-3-opus-20240229 model
- **Google Gemini API**: gemini-pro model

## Usage in Tests

```python
import json

# Load complete response
with open("tests/mock_outputs/anthropic/plain_text.json") as f:
    response = json.load(f)

# Load streaming events
with open("tests/mock_outputs/anthropic/streaming_text.jsonl") as f:
    events = [json.loads(line) for line in f]
```

## Updating Mock Data

When provider APIs change or new response types are added:

1. Capture real API responses (with sensitive data removed)
2. Save in appropriate provider directory
3. Follow naming convention: `{response_type}.json` or `{response_type}.jsonl`
4. Update this README with any new files

## Coverage

Current mock data covers:
- ✅ Plain text responses (sync)
- ✅ Streaming text responses
- ✅ Tool/function call responses (sync)
- ⏳ Streaming tool call responses (TODO)
- ⏳ Structured JSON output (TODO)
- ⏳ Error responses (TODO)
- ⏳ Edge cases (empty responses, missing fields, etc.)
