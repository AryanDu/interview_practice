"""
LLM handler implementations for OpenAI, Gemini, Claude, Grok, and Ollama
"""
from typing import List, Dict, Optional, Any
import openai
import google.generativeai as genai
import anthropic
import requests
from config import Config
import json
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OpenAIHandler:
    """Handler for OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        # Log a masked version of the key for debugging (do not expose full key)
        if self.api_key:
            try:
                masked = f"***{self.api_key[-6:]}" if len(self.api_key) > 6 else "***"
            except Exception:
                masked = "***"
            logger.info(f"OpenAI API key present (masked): {masked}")
            openai.api_key = self.api_key
        else:
            logger.info("OpenAI API key not present")
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        frequency_penalty: float = None,
        presence_penalty: float = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate response from OpenAI"""
        if not self.client:
            logger.error("OpenAI API key not configured")
            raise ValueError("OpenAI API key not configured")
        
        model = model or Config.DEFAULT_OPENAI_MODEL
        temperature = temperature if temperature is not None else Config.DEFAULT_TEMPERATURE
        top_p = top_p if top_p is not None else Config.DEFAULT_TOP_P
        max_tokens = max_tokens or Config.DEFAULT_MAX_TOKENS
        frequency_penalty = frequency_penalty if frequency_penalty is not None else Config.DEFAULT_FREQUENCY_PENALTY
        presence_penalty = presence_penalty if presence_penalty is not None else Config.DEFAULT_PRESENCE_PENALTY
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        # Determine if the requested model is a chat model or a non-chat/completions-style model.
        # Some models (e.g., gpt-5.2-codex, older Codex/text-* models) are not supported by the
        # chat completions endpoint and must be called via the responses/completions endpoint.
        lower_model = (model or Config.DEFAULT_OPENAI_MODEL).lower()
        non_chat_indicators = ["codex", "code-", "text-", "completion", "gpt-5"]
        is_non_chat = any(ind in lower_model for ind in non_chat_indicators)

        # If streaming and chat model, use chat streaming as before
        if not is_non_chat:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=stream
            )

            if stream:
                return response  # Return stream object

            return {
                "content": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": getattr(response.usage, 'prompt_tokens', None),
                    "completion_tokens": getattr(response.usage, 'completion_tokens', None),
                    "total_tokens": getattr(response.usage, 'total_tokens', None)
                },
                "finish_reason": response.choices[0].finish_reason
            }

        # Non-chat model: use responses (or completions) endpoint
        try:
            # Prefer responses API (newer). Map parameters accordingly.
            # Note: some models (e.g., gpt-5.2-codex) do not support all parameters.
            logger.info(f"Using non-chat endpoint for model: {model}")
            
            # Build kwargs, filtering out unsupported parameters for certain models
            resp_kwargs = {
                "model": model,
                "input": user_prompt,
                "max_output_tokens": max_tokens
            }
            
            # gpt-5.2-codex and some other codex models don't support temperature/top_p
            if not any(x in lower_model for x in ["codex", "gpt-5"]):
                if temperature is not None:
                    resp_kwargs["temperature"] = temperature
                if top_p is not None:
                    resp_kwargs["top_p"] = top_p
            
            resp = self.client.responses.create(**resp_kwargs)

            # Extract text content from responses API variations
            content = ""
            if hasattr(resp, 'output_text') and resp.output_text:
                content = resp.output_text
            else:
                # Try to extract from resp.output which may be a list of dictionaries
                try:
                    outputs = getattr(resp, 'output', None)
                    if isinstance(outputs, list) and len(outputs) > 0:
                        # outputs elements can be dicts with 'content'
                        texts = []
                        for item in outputs:
                            if isinstance(item, dict):
                                # 'content' may be a list of { 'type': 'output_text', 'text': '...' }
                                if 'content' in item and isinstance(item['content'], list):
                                    for c in item['content']:
                                        if isinstance(c, dict) and 'text' in c:
                                            texts.append(c['text'])
                                        elif isinstance(c, str):
                                            texts.append(c)
                                elif 'text' in item:
                                    texts.append(item['text'])
                            elif isinstance(item, str):
                                texts.append(item)
                        content = "\n".join(texts)
                except Exception:
                    content = str(resp)

            usage = {}
            try:
                usage_obj = getattr(resp, 'usage', None)
                if usage_obj:
                    usage = {
                        'prompt_tokens': getattr(usage_obj, 'prompt_tokens', None),
                        'completion_tokens': getattr(usage_obj, 'completion_tokens', None),
                        'total_tokens': getattr(usage_obj, 'total_tokens', None)
                    }
            except Exception:
                usage = {}

            return {
                'content': content,
                'model': model,
                'usage': usage,
                'finish_reason': None
            }

        except Exception as e:
            # If responses endpoint fails with a model type error, surface the message
            logger.error(f"OpenAI non-chat request failed: {e}")
            raise


class GeminiHandler:
    """Handler for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GOOGLE_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model_name = Config.DEFAULT_GEMINI_MODEL
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Gemini"""
        if not self.api_key:
            logger.error("Gemini API key not configured")
            raise ValueError("Gemini API key not configured")
        
        model_name = model or self.model_name
        model = genai.GenerativeModel(model_name)
        
        # Combine system and user prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        generation_config = {
            "temperature": temperature if temperature is not None else Config.DEFAULT_TEMPERATURE,
            "top_p": top_p if top_p is not None else Config.DEFAULT_TOP_P,
            "max_output_tokens": max_tokens or Config.DEFAULT_MAX_TOKENS,
        }
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return {
            "content": response.text,
            "model": model_name,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            },
            "finish_reason": response.candidates[0].finish_reason if response.candidates else None
        }


