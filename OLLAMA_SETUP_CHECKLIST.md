# Ollama Setup Checklist

## ✅ Pre-Setup Requirements

- [ ] System has at least 4GB free RAM (8GB recommended)
- [ ] At least 10GB free disk space
- [ ] Python 3.8 or higher installed
- [ ] Internet connection (for downloading models)

---

## ✅ Installation Steps

### 1. Install Ollama
- [ ] Download Ollama from [ollama.ai](https://ollama.ai)
- [ ] Install for your OS (Windows, Mac, or Linux)
- [ ] Verify installation:
  ```bash
  ollama --version
  ```

### 2. Verify Python Environment
- [ ] Python installed: `python --version`
- [ ] Required packages installed:
  ```bash
  pip install -r requirements.txt
  ```

### 3. Configure .env File
- [ ] `.env` file exists in project root
- [ ] Contains: `OLLAMA_BASE_URL=http://localhost:11434`
- [ ] For remote: `OLLAMA_BASE_URL=http://your-ip:11434`

---

## ✅ First Run

### Terminal 1: Start Ollama
```bash
ollama serve
```
- [ ] Shows "Listening on 127.0.0.1:11434"
- [ ] Leave this terminal open

### Terminal 2: Pull a Model
```bash
# Recommended for first time
ollama pull phi3

# Or choose another
ollama pull mistral
ollama pull neural-chat
```
- [ ] Model downloaded successfully
- [ ] Check with: `ollama list`

### Terminal 3: Start App
```bash
streamlit run app.py
```
- [ ] App opens in browser
- [ ] Sidebar shows ✅ ollama status

---

## ✅ Verify Ollama Works

### In Terminal
```bash
# Test Ollama directly
ollama run phi3 "Hello, how are you?"
```
- [ ] Gets a response in a few seconds

### In App
1. [ ] Select "ollama" from provider dropdown
2. [ ] Select a model (e.g., "phi3")
3. [ ] Click "Generate response" or similar
4. [ ] Gets response without timeout error

---

## ✅ Troubleshooting

If you see errors:

### "Cannot connect to Ollama"
- [ ] Ollama is running (`ollama serve`)
- [ ] URL is correct in .env
- [ ] Firewall allows port 11434
- [ ] Check: `curl http://localhost:11434/api/tags`

### "Read timed out"
- [ ] Use faster model (phi3)
- [ ] Reduce max tokens to 500
- [ ] Check system RAM with Task Manager
- [ ] See OLLAMA_TROUBLESHOOTING.md

### "Model not found"
- [ ] Pull model: `ollama pull phi3`
- [ ] Check: `ollama list`
- [ ] Restart app after pulling

---

## ✅ Performance Tips

To optimize Ollama performance:

- [ ] Use **phi3** initially (fastest)
- [ ] Keep "Max Tokens" at 500-1000
- [ ] Keep "Temperature" at 0.5-0.7
- [ ] Close other apps to free RAM
- [ ] Enable GPU support if available
- [ ] Monitor system resources

---

## ✅ Model Recommendation

For different systems:

**Slow/Limited System (4GB RAM)**
- [ ] Use phi3
- [ ] Set max_tokens = 500

**Medium System (8GB RAM)**
- [ ] Use phi3 or openchat
- [ ] Set max_tokens = 1000

**High-end System (16GB RAM, GPU)**
- [ ] Try mistral, llama2, or dolphin-mixtral
- [ ] Set max_tokens = 2000

---

## Common Commands Reference

```bash
# Start Ollama server
ollama serve

# Pull a model
ollama pull phi3

# List installed models
ollama list

# Remove a model
ollama rm phi3

# Test a model
ollama run phi3 "Your question here"

# Check Ollama status
curl http://localhost:11434/api/tags
```

---

## Documentation Files

- [ ] Read **OLLAMA_INTEGRATION.md** - Full technical details
- [ ] Read **OLLAMA_QUICK_START.md** - 5-minute setup
- [ ] Read **OLLAMA_TROUBLESHOOTING.md** - Problem solving
- [ ] Check **requirements.txt** - All dependencies

---

## Next Steps

Once Ollama is working:

1. [ ] Try different models (mistral, neural-chat)
2. [ ] Adjust temperature and max_tokens
3. [ ] Use Ollama for interview practice
4. [ ] Compare with cloud APIs (OpenAI, Gemini)
5. [ ] Enable GPU support for faster inference

---

**Status**: Ready to use Ollama! 🚀
