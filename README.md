# 💼 Interview Practice App

A comprehensive AI-powered interview preparation platform built with Streamlit. Features multiple LLM providers (OpenAI, Gemini, Claude, Ollama), advanced prompt engineering techniques, real-time mock interviews with AI personas, and intelligent study mode with CV/job description integration. Includes security testing, analytics, and cost tracking for a complete interview prep experience.

## 🚀 Features

### Quiz & Progress Tracker (added in `quiz-progress-tracker` branch)
- Generate 5–20 multiple-choice questions from a topic, pasted notes, or TXT/Markdown study material.
- Submit answers and review correct answers with explanations.
- Group performance by the AI-generated topic labels to highlight strengths and areas needing practice.
- Save attempts to SQLite and download a CSV history.
- Uses the Gemini Developer API free tier when available; no paid plan is required, but provider quotas apply.
- Configure `GEMINI_API_KEY` in Streamlit Community Cloud → App settings → Secrets, or as a local environment variable.
- **Storage note:** SQLite is suitable for local use. Free cloud app filesystems may reset, so download your CSV history if you need a backup.


### Core Features
- ✅ **Multiple LLM Support**: OpenAI, Gemini, Claude, and Ollama (local models)
- ✅ **5+ Prompt Engineering Techniques**: Few-shot, Chain-of-Thought, Zero-shot, and more
- ✅ **Configurable Parameters**: Temperature, top-p, frequency penalty, max tokens
- ✅ **Security Guards**: Input validation, prompt injection detection, rate limiting
- ✅ **Multiple Difficulty Levels**: Easy, medium, hard interview questions
- ✅ **Job Description Integration**: RAG with vector database for personalized questions
- ✅ **CV Upload Support**: PDF/TXT for personalized interview preparation

### UI Tabs

**📚 Interview Prep (Study Mode)**
- Generate study packs with questions, answers, and tips
- Upload CV and job description for personalization
- Structured JSON output format
- Export study materials

**🎭 Mock Interview (AI Interviewer)**
- 5 AI personas: Friendly, Strict, Neutral, Technical, Behavioral
- Real-time interview simulation with scoring
- Pass/fail evaluation (80% threshold)
- Detailed feedback on each answer

**💬 Chatbot**
- Interactive conversation with AI
- Context-aware responses
- Multiple provider support

**📊 Analytics**
- Interview performance tracking
- Cost calculations per session
- Usage statistics

**🔒 Security Testing**
- Jailbreak testing suite
- Excel export of test results
- Prompt injection detection

**🎨 Visual Tools**
- Result card generation
- Interview mistake snapshots
- Shareable image exports

### Advanced Features

**Architecture & Code Quality:**
- ✅ Modular UI components (separate tabs)
- ✅ Jinja2 templates for all prompts
- ✅ Python logging (file + console)
- ✅ Ruff linting configuration
- ✅ Poetry dependency management
- ✅ Comprehensive test coverage

**LLM Integration:**
- ✅ Multiple structured JSON output formats
- ✅ Cost calculation per prompt
- ✅ LLM validation (LLM as a judge)
- ✅ LangChain chains and agents
- ✅ Vector database (ChromaDB) for RAG
- ✅ Dynamic model discovery for Ollama

**Security:**
- ✅ Input validation and sanitization
- ✅ Prompt injection detection
- ✅ Rate limiting
- ✅ Content filtering
- ✅ Automated jailbreak testing

## 🛠️ Setup

### Quick Start (5 minutes)

**Option 1: Using pip**
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with API keys
cp .env.example .env  # Edit with your keys

# Run the app
streamlit run app.py
```

**Option 2: Using Poetry (Recommended)**
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run the app
streamlit run app.py
```

**Windows Users:** Use `run.bat` for quick launch

### API Keys Configuration

Create a `.env` file in the project root:

```env
# Cloud LLM Providers (Optional - choose at least one)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here

# Local LLM Provider (Optional)
OLLAMA_BASE_URL=http://localhost:11434
```

**Get your API keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Anthropic Claude**: https://console.anthropic.com/

### Ollama Setup (Optional - for local models)

