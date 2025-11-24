# Error Handling

Guide to understanding and handling errors in Unified LLM Interface.

## Exception Hierarchy

```
UnifiedLLMError (base)
├── ConfigurationError
├── ValidationError
├── APIError
├── NetworkError
└── ParsingError
```

## Exception Types

### UnifiedLLMError

Base exception for all package errors.

```python
from streamshape.exceptions import UnifiedLLMError

try:
    response = client.generate(...)
except UnifiedLLMError as e:
    print(f"An error occurred: {e}")
```

### ConfigurationError

Raised when provider configuration is invalid.

```python
from streamshape.exceptions import ConfigurationError

try:
    client = OpenAICompatible(api_key="key")  # Missing base_url
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

**Common causes:**
- Missing required parameters
- Invalid base URL format
- Incorrect provider setup

### ValidationError

Raised when input validation fails.

```python
from streamshape.exceptions import ValidationError

try:
    response = client.generate(
        model="",  # Empty model
        system_prompt="...",
        user_prompt="..."
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

**Common causes:**
- Missing required parameters
- Empty strings for required fields
- Invalid output_schema type
- Invalid tool definitions

### APIError

Raised when the LLM API call fails.

```python
from streamshape.exceptions import APIError

try:
    response = client.generate(...)
except APIError as e:
    print(f"API error: {e}")
    print(f"Provider: {e.provider}")
    print(f"Original error: {e.original_error}")
```

**Common causes:**
- Authentication failures
- Invalid API keys
- Rate limiting
- Invalid model names
- Insufficient credits

**Attributes:**
- `provider`: Name of the provider (e.g., "openai")
- `original_error`: The underlying exception from LiteLLM

### NetworkError

Raised when network communication fails.

```python
from streamshape.exceptions import NetworkError

try:
    response = client.generate(...)
except NetworkError as e:
    print(f"Network error: {e}")
```

**Common causes:**
- Connection timeouts
- DNS failures
- SSL/TLS errors
- Proxy issues

### ParsingError

Raised when response parsing fails (structured output only).

```python
from streamshape.exceptions import ParsingError

try:
    results = client.structured_output(...)
except ParsingError as e:
    print(f"Parsing error: {e}")
```

**Common causes:**
- Malformed JSON from LLM
- Schema validation failures
- Invalid response format

## Error Handling Patterns

### Basic Try-Except

```python
try:
    response = client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt="Hello"
    )
    print(response)
except Exception as e:
    print(f"Error: {e}")
```

### Specific Exception Handling

```python
from streamshape.exceptions import (
    ValidationError,
    APIError,
    NetworkError
)

try:
    response = client.generate(...)
except ValidationError as e:
    print(f"Invalid input: {e}")
    # Fix input and retry
except APIError as e:
    if "rate_limit" in str(e).lower():
        print("Rate limited. Please wait.")
    elif "authentication" in str(e).lower():
        print("Check your API key")
    else:
        print(f"API error: {e}")
except NetworkError as e:
    print(f"Network issue: {e}")
    # Retry with backoff
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry with Exponential Backoff

```python
import time

def generate_with_retry(client, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.generate(**kwargs)
        except APIError as e:
            if "rate_limit" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
            else:
                raise
        except NetworkError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Network error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

# Usage
response = generate_with_retry(
    client,
    model="gpt-4",
    system_prompt="You are helpful.",
    user_prompt="Hello"
)
```

### Graceful Degradation

```python
def generate_with_fallback(prompt, providers):
    """Try multiple providers until one succeeds."""
    for provider_name, client in providers.items():
        try:
            return client.generate(
                model=get_model_for_provider(provider_name),
                system_prompt="You are helpful.",
                user_prompt=prompt
            )
        except Exception as e:
            print(f"{provider_name} failed: {e}")
            continue
    
    raise Exception("All providers failed")

# Usage
providers = {
    "openai": OpenAI(api_key="..."),
    "anthropic": Anthropic(api_key="..."),
    "google": Google(api_key="...")
}

response = generate_with_fallback("Hello", providers)
```

### Logging Errors

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    response = client.generate(...)
except APIError as e:
    logger.error(
        f"API error from {e.provider}",
        extra={
            "provider": e.provider,
            "error": str(e),
            "original_error": str(e.original_error)
        }
    )
    raise
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

### Context Manager

```python
from contextlib import contextmanager

@contextmanager
def llm_error_handler():
    try:
        yield
    except ValidationError as e:
        print(f"❌ Invalid input: {e}")
    except APIError as e:
        print(f"❌ API error ({e.provider}): {e}")
    except NetworkError as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

# Usage
with llm_error_handler():
    response = client.generate(...)
```

## Common Error Scenarios

### Authentication Errors

**Error:**
```
APIError: [openai] Authentication failed: Incorrect API key provided
```

**Solution:**
1. Verify API key is correct
2. Check key has proper permissions
3. Ensure key is not expired
4. Check for typos or extra spaces

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")

client = OpenAI(api_key=api_key)
```

### Rate Limiting

**Error:**
```
APIError: [openai] Rate limit exceeded
```

**Solution:**
1. Implement exponential backoff
2. Reduce request frequency
3. Upgrade API tier
4. Use multiple API keys with load balancing

```python
import time
from functools import wraps

def rate_limit_handler(max_retries=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except APIError as e:
                    if "rate_limit" in str(e).lower():
                        if attempt < max_retries - 1:
                            wait = min(2 ** attempt, 60)  # Max 60s
                            print(f"Rate limited. Waiting {wait}s...")
                            time.sleep(wait)
                        else:
                            raise
                    else:
                        raise
        return wrapper
    return decorator

@rate_limit_handler()
def generate_text(prompt):
    return client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt=prompt
    )
```

### Invalid Model

**Error:**
```
APIError: [openai] Model 'gpt-5' not found
```

**Solution:**
1. Check model name spelling
2. Verify model is available for your account
3. Use correct model for provider

```python
PROVIDER_MODELS = {
    "openai": ["gpt-4", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-opus", "claude-3-sonnet"],
    "google": ["gemini-pro", "gemini-1.5-pro"]
}

def validate_model(provider, model):
    if model not in PROVIDER_MODELS.get(provider, []):
        raise ValueError(
            f"Invalid model '{model}' for {provider}. "
            f"Available: {PROVIDER_MODELS[provider]}"
        )

validate_model("openai", "gpt-4")
```

### Parsing Errors

**Error:**
```
ParsingError: Failed to parse JSON response
```

**Solution:**
1. Lower temperature for more consistent output
2. Add clearer instructions in prompt
3. Validate schema is correct
4. Try different model

```python
try:
    results = client.structured_output(
        model="gpt-4",
        system_prompt="You are a data generator. Output valid JSON only.",
        user_prompt="Generate 3 users",
        output_schema=User,
        temperature=0.1  # Lower for consistency
    )
except ParsingError as e:
    print(f"Parsing failed: {e}")
    # Fallback to text generation
    text = client.generate(
        model="gpt-4",
        system_prompt="Generate user data.",
        user_prompt="Generate 3 users"
    )
    # Manual parsing
```

### Network Timeouts

**Error:**
```
NetworkError: Connection timeout
```

**Solution:**
1. Check internet connection
2. Increase timeout
3. Retry with backoff
4. Check firewall/proxy settings

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
```

## Best Practices

1. **Always handle exceptions** - Don't let errors crash your app
2. **Log errors** - Track issues for debugging
3. **Implement retries** - Handle transient failures
4. **Validate inputs** - Catch errors early
5. **Use specific exceptions** - Handle different errors differently
6. **Provide user feedback** - Show meaningful error messages
7. **Monitor errors** - Track error rates and types
8. **Test error paths** - Ensure error handling works

## Debugging Tips

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Inspect Error Details

```python
try:
    response = client.generate(...)
except APIError as e:
    print(f"Provider: {e.provider}")
    print(f"Error message: {str(e)}")
    print(f"Original error: {e.original_error}")
    print(f"Error type: {type(e.original_error)}")
```

### Test Error Handling

```python
def test_error_handling():
    # Test invalid API key
    try:
        client = OpenAI(api_key="invalid")
        client.generate(model="gpt-4", system_prompt="", user_prompt="test")
    except APIError:
        print("✅ Invalid API key handled")
    
    # Test missing parameters
    try:
        client.generate(model="", system_prompt="", user_prompt="")
    except ValidationError:
        print("✅ Missing parameters handled")
```

## Getting Help

If you encounter an error not covered here:

1. Check the error message carefully
2. Review the [API Reference](api-reference.md)
3. Search existing GitHub issues
4. Enable debug logging
5. Create a minimal reproduction
6. Open a GitHub issue with details
