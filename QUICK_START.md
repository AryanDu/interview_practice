# Quick Start Guide

## Prerequisites

1. Python 3.8 or higher
2. API keys for at least one LLM provider:
   - OpenAI (required for basic functionality)
   - Google Gemini (optional)
   - Anthropic Claude (optional)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here
```

You can get your API keys from:
- **OpenAI**: https://platform.openai.com/api-keys
- **Google**: https://makersuite.google.com/app/apikey
- **Anthropic**: https://console.anthropic.com/

### 3. Run the Application

**Windows:**
```bash
streamlit run app.py
```

Or use the provided batch file:
```bash
run.bat
```

**Linux/Mac:**
```bash
streamlit run app.py
```

Or use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

The app will open in your default web browser at `http://localhost:8501`

## Project Structure Overview

```
interview2/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── QUICK_START.md             # This file
├── .env                        # API keys (create this file)
├── utils/                      # Utility modules
│   ├── llm_handlers.py        # LLM provider integrations
│   ├── prompts.py             # Prompt engineering utilities
│   ├── security.py            # Security guards
│   ├── cost_calculator.py     # Cost calculation
│   ├── vector_db.py           # Vector database operations
│   ├── image_gen.py           # Image generation
│   └── validators.py          # Input validation
├── chains/                     # LangChain chains and agents
│   └── interview_chains.py
├── tests/                      # Testing utilities
│   └── jailbreak_tests.py     # Security testing
├── data/                       # Data storage
│   └── vector_db/             # Vector database files
├── templates/                  # Prompt templates
│   └── prompts/
└── jailbreak_results/         # Security test results
```

## Features Quick Reference

### Core Features (Required)
- ✅ Multiple LLM support (OpenAI, Gemini, Claude)
- ✅ 10+ prompt engineering techniques
- ✅ Configurable LLM parameters
- ✅ Security guards
- ✅ Multiple difficulty levels
- ✅ Job description integration (RAG)

### Optional Features (All Implemented)
- ✅ ChatGPT critique functionality
- ✅ Domain-specific optimization
- ✅ Enhanced security constraints
- ✅ All OpenAI settings as UI controls
- ✅ Multiple structured JSON output formats
- ✅ Cost calculation
- ✅ LLM validation (LLM as a judge)
- ✅ Jailbreak testing with Excel export
- ✅ Vector database duplicate detection
- ✅ Multiple LLM selection
- ✅ Image generation
- ✅ Full chatbot implementation
- ✅ LangChain chains and agents
- ✅ Analytics dashboard

## Usage Examples

### Basic Interview Prep

1. Select LLM provider (e.g., OpenAI)
2. Select model (e.g., gpt-4o-mini)
3. Choose prompt technique (e.g., Few-shot)
4. Enter domain (e.g., "Software Engineering")
5. Select difficulty (e.g., Medium)
6. Click "Generate Interview Questions"

### Advanced Usage with RAG

1. Enable "Use RAG (Job Description Context)"
2. Paste job description in the text area
3. Generate questions - they'll be tailored to the job description

### Chatbot Mode

1. Go to "💬 Chatbot" tab
2. Start chatting with the AI interviewer
3. Get real-time feedback and follow-up questions

### Security Testing

1. Go to "🔒 Security Testing" tab
2. Click "Run Jailbreak Tests"
3. Review results and export to Excel if needed

## Troubleshooting

### Issue: "API key not configured"
- **Solution**: Make sure your `.env` file exists and contains valid API keys

### Issue: "Module not found"
- **Solution**: Run `pip install -r requirements.txt` to install all dependencies

### Issue: Vector database errors
- **Solution**: The app will work without vector database. It's optional for duplicate detection

### Issue: Image generation not working
- **Solution**: Requires OpenAI API key. Feature is optional

## Next Steps

1. **Customize Prompts**: Edit `utils/prompts.py` to add your own prompt templates
2. **Adjust Security**: Modify `utils/security.py` to customize security rules
3. **Add Features**: Extend the codebase with your own features
4. **Deploy**: Follow deployment guides for Streamlit apps on cloud platforms

## Support

- Check `README.md` for detailed documentation
- Review code comments for implementation details
- Test with jailbreak tests to verify security

---

**Happy Interview Practicing! 🎯**
