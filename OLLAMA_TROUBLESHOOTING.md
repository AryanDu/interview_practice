# Ollama Troubleshooting Guide

## Common Issues & Solutions

### ❌ Error: "HTTPConnectionPool Read timed out"

**Cause**: Model is taking too long to respond (>10 minutes)

**Solutions**:

1. **Model not installed** - Install the model first:
   ```bash
   ollama pull phi3
   ```

2. **Model too large for your system** - Use a smaller model:
   - ✅ **phi3** (2.7GB) - Fastest, lightweight
   - ✅ **openchat** (3.5GB) - Good balance
   - ✅ **neural-chat** (4GB) - Medium
   - ❌ **llama2** (3.8GB) - Slower
   - ❌ **mistral** (4GB) - Slower
   - ❌ **dolphin-mixtral** (26GB) - Very slow

3. **Reduce max tokens** in the app:
   - Slide "Max Tokens" to 500-1000 instead of 2000

4. **Check system resources**:
   ```bash
   # Windows: Check Task Manager for RAM usage
   # Linux/Mac: watch -n 1 'ps aux | grep ollama'
   ```

5. **Restart Ollama**:
   ```bash
   # Stop Ollama (Ctrl+C in terminal)
   # Wait 10 seconds
   ollama serve
   ```

---

### ❌ Error: "Cannot connect to Ollama at localhost:11434"

**Cause**: Ollama service is not running

**Solution**:
```bash
ollama serve
```
Keep this terminal open. Don't close it!

**Check if running**:
```bash
# Windows
curl http://localhost:11434/api/tags

# Mac/Linux
curl -s http://localhost:11434/api/tags
```

---

### ❌ Error: "Model not found" or "404 error"

**Cause**: Model not installed on your system

**Solution**:
```bash
# Pull the model
ollama pull phi3
ollama pull mistral
ollama pull neural-chat
# etc.

# List installed models
ollama list
```

---

### ❌ Error: "OLLAMA_BASE_URL not configured"

**Cause**: Missing .env file configuration

**Solution**:
Check your `.env` file contains:
```
OLLAMA_BASE_URL=http://localhost:11434
```

If using a remote Ollama server:
```
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

---

### ❌ App is very slow or freezes

**Cause**: Model too large, not enough resources, or wrong timeout

**Solutions**:

1. **Use faster model**:
   - Switch to **phi3** (fastest)
   - Avoid **llama2** or **dolphin-mixtral**

2. **Reduce complexity**:
   - Lower "Max Tokens" to 500
   - Lower "Temperature" to 0.5

3. **Check system RAM**:
   - Need at least 4GB free RAM
   - 8GB+ recommended

4. **Restart everything**:
   - Stop app (Ctrl+C)
   - Stop Ollama (Ctrl+C)
   - Wait 30 seconds
   - Start Ollama again
   - Start app again

---

### ❌ "Empty response from Ollama"

**Cause**: Model returned blank response

**Solutions**:

1. Verify model is working:
   ```bash
   ollama run phi3 "Hello, how are you?"
   ```

2. Try with fewer tokens:
   - Reduce "Max Tokens" slider to 500

3. Reinstall the model:
   ```bash
   ollama rm phi3
   ollama pull phi3
   ```

---

### ❌ High CPU/Memory usage, system freezing

**Cause**: Model too large for your hardware

**Solution**:
1. Stop Ollama (Ctrl+C)
2. Use a smaller model:
   ```bash
   ollama pull phi3
   ```

**Hardware Requirements**:
- **Minimum**: 4GB RAM, Intel i5/AMD R5
- **Recommended**: 8GB RAM, Intel i7/AMD R7, GPU support
- **Optimal**: 16GB RAM, NVIDIA GPU with CUDA

---

### ❌ "Connection refused" on non-localhost

**Cause**: Ollama not listening on network

**Solution**:
When starting Ollama, specify the binding address:
```bash
# Windows - Edit Ollama settings to include:
OLLAMA_HOST=0.0.0.0:11434

# Or start from command line:
set OLLAMA_HOST=0.0.0.0:11434 && ollama serve
```

---

## Performance Optimization Tips

### Speed Up Response Times:

1. **Use phi3** - Fastest model (2.7GB)
   ```bash
   ollama pull phi3
   ```

2. **Enable GPU acceleration** (if you have NVIDIA GPU):
   - Install CUDA Toolkit
   - Ollama automatically uses GPU if available

3. **Pre-load model** to memory:
   ```bash
   ollama run phi3
   # Let it load, then exit with Ctrl+D
   ```

4. **Reduce max tokens**:
   - In app: Set "Max Tokens" to 500-800

5. **Lower temperature**:
   - In app: Set temperature to 0.5-0.7 (faster inference)

---

## Verification Checklist

Before using Ollama, verify:

- [ ] Ollama is installed and running (`ollama serve` in terminal)
- [ ] At least one model is pulled (`ollama list`)
- [ ] Connection works: `curl http://localhost:11434/api/tags`
- [ ] `.env` file has `OLLAMA_BASE_URL=http://localhost:11434`
- [ ] App is restarted after pulling new models
- [ ] System has at least 4GB free RAM
- [ ] Model is appropriate for your hardware

---

## Getting Help

**Check logs**:
```bash
# App logs are saved in app.log
tail -f app.log
```

**Test Ollama directly**:
```bash
ollama run phi3 "What is Python?"
```

**Reinstall a model**:
```bash
ollama rm phi3
ollama pull phi3
```

**Restart everything**:
```bash
# Stop app (Ctrl+C)
# Stop Ollama (Ctrl+C)
# Wait 30 seconds
ollama serve
# New terminal: streamlit run app.py
```

---

## Model Selection Guide

| Model | Size | Speed | Memory | Quality | Recommended For |
|-------|------|-------|--------|---------|-----------------|
| **phi3** | 2.7GB | ⭐⭐⭐⭐⭐ | 4GB | ⭐⭐⭐ | First-time users, slow systems |
| openchat | 3.5GB | ⭐⭐⭐⭐⭐ | 4GB | ⭐⭐⭐ | Fast & reliable |
| neural-chat | 4GB | ⭐⭐⭐⭐ | 6GB | ⭐⭐⭐ | Conversational |
| mistral | 4GB | ⭐⭐⭐ | 6GB | ⭐⭐⭐⭐ | Better quality, slower |
| llama2 | 3.8GB | ⭐⭐⭐ | 8GB | ⭐⭐⭐⭐ | More powerful |
| dolphin-mixtral | 26GB | ⭐⭐ | 16GB | ⭐⭐⭐⭐⭐ | High-end systems only |

**Recommendation**: Start with **phi3**, then experiment with others based on performance.
