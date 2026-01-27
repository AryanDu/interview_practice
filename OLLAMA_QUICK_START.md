# Quick Start: Using Ollama with Interview Practice App

## 5-Minute Setup

### Step 1: Install Ollama
Visit [ollama.ai](https://ollama.ai) and download for your OS.

### Step 2: Start Ollama
```bash
ollama serve
```
Leave this terminal open. Ollama will run on `http://localhost:11434`

### Step 3: Get a Model (in another terminal)
```bash
# Default (recommended for interview prep)
ollama pull phi3

# Or try others
ollama pull mistral
ollama pull neural-chat
ollama pull llama2
```

### Step 4: Run the App
```bash
python -m streamlit run app.py
```

### Step 5: Use Ollama in the App
1. Open the sidebar ⚙️
2. Select "ollama" from "Select LLM Provider"
3. Choose your model from "Select Model"
4. Use the app normally!

---

## Available Models to Try

| Model | Size | Speed | Quality | Memory | Notes |
|-------|------|-------|---------|--------|-------|
| **phi3** | 2.7GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Low | Recommended - Fast & efficient |
| mistral | 4GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Medium | Good balance |
| neural-chat | 4GB | ⭐⭐⭐⭐ | ⭐⭐⭐ | Medium | Conversational |
| openchat | 3.5GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Low | Good for chat |
| llama2 | 3.8GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | Medium | Powerful, slower |
| orca-mini | 1.6GB | ⭐⭐⭐⭐⭐ | ⭐⭐ | Very Low | Minimal resources |

## Common Commands

```bash
# List installed models
ollama list

# Pull a model
ollama pull <model-name>

# Remove a model
ollama rm <model-name>

# Check Ollama status
curl http://localhost:11434/api/tags

# See running models
ollama ps
```

## Tips & Tricks

### Speed Up Responses
- Use smaller models (phi3, openchat)
- Lower the "Max Tokens" slider in the app
- Add GPU support if available

### Better Quality
- Use larger models (mistral, llama2)
- Increase temperature slightly (0.8-0.9)
- Ask more specific questions

### Use Custom Base URL
If Ollama is on a different machine:
```bash
# Edit .env file
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Ollama not found" | Make sure `ollama serve` is running |
| "Model not available" | Run `ollama pull phi3` |
| "Slow responses" | Use smaller model or reduce max_tokens |
| "Out of memory" | Use smaller model or restart Ollama |
| "Connection refused" | Check OLLAMA_BASE_URL in .env |

## Why Ollama?

✅ **Free** - No API costs  
✅ **Private** - Data stays on your machine  
✅ **Offline** - Works without internet  
✅ **Fast** - No network latency  
✅ **Customizable** - Use any model  

Perfect for interview prep practice!