class ClaudeHandler:
    """Handler for Anthropic Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        self.model_name = Config.DEFAULT_CLAUDE_MODEL
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Claude"""
        if not self.client:
            logger.error("Claude API key not configured")
            raise ValueError("Claude API key not configured")
        
        model_name = model or self.model_name
        
        response = self.client.messages.create(
            model=model_name,
            max_tokens=max_tokens or Config.DEFAULT_MAX_TOKENS,
            temperature=temperature if temperature is not None else Config.DEFAULT_TEMPERATURE,
            top_p=top_p if top_p is not None else Config.DEFAULT_TOP_P,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return {
            "content": response.content[0].text,
            "model": model_name,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "finish_reason": response.stop_reason
        }


class GrokHandler:
    """Handler for xAI Grok API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GROK_API_KEY
        self.base_url = "https://api.x.ai/v1"
        self.model_name = Config.DEFAULT_GROK_MODEL
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Grok via xAI API"""
        if not self.api_key:
            logger.error("Grok API key not configured")
            raise ValueError("Grok API key not configured")
        
        model_name = model or self.model_name
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature if temperature is not None else Config.DEFAULT_TEMPERATURE,
            "top_p": top_p if top_p is not None else Config.DEFAULT_TOP_P,
            "max_tokens": max_tokens or Config.DEFAULT_MAX_TOKENS,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": model_name,
                "usage": {
                    "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": data.get("usage", {}).get("total_tokens", 0)
                },
                "finish_reason": data["choices"][0].get("finish_reason", "stop")
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Grok API error: {str(e)}")
            raise ValueError(f"Grok API error: {str(e)}")


class OllamaHandler:
    """Handler for Ollama local LLM API"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.model_name = Config.DEFAULT_OLLAMA_MODEL
        self.connection_verified = self._verify_connection()
    
    def _verify_connection(self) -> bool:
        """Verify that Ollama service is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"Ollama service verified at {self.base_url}")
            return True
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Ollama not running at {self.base_url}. Start with: ollama serve")
            return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"Ollama service not accessible at {self.base_url}: {str(e)}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models if models else [self.model_name]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Ollama models: {str(e)}")
            return [self.model_name]
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Ollama local LLM"""
        model_name = model or self.model_name
        
        if not self.connection_verified:
            raise ValueError(
                f"Ollama service is not running at {self.base_url}. "
                f"Please start Ollama with: ollama serve"
            )
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Ollama uses slightly different parameter names
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature if temperature is not None else Config.DEFAULT_TEMPERATURE,
            "top_p": top_p if top_p is not None else Config.DEFAULT_TOP_P,
            "num_predict": max_tokens or Config.DEFAULT_MAX_TOKENS,
            "stream": False
        }
        
        try:
            logger.info(f"Generating response with Ollama model: {model_name}")
            
            # Use longer timeout for initial request, with connection timeout
            response = requests.post(
                f"{self.base_url}/api/chat",
                headers=headers,
                json=payload,
                timeout=(10, 600)  # (connection timeout, read timeout)
            )
            response.raise_for_status()
            data = response.json()
            
            content = data.get("message", {}).get("content", "")
            if not content:
                raise ValueError("Empty response from Ollama. Model may not be installed.")
            
            return {
                "content": content,
                "model": model_name,
                "usage": {
                    "prompt_tokens": 0,  # Ollama doesn't return token counts
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "finish_reason": "stop"
            }
        except requests.exceptions.Timeout as e:
            error_msg = (
                f"Ollama request timed out after 10 minutes. "
                f"Model '{model_name}' may be too large for your system or not installed. "
                f"Try: ollama pull {model_name}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = (
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: ollama serve"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama API error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error with Ollama: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)


class LLMManager:
    """Manager for multiple LLM providers"""
    
    def __init__(self):
        self.openai_handler = OpenAIHandler() if Config.OPENAI_API_KEY else None
        self.gemini_handler = GeminiHandler() if Config.GOOGLE_API_KEY else None
        self.claude_handler = ClaudeHandler() if Config.ANTHROPIC_API_KEY else None
        self.grok_handler = GrokHandler() if Config.GROK_API_KEY else None
        self.ollama_handler = OllamaHandler() if Config.OLLAMA_BASE_URL else None
    
    def get_handler(self, provider: str):
        """Get handler for specified provider"""
        handlers = {
            "openai": self.openai_handler,
            "gemini": self.gemini_handler,
            "claude": self.claude_handler,
            "grok": self.grok_handler,
            "ollama": self.ollama_handler
        }
        handler = handlers.get(provider.lower())
        if not handler:
            logger.error(f"Provider {provider} not available or not configured")
            raise ValueError(f"Provider {provider} not available or not configured")
        return handler
    
    def generate_response(
        self,
        provider: str,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified provider"""
        handler = self.get_handler(provider)
        return handler.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            **kwargs
        )
    
    def validate_response(
        self,
        main_provider: str,
        validator_provider: str,
        main_response: str,
        original_prompt: str
    ) -> Dict[str, Any]:
        """Use a second LLM to validate the main LLM's response"""
        validation_prompt = f"""
        Please evaluate the following interview preparation response for quality, accuracy, and appropriateness.
        
        Original prompt: {original_prompt}
        
        Response to evaluate:
        {main_response}
        
        Provide:
        1. Quality score (1-10)
        2. Strengths
        3. Weaknesses
        4. Suggestions for improvement
        5. Overall assessment (pass/fail)
        """
        
        system_prompt = "You are an expert evaluator of AI-generated interview preparation content."
        
        validation_response = self.generate_response(
            provider=validator_provider,
            system_prompt=system_prompt,
            user_prompt=validation_prompt
        )
        
        return {
            "validator_provider": validator_provider,
            "validation": validation_response["content"],
            "original_response": main_response
        }
