# Output Parser Playground

A small toolbox for experimenting with LLM response parsing. It ships mock
payloads for OpenAI, Anthropic, and Google along with a LiteLLM-backed
normalizer so all providers can be handled uniformly.

## Features

- Unified `LLMResponseNormalizer` that turns wildly different payloads into a
  predictable schema (`NormalizedMessage`).
- `LiteLLMRunner` convenience wrapper that executes real models (any provider
  LiteLLM supports) and immediately returns normalized data.
- Streaming helpers that yield text/tool-call deltas without writing custom SSE
  handlers.
- Mock datasets and Pytests that ensure the normalizer keeps working without
  live API calls.

## Installation

Use any virtual environment you like, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## LiteLLM Normalizer

```python
from parse_output.normalizer import LiteLLMRunner

runner = LiteLLMRunner(model="openai/gpt-4o-mini")
normalized = runner.complete([
    {"role": "system", "content": "Return JSON with `facts` and `summary`."},
    {"role": "user", "content": "Share two facts about code review."},
])
print(normalized.as_dict())
```

To try it without writing code, export an API key supported by LiteLLM and run
our demo helper:

```powershell
$env:LITELLM_MODEL = "openai/gpt-4o-mini"
python dummy/litellm_normalizer_demo.py
```

### Compare Gemini vs OpenRouter keys

Use `dummy/compare_normalized_keys.py` to send the same prompt to two providers
and ensure their normalized payloads expose identical top-level keys.

```powershell
$env:LITELLM_MODEL_OPENROUTER = "openrouter/kwaipilot/kat-coder-pro:free"
$env:LITELLM_PARAMS_OPENROUTER = '{"api_base": "https://openrouter.ai/api/v1", "api_key": "YOUR_TOKEN"}'
$env:LITELLM_MODEL_GEMINI = "gemini/gemini-2.0-flash"
$env:LITELLM_PARAMS_GEMINI = '{"api_key": "YOUR_GEMINI_KEY"}'
python dummy/compare_normalized_keys.py
```

If you already export provider-specific API keys (e.g., `OPENROUTER_API_KEY`,
`GEMINI_API_KEY`), you can omit the JSON parameter blocks and LiteLLM will pick
up the defaults automatically.

## Tests

Our focused regression suite keeps the new normalizer honest:

```powershell
python -m pytest tests/test_normalizer.py
```

The tests rely exclusively on the mock payloads in `mock_outputs/raw_data`, so
no external API calls are performed.
