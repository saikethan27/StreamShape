# Provider Configuration

Detailed configuration guide for each supported provider.

## OpenAI

### Setup

1. Get API key from https://platform.openai.com/api-keys
2. Initialize client:

```python
from streamshape import OpenAI

client = OpenAI(api_key="sk-...")
```

### Available Models

| Model | Context | Best For |
|-------|---------|----------|
| gpt-4-turbo | 128K | Most capable, latest features |
| gpt-4 | 8K | High quality, complex tasks |
| gpt-3.5-turbo | 16K | Fast, cost-effective |

### Pricing (as of 2024)

- GPT-4 Turbo: $0.01/1K input, $0.03/1K output
- GPT-4: $0.03/1K input, $0.06/1K output
- GPT-3.5 Turbo: $0.0005/1K input, $0.0015/1K output

## Anthropic (Claude)

### Setup

1. Get API key from https://console.anthropic.com/
2. Initialize client:

```python
from streamshape import Anthropic

client = Anthropic(api_key="sk-ant-...")
```

### Available Models

| Model | Context | Best For |
|-------|---------|----------|
| claude-3-opus | 200K | Most capable, complex tasks |
| claude-3-sonnet | 200K | Balanced performance/cost |
| claude-3-haiku | 200K | Fast, cost-effective |

## Google (Gemini)

### Setup

1. Get API key from https://makersuite.google.com/app/apikey
2. Initialize client:

```python
from streamshape import Google

client = Google(api_key="...")
```

### Available Models

| Model | Context | Best For |
|-------|---------|----------|
| gemini-1.5-pro | 1M | Long context, complex tasks |
| gemini-pro | 32K | General purpose |
| gemini-1.5-flash | 1M | Fast, cost-effective |

## OpenRouter

### Setup

1. Get API key from https://openrouter.ai/keys
2. Initialize client:

```python
from streamshape import OpenRouter

client = OpenRouter(api_key="sk-or-...")
```

### Benefits

- Access to 100+ models from one API
- Automatic fallbacks
- Cost optimization
- No rate limits

### Popular Models

- `openai/gpt-4-turbo`
- `anthropic/claude-3-opus`
- `google/gemini-pro`
- `meta-llama/llama-3-70b`

## xAI (Grok)

### Setup

1. Get API key from https://console.x.ai/
2. Initialize client:

```python
from streamshape import XAI

client = XAI(api_key="...")
```

### Available Models

- `grok-beta`: Latest Grok model
- `grok-vision-beta`: With vision capabilities

## OpenAI-Compatible Endpoints

### Local Models (Ollama)

```python
from streamshape import OpenAICompatible

client = OpenAICompatible(
    api_key="ollama",  # Can be any string
    base_url="http://localhost:11434/v1"
)

response = client.generate(
    model="llama2",
    system_prompt="You are helpful.",
    user_prompt="Hello!"
)
```

### LM Studio

```python
client = OpenAICompatible(
    api_key="lm-studio",
    base_url="http://localhost:1234/v1"
)
```

### Custom Endpoints

```python
client = OpenAICompatible(
    api_key="your-api-key",
    base_url="https://your-endpoint.com/v1"
)
```

## Comparison Table

| Provider | Strengths | Weaknesses | Best Use Case |
|----------|-----------|------------|---------------|
| OpenAI | Most popular, great docs | Can be expensive | General purpose |
| Anthropic | Long context, safety | Limited availability | Complex analysis |
| Google | Huge context, free tier | Newer, less tested | Long documents |
| OpenRouter | Many models, one API | Extra abstraction layer | Model comparison |
| xAI | Real-time data | Limited models | Current events |
| Local | Privacy, no cost | Requires setup | Sensitive data |

## Rate Limits

### OpenAI
- Free tier: 3 RPM, 40K TPM
- Pay-as-you-go: 3,500 RPM, 90K TPM

### Anthropic
- Tier 1: 50 RPM, 100K TPM
- Tier 4: 4,000 RPM, 400K TPM

### Google
- Free: 60 RPM
- Paid: Higher limits

### OpenRouter
- No rate limits (pay per use)

## Best Practices

1. **Start with cheaper models** for development
2. **Use streaming** for better UX
3. **Cache responses** when possible
4. **Monitor costs** with provider dashboards
5. **Set max_tokens** to control costs
6. **Use temperature=0** for consistent results

## Switching Providers

The API is identical across providers:

```python
# Just change the import and API key!

# OpenAI
from streamshape import OpenAI
client = OpenAI(api_key="...")

# Anthropic
from streamshape import Anthropic
client = Anthropic(api_key="...")

# Same code works for both!
response = client.generate(
    model="gpt-4",  # or "claude-3-opus"
    system_prompt="You are helpful.",
    user_prompt="Hello!"
)
```

