# Installation Guide

Complete guide to installing and setting up Unified LLM Interface.

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install unified-llm-interface
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/unified-llm-interface.git
cd unified-llm-interface

# Install in development mode
pip install -e .
```

### Method 3: Install with Poetry

```bash
poetry add unified-llm-interface
```

## Dependencies

The package automatically installs these dependencies:

- **litellm** (>=1.45.0) - Provider normalization
- **openai** (>=1.52.0) - OpenAI SDK
- **anthropic** (>=0.34.0) - Anthropic SDK
- **google-genai** (>=0.6.0) - Google SDK
- **pydantic** (>=2.7.0) - Data validation
- **requests** (>=2.32.0) - HTTP client

## Verify Installation

```python
# Test the installation
from src import OpenAI

print("✅ Unified LLM Interface installed successfully!")
```

## Setting Up API Keys

### Option 1: Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
OPENROUTER_API_KEY=sk-or-...
XAI_API_KEY=...
```

Load in your code:

```python
import os
from dotenv import load_dotenv
from src import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

Install python-dotenv if needed:

```bash
pip install python-dotenv
```

### Option 2: Direct in Code

```python
from src import OpenAI

client = OpenAI(api_key="sk-your-api-key-here")
```

⚠️ **Warning**: Never commit API keys to version control!

### Option 3: System Environment Variables

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-...
set ANTHROPIC_API_KEY=sk-ant-...
```

## Getting API Keys

### OpenAI

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy and save your key

### Anthropic (Claude)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Generate a new key
5. Copy and save your key

### Google (Gemini)

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and save your key

### OpenRouter

1. Go to https://openrouter.ai/
2. Sign up or log in
3. Navigate to Keys section
4. Create a new key
5. Copy and save your key

### xAI (Grok)

1. Go to https://console.x.ai/
2. Sign up or log in
3. Navigate to API section
4. Generate a new key
5. Copy and save your key

## Virtual Environment Setup (Recommended)

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install package
pip install unified-llm-interface
```

### Using conda

```bash
# Create environment
conda create -n llm-env python=3.10

# Activate
conda activate llm-env

# Install package
pip install unified-llm-interface
```

## Upgrading

### Upgrade to Latest Version

```bash
pip install --upgrade unified-llm-interface
```

### Upgrade Specific Version

```bash
pip install unified-llm-interface==1.2.0
```

## Uninstallation

```bash
pip uninstall unified-llm-interface
```

## Troubleshooting

### Issue: Import Error

**Problem:**
```python
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
pip install unified-llm-interface
# or
pip install -e .  # if installing from source
```

### Issue: Dependency Conflicts

**Problem:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

**Solution:**
```bash
# Create a fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # or fresh_env\Scripts\activate on Windows
pip install unified-llm-interface
```

### Issue: SSL Certificate Error

**Problem:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solution:**
```bash
# Update certificates
pip install --upgrade certifi

# Or install with --trusted-host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org unified-llm-interface
```

### Issue: Permission Denied

**Problem:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Install for current user only
pip install --user unified-llm-interface

# Or use sudo (Linux/Mac)
sudo pip install unified-llm-interface
```

## Development Installation

For contributing or development:

```bash
# Clone repository
git clone https://github.com/yourusername/unified-llm-interface.git
cd unified-llm-interface

# Install with development dependencies
pip install -e ".[dev]"

# Or install dev dependencies separately
pip install -e .
pip install pytest hypothesis black mypy
```

## Docker Installation

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install package
RUN pip install unified-llm-interface

# Copy your application
COPY . .

CMD ["python", "your_app.py"]
```

Build and run:

```bash
docker build -t my-llm-app .
docker run -e OPENAI_API_KEY=sk-... my-llm-app
```

## Next Steps

✅ Installation complete! Now:

1. **Quick Start**: Follow the [Quick Start Guide](quickstart.md)
2. **Configuration**: Set up [Provider Configuration](providers.md)
3. **Usage**: Learn from the [Usage Guide](usage.md)

## Support

If you encounter issues:

1. Check this troubleshooting section
2. Review [Error Handling](error-handling.md)
3. Open an issue on GitHub
4. Check existing issues for solutions
