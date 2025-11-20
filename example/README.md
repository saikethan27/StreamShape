# Real API Tests

This folder contains test scripts that use real API keys to test the unified LLM interface.

## Setup

1. Make sure you have a `.env` file in the root directory with your API keys:
   ```
   OPENROUTER_API_KEY="your-key-here"
   OPENAI_BASE_URL="https://openrouter.ai/api/v1"
   OPENROUTER_MODEL="kwaipilot/kat-coder-pro:free"
   
   GOOGLE_API_KEY="your-key-here"
   GOOGLE_MODEL="gemini-flash-lite-latest"
   ```

2. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

## Test Files

### 1. `streaming_structured_output_usage.py`
Tests streaming structured output with the Joke schema across different providers.

**Run:**
```bash
python real_use/streaming_structured_output_usage.py
```

**Features:**
- Tests OpenRouter with OpenAI-compatible endpoint
- Tests Google Gemini (uncomment to enable)
- Streams Joke objects with setup, punchline, and rating
- Real-time display of jokes as they arrive
- Returns dictionaries with `data`, `usage`, `finished`, and `error` keys
- Each `data` contains a validated Pydantic Joke object

### 2. `all_methods_usage.py`
Comprehensive test of all four methods in the unified interface.

**Run:**
```bash
python real_use/all_methods_usage.py
```

**Tests:**
1. **Generate** - Non-streaming text generation
2. **Stream** - Streaming text generation
3. **Tool Call** - Function calling with weather tool
4. **Structured Streaming Output** - Streaming validated Pydantic objects

### 3. `structured_output_usage.py`
Tests non-streaming structured output (returns complete list at once).

**Run:**
```bash
python real_use/structured_output_usage.py
```

**Features:**
- Tests `structured_output` method (non-streaming)
- Returns complete list of Pydantic objects
- Compares streaming vs non-streaming approaches
- Shows when to use each method

## Example Output

### Streaming Structured Output:
```
================================================================================
Testing OpenAI-Compatible Streaming Structured Output
================================================================================

📝 Model: gpt-3.5-turbo
📝 Prompt: Give me 4 jokes on Algorithms

🔄 Streaming jokes...

Joke #1:
  Setup: Why did the graph go to therapy?
  Punchline: Because it had too many cycles!
  Rating: 7/10

Joke #2:
  Setup: What do you call a graph with no edges?
  Punchline: A discrete set of points!
  Rating: 6/10

Joke #3:
  Setup: Why do programmers prefer dark mode?
  Punchline: Because light attracts bugs!
  Rating: 8/10

Joke #4:
  Setup: How do you comfort a JavaScript bug?
  Punchline: You console it!
  Rating: 9/10

✅ Stream completed!
================================================================================
✅ Successfully received 4 jokes!
   Tokens used: 245
================================================================================
```

### Tool Call:
```
Tool Call Result:
  Tool Name: get_weather
  Arguments: {"location": "San Francisco, CA", "unit": "fahrenheit"}
```

## Output Format

### Streaming Structured Output
The `structured_streaming_output` method yields dictionaries with the following structure:

```python
{
    "data": Joke(setup="...", punchline="...", rating=7),  # Validated Pydantic object
    "usage": {"total_tokens": 245, "prompt_tokens": 50, "completion_tokens": 195},
    "finished": False,  # True when stream is complete
    "error": None  # Error message if something went wrong
}
```

**Usage Pattern:**
```python
for result in provider.structured_streaming_output(...):
    data = result.get("data")  # Pydantic object
    usage = result.get("usage")  # Token usage info
    finished = result.get("finished")  # Stream completion flag
    error = result.get("error")  # Error message if any
    
    if data:
        # Process the validated Pydantic object
        print(f"Setup: {data.setup}")
        print(f"Punchline: {data.punchline}")
    
    if finished:
        break
```

### Non-Streaming Structured Output
The `structured_output` method returns a complete list:

```python
jokes = provider.structured_output(...)
# Returns: List[Joke]
for joke in jokes:
    print(f"Setup: {joke.setup}")
```

## Customization

You can modify the test files to:
- Change the number of jokes requested
- Test different providers (OpenAI, Google, Anthropic, etc.)
- Adjust temperature and other parameters
- Create your own Pydantic schemas for structured output

## Troubleshooting

If you encounter errors:
1. Check that your API keys are valid in the `.env` file
2. Ensure you have internet connectivity
3. Verify the model names are correct for your provider
4. Check the console output for detailed error messages
