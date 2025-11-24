# Best Practices

Tips and recommendations for using Unified LLM Interface effectively.

## General Guidelines

### 1. Use Environment Variables for API Keys

❌ **Don't:**
```python
client = OpenAI(api_key="sk-1234567890abcdef")  # Hardcoded
```

✅ **Do:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### 2. Choose the Right Method

| Method | Use When |
|--------|----------|
| `generate()` | Need complete response before processing |
| `stream()` | Want to show progress, long responses |
| `tool_call()` | Need function calling capabilities |
| `structured_output()` | Need all validated data at once |
| `structured_streaming_output()` | Want to process data as it arrives |

### 3. Set Appropriate Temperature

```python
# Factual, consistent responses
response = client.generate(..., temperature=0.1)

# Balanced creativity
response = client.generate(..., temperature=0.7)

# Maximum creativity
response = client.generate(..., temperature=1.5)
```

**Guidelines:**
- **0.0-0.3**: Factual tasks (translation, extraction, classification)
- **0.5-0.8**: Balanced tasks (general chat, content generation)
- **0.9-2.0**: Creative tasks (storytelling, brainstorming)

### 4. Control Response Length

```python
response = client.generate(
    model="gpt-4",
    system_prompt="Be concise.",
    user_prompt="Explain AI",
    max_tokens=100  # Limit response length
)
```

**Benefits:**
- Reduce costs
- Faster responses
- More focused outputs

### 5. Use Streaming for Better UX

```python
# Show progress to users
print("Generating response: ", end="", flush=True)
for chunk in client.stream(...):
    print(chunk, end="", flush=True)
print("\n✅ Done!")
```

## Performance Optimization

### 1. Batch Similar Requests

```python
# Process multiple prompts efficiently
prompts = ["Translate: Hello", "Translate: Goodbye", ...]

results = []
for prompt in prompts:
    result = client.generate(
        model="gpt-3.5-turbo",  # Faster model
        system_prompt="You are a translator.",
        user_prompt=prompt,
        temperature=0.3
    )
    results.append(result)
```

### 2. Cache Responses

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(prompt):
    return client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt=prompt
    )

# First call - hits API
response1 = get_cached_response("What is Python?")

# Second call - returns cached result
response2 = get_cached_response("What is Python?")
```

### 3. Use Cheaper Models for Development

```python
# Development
if os.getenv("ENV") == "development":
    model = "gpt-3.5-turbo"  # Cheaper, faster
else:
    model = "gpt-4"  # Production quality

response = client.generate(model=model, ...)
```

### 4. Implement Request Pooling

```python
from concurrent.futures import ThreadPoolExecutor

def process_prompts_parallel(prompts, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(client.generate, 
                          model="gpt-4",
                          system_prompt="You are helpful.",
                          user_prompt=prompt)
            for prompt in prompts
        ]
        return [f.result() for f in futures]

results = process_prompts_parallel(["Q1", "Q2", "Q3"])
```

## Cost Optimization

### 1. Monitor Token Usage

```python
def generate_with_cost_tracking(prompt):
    response = client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt=prompt
    )
    
    # Estimate cost (approximate)
    input_tokens = len(prompt.split()) * 1.3  # Rough estimate
    output_tokens = len(response.split()) * 1.3
    cost = (input_tokens * 0.03 + output_tokens * 0.06) / 1000
    
    print(f"Estimated cost: ${cost:.4f}")
    return response
```

### 2. Use Appropriate Models

| Task | Recommended Model | Why |
|------|------------------|-----|
| Simple Q&A | gpt-3.5-turbo | Fast, cheap |
| Complex reasoning | gpt-4 | Best quality |
| Long context | claude-3-opus | 200K context |
| Cost-sensitive | gemini-pro | Free tier |

### 3. Optimize Prompts

❌ **Verbose:**
```python
prompt = """
I would like you to please help me understand what 
artificial intelligence is. Could you explain it to me 
in simple terms that anyone could understand? Thank you!
"""
```

✅ **Concise:**
```python
prompt = "Explain AI in simple terms."
```

### 4. Set Token Limits

```python
response = client.generate(
    model="gpt-4",
    system_prompt="Be concise.",
    user_prompt="Explain quantum computing",
    max_tokens=150  # Prevent runaway costs
)
```

## Reliability

### 1. Implement Retry Logic

```python
import time
from functools import wraps

