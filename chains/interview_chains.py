"""
LangChain chains and agents for interview preparation
"""
from typing import Optional, List, Dict, Any

try:
    from langchain.prompts import PromptTemplate
except ImportError:
    # Fallback: create a simple PromptTemplate class
    class PromptTemplate:
        def __init__(self, input_variables: List[str], template: str):
            self.input_variables = input_variables
            self.template = template
        
        def format(self, **kwargs) -> str:
            return self.template.format(**kwargs)

# Mock classes for LLMChain since it's deprecated
class LLMChain:
    def __init__(self, llm, prompt, output_key: str = "output"):
        self.llm = llm
        self.prompt = prompt
        self.output_key = output_key
    
    def run(self, **kwargs):
        return self.llm.predict(self.prompt.format(**kwargs))

class ConversationBufferMemory:
    def __init__(self):
        self.buffer = []
    
    def add_user_input(self, user_input: str):
        self.buffer.append({"type": "user", "content": user_input})
    
    def add_ai_message(self, ai_message: str):
        self.buffer.append({"type": "ai", "content": ai_message})

class AgentType:
    ZERO_SHOT_REACT_DESCRIPTION = "zero-shot-react-description"

def initialize_agent(*args, **kwargs):
    """Mock initialize_agent function"""
    return None

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from config import Config


class InterviewChain:
    """LangChain-based interview preparation chain"""
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        self.provider = provider.lower()
        
        if self.provider == "openai":
            self.llm = ChatOpenAI(
                model=model or Config.DEFAULT_OPENAI_MODEL,
                temperature=Config.DEFAULT_TEMPERATURE,
                openai_api_key=Config.OPENAI_API_KEY
            )
        elif self.provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model=model or Config.DEFAULT_GEMINI_MODEL,
                temperature=Config.DEFAULT_TEMPERATURE,
                google_api_key=Config.GOOGLE_API_KEY
            )
        elif self.provider == "claude":
            self.llm = ChatAnthropic(
                model=model or Config.DEFAULT_CLAUDE_MODEL,
                temperature=Config.DEFAULT_TEMPERATURE,
                anthropic_api_key=Config.ANTHROPIC_API_KEY
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        self.memory = ConversationBufferMemory()
    
    def create_question_generation_chain(self) -> LLMChain:
        """Create a chain for generating interview questions"""
        prompt = PromptTemplate(
            input_variables=["domain", "difficulty", "job_description"],
            template="""You are an expert interview coach.
            
            Domain: {domain}
            Difficulty: {difficulty}
            Job Description: {job_description}
            
            Generate 5-7 interview questions appropriate for this role.
            Make questions relevant, challenging, and practical.
            
            Questions:"""
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="questions"
        )
    
    def create_answer_evaluation_chain(self) -> LLMChain:
        """Create a chain for evaluating candidate answers"""
        prompt = PromptTemplate(
            input_variables=["question", "answer"],
            template="""You are an expert interviewer evaluating a candidate's answer.
            
            Question: {question}
            Candidate's Answer: {answer}
            
            Provide:
            1. Score (1-10)
            2. Strengths
            3. Areas for improvement
            4. Detailed feedback
            
            Evaluation:"""
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="evaluation"
        )
    
    def create_sequential_chain(
        self,
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a sequential chain for complete interview preparation"""
        question_chain = self.create_question_generation_chain()
        answer_chain = self.create_answer_evaluation_chain()
        
        # Return a dict representing the chain setup
        overall_chain = {
            "chains": [question_chain, answer_chain],
            "input_variables": ["domain", "difficulty", "job_description"],
            "output_variables": ["questions", "evaluation"],
            "verbose": True
        }
        
        return overall_chain
    
    def create_interview_agent(self) -> Any:
        """Create an agent for interactive interview practice"""
        tools = []  # Add tools as needed
        
        agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent
    
    def run_interview_chain(
        self,
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None
    ) -> Dict[str, str]:
        """Run the complete interview preparation chain"""
        # Use the question generation chain directly
        question_chain = self.create_question_generation_chain()
        
        # Generate the prompt and get the response
        prompt_text = question_chain.prompt.format(
            domain=domain,
            difficulty=difficulty,
            job_description=job_description or "Not provided"
        )
        
        # Invoke the LLM with the formatted prompt
        response = self.llm.invoke(prompt_text)
        
        result = {
            "questions": response.content if hasattr(response, 'content') else str(response)
        }
        
        return result
