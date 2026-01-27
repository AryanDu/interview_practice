# Ollama LLM Provider Integration

## Overview
Ollama has been successfully integrated as a new LLM provider option in the Interview Practice App. This allows users to run local language models without relying on cloud-based APIs.

## Features

### Default Configuration
- **Default Model**: `phi3` (lightweight and efficient for interview preparation)
- **Default Base URL**: `http://localhost:11434`
- **Environment Variable**: `OLLAMA_BASE_URL` (configurable in `.env`)

### Supported Models
The implementation supports any Ollama-compatible model. Common options include:
- `phi3` (default - recommended for interview prep)
- `mistral`
- `neural-chat`
- `llama2`
- `openchat`
- `orca-mini`
- `starling-lm`

### Dynamic Model Discovery
The UI automatically detects available models from your running Ollama instance. If Ollama is not accessible, fallback models are suggested.

## Installation & Setup

### 1. Install Ollama
Download and install Ollama from [ollama.ai](https://ollama.ai)

### 2. Start Ollama Server
```bash
ollama serve
```
The server will run on `http://localhost:11434` by default.

### 3. Pull a Model
```bash
# Download the default phi3 model
ollama pull phi3

# Or other models
ollama pull mistral
ollama pull llama2
ollama pull neural-chat
```

### 4. Configuration
The `.env` file already includes:
```
OLLAMA_BASE_URL=http://localhost:11434
```

If running Ollama on a different host/port, update this value accordingly:
```
OLLAMA_BASE_URL=http://your-host:11434
```

## Implementation Details

### Files Modified

#### 1. `config.py`
- Added `OLLAMA_BASE_URL` configuration with default `http://localhost:11434`
- Added `DEFAULT_OLLAMA_MODEL = "phi3"`
- Updated `validate_api_keys()` to check Ollama availability

#### 2. `utils/llm_handlers.py`
- Added `OllamaHandler` class with:
  - `_verify_connection()`: Checks if Ollama service is accessible
  - `get_available_models()`: Fetches list of installed models from Ollama
  - `generate_response()`: Generates responses using Ollama API
- Updated `LLMManager` to include Ollama handler
- Updated handler initialization and routing

#### 3. `ui/sidebar.py`
- Added Ollama to model options dictionary
- Implemented dynamic model fetching for Ollama
- Added fallback models if Ollama is unavailable
- Integrated with existing UI selections

#### 4. `.env`
- Added `OLLAMA_BASE_URL=http://localhost:11434`

## API Endpoints Used

The integration uses the Ollama REST API:

### Get Available Models
```
GET /api/tags
```
Returns list of installed models.

### Generate Response
```
POST /api/chat
```
Parameters:
- `model`: Model name
- `messages`: Array of message objects with roles and content
- `temperature`: Temperature parameter
- `top_p`: Top-p sampling parameter
- `num_predict`: Maximum tokens to generate
- `stream`: Set to false for non-streaming responses

## Usage

### Via UI
1. Select "ollama" from the LLM Provider dropdown
2. Choose a model from the available models dropdown
3. Adjust temperature, top-p, and other parameters as needed
4. Use the app normally - Ollama will be used instead of cloud APIs

### Programmatically
```python
from utils.llm_handlers import LLMManager

manager = LLMManager()
response = manager.generate_response(
    provider="ollama",
    system_prompt="You are an interview coach.",
    user_prompt="How should I answer this question?",
    model="phi3",
    temperature=0.7
)
```

## Advantages

✅ **Local Execution**: Run models locally without internet dependency
✅ **No API Costs**: No usage-based billing
✅ **Privacy**: All data stays on your machine
✅ **Customizable**: Use any Ollama-compatible model
✅ **Lightweight**: Phi3 is optimized for resource-constrained environments

## Limitations

⚠️ **Speed**: Local execution may be slower than cloud APIs (varies by hardware)
⚠️ **Model Quality**: Smaller models may not match commercial LLM performance
⚠️ **GPU Requirements**: Better performance with GPU support (requires appropriate drivers)
⚠️ **Token Count**: Ollama doesn't return token counts (usage metrics show 0)

## Troubleshooting

### "Ollama service not accessible"
- Ensure Ollama is running: `ollama serve`
- Check the URL matches your Ollama configuration
- Verify firewall allows connection to port 11434

### "Model not found"
- Pull the model: `ollama pull <model-name>`
- Check available models: `ollama list`

### Slow Responses
- Reduce `max_tokens` slider
- Use smaller models (phi3, openchat)
- Consider GPU acceleration

### Memory Issues
- Use smaller models
- Reduce `max_tokens`
- Offload to GPU if available

## Example Workflow

```bash
# 1. Install Ollama (one-time)
# Download from ollama.ai

# 2. Start Ollama server
ollama serve

# 3. In another terminal, pull model
ollama pull phi3

# 4. Run the app
python -m streamlit run app.py

# 5. In sidebar, select "ollama" provider and "phi3" model
```

## Future Enhancements

Possible improvements:
- Add support for streaming responses
- Implement model quantization options
- Add model management UI (install/remove models)
- Support for multi-modal models (vision)
- Performance optimization and caching