def retry_on_error(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator

@retry_on_error(max_attempts=3)
def generate_text(prompt):
    return client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt=prompt
    )
```

### 2. Handle Errors Gracefully

```python
from streamshape.exceptions import APIError, NetworkError

def safe_generate(prompt, fallback="Unable to generate response"):
    try:
        return client.generate(
            model="gpt-4",
            system_prompt="You are helpful.",
            user_prompt=prompt
        )
    except (APIError, NetworkError) as e:
        print(f"Error: {e}")
        return fallback
```

### 3. Use Fallback Providers

```python
def generate_with_fallback(prompt):
    providers = [
        ("openai", OpenAI(api_key=os.getenv("OPENAI_API_KEY"))),
        ("anthropic", Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))),
    ]
    
    for name, client in providers:
        try:
            return client.generate(
                model=get_model(name),
                system_prompt="You are helpful.",
                user_prompt=prompt
            )
        except Exception as e:
            print(f"{name} failed: {e}")
            continue
    
    raise Exception("All providers failed")
```

### 4. Validate Inputs

```python
def validate_and_generate(prompt, max_length=1000):
    # Validate input
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    if len(prompt) > max_length:
        raise ValueError(f"Prompt too long (max {max_length} chars)")
    
    # Generate
    return client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt=prompt
    )
```

## Security

### 1. Sanitize User Input

```python
import re

def sanitize_prompt(user_input):
    # Remove potential injection attempts
    sanitized = re.sub(r'[^\w\s\.,!?-]', '', user_input)
    
    # Limit length
    sanitized = sanitized[:1000]
    
    return sanitized

user_input = request.form.get('prompt')
safe_input = sanitize_prompt(user_input)

response = client.generate(
    model="gpt-4",
    system_prompt="You are helpful.",
    user_prompt=safe_input
)
```

### 2. Implement Rate Limiting

```python
from time import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=10, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id):
        now = time()
        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True

limiter = RateLimiter(max_requests=10, window=60)

def generate_with_rate_limit(user_id, prompt):
    if not limiter.is_allowed(user_id):
        raise Exception("Rate limit exceeded")
    
    return client.generate(
        model="gpt-4",
        system_prompt="You are helpful.",
        user_prompt=prompt
    )
```

### 3. Filter Sensitive Data

```python
import re

def remove_pii(text):
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove SSN
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    return text

user_input = "My email is john@example.com and phone is 555-123-4567"
safe_input = remove_pii(user_input)

response = client.generate(
    model="gpt-4",
    system_prompt="You are helpful.",
    user_prompt=safe_input
)
```

## Structured Output Best Practices

### 1. Use Clear Field Descriptions

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(description="Product name, 2-50 characters")
    price: float = Field(gt=0, description="Price in USD")
    category: str = Field(description="One of: electronics, clothing, food")
    in_stock: bool = Field(description="Whether product is available")
```

### 2. Add Validation

```python
from pydantic import validator

class Email(BaseModel):
    subject: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=10)
    priority: str
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed = ['low', 'medium', 'high']
        if v.lower() not in allowed:
            raise ValueError(f'Priority must be one of {allowed}')
        return v.lower()
```

### 3. Use Enums for Fixed Values

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority  # Only allows defined values
    status: str
```

### 4. Handle Optional Fields

```python
from typing import Optional

class Person(BaseModel):
    name: str  # Required
    age: int  # Required
    email: Optional[str] = None  # Optional
    phone: Optional[str] = None  # Optional