1. **Install Ollama** from [ollama.ai](https://ollama.ai)

2. **Start Ollama server:**
   ```bash
   ollama serve
   ```

3. **Pull a model:**
   ```bash
   ollama pull phi3      # Recommended for interview prep
   ollama pull mistral   # Alternative option
   ollama pull llama2    # Another option
   ```

4. **Verify installation:**
   - The app will auto-detect available Ollama models
   - Select "Ollama" from the LLM provider dropdown

📖 **Detailed Ollama instructions:** See [OLLAMA_QUICK_START.md](OLLAMA_QUICK_START.md)

## 📁 Project Structure

```
ubusin-AE.1.4/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration management
├── requirements.txt                # pip dependencies
├── pyproject.toml                  # Poetry configuration
├── run.bat / run.sh               # Quick launch scripts
│
├── ui/                            # UI Components (modular tabs)
│   ├── interview_prep.py          # Study mode tab
│   ├── mock_interview.py          # AI interviewer tab
│   ├── chatbot.py                 # Chatbot tab
│   ├── analytics.py               # Analytics tab
│   ├── security.py                # Security testing tab
│   ├── visual_tools.py            # Image generation tab
│   └── sidebar.py                 # Sidebar configuration
│
├── utils/                         # Core utilities
│   ├── llm_handlers.py           # LLM provider integrations
│   ├── prompts.py                # Prompt engineering with Jinja2
│   ├── security.py               # Security guards
│   ├── cost_calculator.py        # Cost tracking
│   ├── vector_db.py              # ChromaDB integration
│   ├── image_gen.py              # Image generation
│   ├── structured_outputs.py     # JSON output schemas
│   └── validators.py             # Input validation
│
├── chains/                        # LangChain integration
│   └── interview_chains.py       # Chains and agents
│
├── templates/                     # Jinja2 templates
│   └── prompts/                  # Prompt templates
│       ├── interview_question.jinja2
│       ├── interview_guidelines.jinja2
│       ├── structured_output.jinja2
│       ├── system_prompt.jinja2
│       ├── user_prompt.jinja2
│       └── assistant_prompt.jinja2
│
├── tests/                         # Test suite
│   ├── test_structured_outputs.py
│   ├── test_interview_study_mode.py
│   └── jailbreak_tests.py
│
├── data/                          # Data storage
│   └── vector_db/                # ChromaDB vector store
│
└── docs/                          # Documentation
    ├── README.md                  # This file
    ├── QUICK_START.md            # Quick start guide
    ├── IMPROVEMENTS_SUMMARY.md   # Feature changelog
    ├── PROJECT_STRUCTURE.md      # Detailed structure
    ├── OLLAMA_INTEGRATION.md     # Ollama setup
    ├── OLLAMA_QUICK_START.md     # Ollama quick guide
    ├── OLLAMA_SETUP_CHECKLIST.md # Ollama checklist
    └── OLLAMA_TROUBLESHOOTING.md # Ollama issues
```

📖 **See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed documentation**

## 🎯 Usage

### Basic Workflow

1. **Select LLM Provider** in sidebar
   - OpenAI (GPT-3.5/4)
   - Google Gemini
   - Anthropic Claude
   - Ollama (local models)

2. **Configure Interview Parameters**
   - Domain (Software Engineering, Data Science, etc.)
   - Difficulty level (Easy, Medium, Hard)
   - Response style (Concise, Detailed)

3. **Optional: Upload Context**
   - CV/Resume (PDF or TXT)
   - Job description for personalization

4. **Choose Prompt Technique**
   - Few-shot learning
   - Chain-of-thought
   - Zero-shot
   - And more...

5. **Adjust LLM Settings**
   - Temperature, top-p
   - Frequency/presence penalty
   - Max tokens

6. **Select Your Mode**
   - **Interview Prep**: Generate study materials
   - **Mock Interview**: Real-time AI interview simulation
   - **Chatbot**: Free-form Q&A
   - **Analytics**: Track your performance
   - **Security Testing**: Test prompt security
   - **Visual Tools**: Generate result cards

### Mock Interview Scoring System

- **5 questions** (mix of technical and behavioral)
- **25 points** per answer
- **Total: 125 points**

**Pass Criteria:**
- ✅ Pass: ≥80% (100+ points) - "Congratulations! You passed!"
- ⚠️ Borderline: 75-79% - "Close to passing"
- ❌ Fail: <75% - "We shall let you know"

## 📚 Documentation

- [QUICK_START.md](QUICK_START.md) - Get started in 5 minutes
- [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) - Complete feature list
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Architecture details
- [OLLAMA_INTEGRATION.md](OLLAMA_INTEGRATION.md) - Ollama setup guide
- [OLLAMA_QUICK_START.md](OLLAMA_QUICK_START.md) - Quick Ollama guide
- [OLLAMA_TROUBLESHOOTING.md](OLLAMA_TROUBLESHOOTING.md) - Fix common issues

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_structured_outputs.py

# Run jailbreak security tests
python tests/jailbreak_tests.py
```

**Test Coverage:**
- ✅ Structured output validation
- ✅ Mock interview scoring logic
- ✅ Jailbreak detection
- ✅ Study mode functionality

## 🔒 Security Features

The app includes multiple security layers:

1. **Input Validation**
   - File type checking (CV uploads)
   - Text length limits
   - Malicious content detection

2. **Prompt Injection Protection**
   - Pattern detection for common attacks
   - System prompt isolation
   - Rate limiting per session

3. **Content Filtering**
   - Inappropriate content detection
   - Professional language enforcement

4. **Automated Testing**
   - 10+ jailbreak test scenarios
   - Excel export of results
   - Continuous monitoring

## 🛠️ Development

### Code Quality Tools

- **Ruff**: Fast Python linter (configured in `.ruff.toml`)
- **Logging**: Console + file logging (`app.log`)
- **Type hints**: Full type annotation support
- **Jinja2 templates**: Separation of prompts from code

### Run Linting

```bash
ruff check .
ruff format .
```

### Project Management

```bash
# Using Poetry
poetry install        # Install dependencies
poetry add package    # Add new package
poetry shell         # Activate venv

# Using pip
pip install -r requirements.txt
```

## 🚀 Deployment

The app is ready for deployment on:
- **Streamlit Cloud**: Push to GitHub and deploy
- **Docker**: Containerized deployment
- **Local server**: Run with custom configs

See deployment instructions in your preferred platform's documentation.

## 📊 Performance

- **Response time**: 2-5 seconds per question (varies by provider)
- **Cost**: Calculated per prompt (see Analytics tab)
- **Offline mode**: Available with Ollama local models
- **Concurrent users**: Scalable with Streamlit Cloud

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional LLM providers
- More prompt engineering techniques
- UI/UX enhancements
- Test coverage expansion
- Documentation improvements

## 📄 License

MIT License - See LICENSE file for details

## 🙋 Support

**Having issues?**
- Check [OLLAMA_TROUBLESHOOTING.md](OLLAMA_TROUBLESHOOTING.md) for Ollama issues
- Review [QUICK_START.md](QUICK_START.md) for setup problems
- Check API key configuration in `.env`
- Verify Python version (3.10+ required)

**Common Issues:**
- Ollama not detected → Ensure `ollama serve` is running
- API key errors → Check `.env` file format
- Import errors → Run `pip install -r requirements.txt` again

---

**Built with ❤️ for interview preparation**
