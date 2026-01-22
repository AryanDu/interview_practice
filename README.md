# Interview Practice App

An AI-powered interview preparation application built with Streamlit, featuring multiple LLM providers, prompt engineering, and advanced features.

## Features

### Core Features
- ✅ Multiple LLM support (OpenAI, Gemini, Claude)
- ✅ 5+ prompt engineering techniques (Few-shot, Chain-of-Thought, Zero-shot, etc.)
- ✅ Configurable OpenAI parameters (temperature, top-p, frequency penalty, etc.)
- ✅ Security guards to prevent misuse
- ✅ Multiple difficulty levels (easy, medium, hard)
- ✅ Job description integration (RAG)

### Optional Features Implemented

**Easy:**
- ChatGPT critique functionality
- Domain-specific prompt optimization
- Enhanced security constraints
- Difficulty level simulation
- Concise vs detailed response optimization
- Interviewer guidelines generation
- AI persona mock interviews

**Medium:**
- All OpenAI settings as UI controls
- Multiple structured JSON output formats
- Cost calculation per prompt
- LLM validation (LLM as a judge)
- Jailbreak testing with Excel export
- Job description RAG integration
- Multiple LLM selection
- Image generation integration

**Hard:**
- Full chatbot implementation
- LangChain chains and agents
- Vector database for duplicate detection
- Deployment configuration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
interview2/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration management
├── utils/
│   ├── __init__.py
│   ├── llm_handlers.py   # LLM provider integrations
│   ├── prompts.py        # Prompt engineering utilities
│   ├── security.py       # Security guards
│   ├── cost_calculator.py # Cost calculation
│   ├── vector_db.py      # Vector database operations
│   ├── image_gen.py      # Image generation
│   └── validators.py     # Input validation
├── chains/
│   ├── __init__.py
│   └── interview_chains.py # LangChain chains and agents
├── templates/
│   └── prompts/          # Prompt templates
├── data/
│   └── vector_db/        # Vector database storage
├── tests/
│   └── jailbreak_tests.py # Security testing
├── requirements.txt
├── .env                  # API keys (not in git)
└── README.md
```

## Usage

1. Select your LLM provider
2. Configure interview parameters (domain, difficulty, style)
3. Enter job description (optional, for RAG)
4. Choose prompt engineering technique
5. Adjust LLM parameters
6. Start your interview practice!

## Security

The app includes multiple security guards:
- Input validation and sanitization
- Prompt injection detection
- Rate limiting
- Content filtering

## License

MIT