```

## Prompt Engineering

### 1. Be Specific

❌ **Vague:**
```python
system_prompt = "You are helpful."
user_prompt = "Tell me about dogs."
```

✅ **Specific:**
```python
system_prompt = "You are a veterinarian. Provide accurate, helpful information."
user_prompt = "List 5 common health issues in Golden Retrievers with prevention tips."
```

### 2. Provide Examples

```python
system_prompt = """You are a translator. Examples:
Input: "Hello" → Output: "Hola"
Input: "Goodbye" → Output: "Adiós"
"""
user_prompt = "Translate: Good morning"
```

### 3. Use System Prompts Effectively

```python
# Good system prompts
system_prompts = {
    "concise": "You are helpful. Keep responses under 50 words.",
    "technical": "You are a senior software engineer. Use technical terminology.",
    "beginner": "You are a teacher. Explain concepts simply for beginners.",
    "formal": "You are a professional writer. Use formal language.",
}
```

### 4. Structure Complex Prompts

```python
user_prompt = """
Task: Analyze this customer review

Review: "Great product but shipping was slow"

Please provide:
1. Sentiment (positive/negative/neutral)
2. Key topics mentioned
3. Suggested response
"""
```

## Testing

### 1. Test with Different Inputs

```python
def test_generation():
    test_cases = [
        "Simple question",
        "Very long question " * 100,
        "Question with special chars: @#$%",
        "",  # Empty
        "Non-English: 你好",
    ]
    
    for test_input in test_cases:
        try:
            response = client.generate(
                model="gpt-4",
                system_prompt="You are helpful.",
                user_prompt=test_input
            )
            print(f"✅ Passed: {test_input[:50]}")
        except Exception as e:
            print(f"❌ Failed: {test_input[:50]} - {e}")
```

### 2. Test Error Handling

```python
def test_error_handling():
    # Test invalid API key
    try:
        bad_client = OpenAI(api_key="invalid")
        bad_client.generate(model="gpt-4", system_prompt="", user_prompt="test")
        print("❌ Should have raised error")
    except Exception:
        print("✅ Invalid API key handled")
```

### 3. Monitor Response Quality

```python
def evaluate_response(response, expected_keywords):
    score = sum(1 for keyword in expected_keywords if keyword.lower() in response.lower())
    return score / len(expected_keywords)

response = client.generate(
    model="gpt-4",
    system_prompt="Explain Python.",
    user_prompt="What is Python?"
)

quality = evaluate_response(response, ["programming", "language", "code"])
print(f"Quality score: {quality:.2%}")
```

## Monitoring

### 1. Log All Requests

```python
import logging

logger = logging.getLogger(__name__)

def generate_with_logging(prompt):
    logger.info(f"Generating response for: {prompt[:50]}...")
    
    try:
        response = client.generate(
            model="gpt-4",
            system_prompt="You are helpful.",
            user_prompt=prompt
        )
        logger.info(f"Response length: {len(response)} chars")
        return response
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise
```

### 2. Track Metrics

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RequestMetrics:
    timestamp: datetime
    model: str
    prompt_length: int
    response_length: int
    duration: float
    success: bool

metrics = []

def generate_with_metrics(prompt):
    start = datetime.now()
    
    try:
        response = client.generate(
            model="gpt-4",
            system_prompt="You are helpful.",
            user_prompt=prompt
        )
        
        metrics.append(RequestMetrics(
            timestamp=start,
            model="gpt-4",
            prompt_length=len(prompt),
            response_length=len(response),
            duration=(datetime.now() - start).total_seconds(),
            success=True
        ))
        
        return response
    except Exception as e:
        metrics.append(RequestMetrics(
            timestamp=start,
            model="gpt-4",
            prompt_length=len(prompt),
            response_length=0,
            duration=(datetime.now() - start).total_seconds(),
            success=False
        ))
        raise
```

## Summary

**Key Takeaways:**

1. ✅ Use environment variables for API keys
2. ✅ Choose the right method for your use case
3. ✅ Implement error handling and retries
4. ✅ Optimize costs with appropriate models
5. ✅ Cache responses when possible
6. ✅ Validate and sanitize inputs
7. ✅ Use streaming for better UX
8. ✅ Monitor and log requests
9. ✅ Test thoroughly
10. ✅ Follow security best practices
