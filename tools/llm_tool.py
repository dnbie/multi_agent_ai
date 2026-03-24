"""
LLM Tool - Integration with Google Gemini and OpenAI APIs
Provides text generation capabilities for all agents
"""

import os
import time
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def generate_with_context(self, prompt: str, context: str, **kwargs) -> str:
        pass


class GeminiLLM(BaseLLM):
    """Google Gemini API integration with automatic model rotation on quota errors."""

    # Free-tier friendly models in priority order (fastest/cheapest first)
    FREE_MODEL_PRIORITY = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-pro",
    ]

    def __init__(self, api_key: str, preferred_model: str = None):
        self.api_key = api_key
        self.preferred_model = preferred_model
        self.model = None
        self._genai = None
        self._model_names: List[str] = []   # ordered candidates discovered at init
        self._current_model_idx: int = 0
        self._quota_exhausted: set = set()  # model names that hit 429/quota
        self._initialize()

    def _initialize(self):
        """Discover available generateContent-capable models, ranked by free-tier friendliness."""
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._genai = genai

            # If a specific model was requested, skip auto-discovery
            if self.preferred_model:
                self._model_names = [self.preferred_model]
                self._current_model_idx = 0
                self._load_model(self.preferred_model)
                return

            api_models = list(genai.list_models())
            available: Dict[str, str] = {}  # short_name -> full_name

            for m in api_models:
                methods = getattr(m, "supported_generation_methods", []) or []
                if "generateContent" not in methods:
                    continue
                full = getattr(m, "name", "")
                short = full.split("/", 1)[1] if "/" in full else full
                lower = short.lower()
                # Skip non-text / quota-zero families
                if any(t in lower for t in ["preview", "experimental", "computer-use", "embedding", "aqa"]):
                    continue
                if "gemini" in lower:
                    available[short] = full

            # Build ordered list: priority names first, then anything else
            ordered = []
            for pname in self.FREE_MODEL_PRIORITY:
                if pname in available:
                    ordered.append(pname)
            for name in available:
                if name not in ordered:
                    ordered.append(name)

            if not ordered:
                raise Exception("No usable Gemini models found for this API key.")

            self._model_names = ordered
            self._current_model_idx = 0
            self._load_model(self._model_names[0])

        except ImportError:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini: {str(e)}")

    def _load_model(self, model_name: str):
        """Load a specific model by short name."""
        self.model = self._genai.GenerativeModel(model_name)
        self._active_model_name = model_name
        print(f"[GeminiLLM] Using model: {model_name}")

    def _rotate_model(self) -> bool:
        """Try the next available model. Returns True if rotation succeeded."""
        self._quota_exhausted.add(self._active_model_name)
        for idx, name in enumerate(self._model_names):
            if name not in self._quota_exhausted:
                self._current_model_idx = idx
                self._load_model(name)
                print(f"[GeminiLLM] Rotated to model: {name}")
                return True
        return False  # all models exhausted

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Generate text, rotating models automatically on quota/rate-limit errors."""
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        attempts = 0
        max_attempts = len(self._model_names)

        while attempts < max_attempts:
            attempts += 1
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text

            except Exception as e:
                err_str = str(e).lower()
                is_quota = any(k in err_str for k in [
                    "429", "quota", "rate limit", "resource_exhausted",
                    "ratequota", "exceeded", "too many"
                ])
                is_blocked = "api_key_service_blocked" in err_str or "403" in err_str

                if is_quota or is_blocked:
                    model_label = getattr(self, "_active_model_name", "unknown")
                    print(f"[GeminiLLM] Model '{model_label}' hit quota/block — trying next model...")
                    if not self._rotate_model():
                        return (
                            "All available Gemini models have hit their quota. "
                            "Please wait a while or add billing to your Google AI account."
                        )
                    # Small back-off before retry
                    time.sleep(1)
                else:
                    return f"Error generating response: {str(e)}"

        return "Failed to generate after trying all available models."

    def generate_with_context(self, prompt: str, context: str, temperature: float = 0.7) -> str:
        """Generate with additional context"""
        full_prompt = f"Context:\n{context}\n\nTask:\n{prompt}"
        return self.generate(full_prompt, temperature)


class OpenAILLM(BaseLLM):
    """OpenAI API integration"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model_name = model
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI: {str(e)}")
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Generate text using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_with_context(self, prompt: str, context: str, temperature: float = 0.7) -> str:
        """Generate with additional context"""
        full_prompt = f"Context:\n{context}\n\nTask:\n{prompt}"
        return self.generate(full_prompt, temperature)


# ── Session-level model override ──────────────────────────────────────────────
# Set by the UI; picked up by every LLMTool() call in this process.
_MODEL_OVERRIDE: Dict[str, Optional[str]] = {"provider": None, "model": None}


def set_model_override(provider: str, model: str) -> None:
    """Override the active LLM provider and model for this process."""
    _MODEL_OVERRIDE["provider"] = provider
    _MODEL_OVERRIDE["model"] = model


SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "system_prompt.txt")


def load_system_prompt() -> str:
    """Load the system prompt from prompts/system_prompt.txt.  Returns empty string if missing."""
    try:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def save_system_prompt(content: str) -> None:
    """Save updated system prompt text to prompts/system_prompt.txt."""
    os.makedirs(os.path.dirname(SYSTEM_PROMPT_PATH), exist_ok=True)
    with open(SYSTEM_PROMPT_PATH, "w", encoding="utf-8") as f:
        f.write(content)


class LLMTool:
    """
    Main LLM Tool class that provides unified interface
    for text generation across different LLM providers.
    """
    
    def __init__(self, provider: str = None, api_key: str = None, model: str = None):
        """
        Initialize LLM Tool.

        Args:
            provider: 'gemini' or 'openai'
            api_key: API key for the provider
            model: Specific model name to use (overrides default)
        """
        from config import get_llm_config, GOOGLE_API_KEY, OPENAI_API_KEY

        config = get_llm_config()
        provider = provider or config["provider"]
        api_key = api_key or config["api_key"]

        # Apply session-level override set via set_model_override()
        if _MODEL_OVERRIDE["provider"]:
            provider = _MODEL_OVERRIDE["provider"]
            api_key = GOOGLE_API_KEY if provider == "gemini" else OPENAI_API_KEY
        if _MODEL_OVERRIDE["model"]:
            model = _MODEL_OVERRIDE["model"]

        self.provider = provider
        self.llm = self._create_llm(provider, api_key, model)
    
    def _create_llm(self, provider: str, api_key: str, model: str = None) -> BaseLLM:
        """Create appropriate LLM instance"""
        if not api_key:
            raise ValueError(f"API key not provided for {provider}")

        if provider == "gemini":
            return GeminiLLM(api_key, preferred_model=model)
        elif provider == "openai":
            return OpenAILLM(api_key, model=model or "gpt-3.5-turbo")
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text from a prompt, prepending the active system prompt if one is set.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters (e.g. temperature, max_tokens)
            
        Returns:
            Generated text
        """
        system_prompt = load_system_prompt()
        if system_prompt:
            full_prompt = f"[System Instructions]\n{system_prompt}\n\n[User Task]\n{prompt}"
        else:
            full_prompt = prompt
        return self.llm.generate(full_prompt, **kwargs)
    
    def summarize(self, text: str, max_length: int = 200) -> str:
        """
        Summarize given text.
        
        Args:
            text: Text to summarize
            max_length: Target summary length in words
            
        Returns:
            Summarized text
        """
        prompt = f"""Please summarize the following text in approximately {max_length} words.
Keep the key points and maintain clarity.

Text to summarize:
{text}

Summary:"""
        return self.generate_text(prompt, temperature=0.3)
    
    def generate_email(
        self,
        recipient: str,
        subject: str,
        purpose: str,
        tone: str = "professional"
    ) -> Dict[str, str]:
        """
        Generate email content.
        
        Args:
            recipient: Email recipient name/description
            subject: Email subject
            purpose: Purpose of the email
            tone: Tone of the email (professional, friendly, formal)
            
        Returns:
            Dictionary with subject and body
        """
        prompt = f"""Generate a {tone} email with the following details:
- To: {recipient}
- Subject: {subject}
- Purpose: {purpose}

Format the response as:
SUBJECT: [email subject]
BODY:
[email body]

Make it clear, concise, and appropriate for the intended purpose."""

        response = self.generate_text(prompt, temperature=0.7)
        
        # Parse response
        result = {"subject": subject, "body": ""}
        
        if "SUBJECT:" in response:
            parts = response.split("BODY:")
            if len(parts) >= 2:
                result["subject"] = parts[0].replace("SUBJECT:", "").strip()
                result["body"] = parts[1].strip()
        else:
            result["body"] = response
        
        return result
    
    def generate_reply(self, original_email: str, reply_intent: str) -> str:
        """
        Generate a reply to an email.
        
        Args:
            original_email: Original email content
            reply_intent: What the reply should convey
            
        Returns:
            Generated reply
        """
        prompt = f"""Generate a professional reply to the following email.

Original Email:
{original_email}

Reply Intent/Purpose:
{reply_intent}

Generate a clear, professional reply:"""

        return self.generate_text(prompt, temperature=0.7)
    
    def generate_report(
        self,
        topic: str,
        data: str = None,
        sections: List[str] = None
    ) -> str:
        """
        Generate a report.
        
        Args:
            topic: Report topic
            data: Data to include in report
            sections: Sections to include
            
        Returns:
            Generated report
        """
        sections_str = ", ".join(sections) if sections else "Introduction, Main Content, Conclusion"
        
        prompt = f"""Generate a professional report on the following topic:

Topic: {topic}

{"Data/Information to include:" + data if data else ""}

Include these sections: {sections_str}

Format the report with clear headings and structured content.
Make it informative and well-organized."""

        return self.generate_text(prompt, temperature=0.5)
    
    def analyze_data(self, data_summary: str, analysis_type: str = "general") -> str:
        """
        Analyze data and provide insights.
        
        Args:
            data_summary: Summary or description of data
            analysis_type: Type of analysis needed
            
        Returns:
            Analysis result
        """
        prompt = f"""Analyze the following data and provide insights.

Data Summary:
{data_summary}

Analysis Type: {analysis_type}

Provide:
1. Key observations
2. Trends or patterns
3. Recommendations or insights
4. Summary

Analysis:"""

        return self.generate_text(prompt, temperature=0.3)
    
    def classify_intent(self, user_input: str) -> Dict[str, any]:
        """
        Classify user intent for routing to appropriate agent.
        
        Args:
            user_input: User's instruction
            
        Returns:
            Classification result
        """
        prompt = f"""Classify the intent of the following user request and identify the required action.

User Request: "{user_input}"

Classify into one of these categories:
1. email - Send or compose email
2. email_read - Read/search inbox emails
3. browser - Open websites, YouTube, Gmail search, Google Maps directions
4. file_read - Read or view file
5. file_write - Create or save file
6. summarize - Summarize content
7. report - Generate report
8. analyze - Analyze data
9. flight_search - Search flights
10. bus_search - Search bus routes
11. organize_files - Organize or manage files
12. multi_step - Multiple actions needed

Response format (JSON):
{{"intent": "category", "action": "specific action", "entities": {{"key": "extracted value"}}}}

Classification:"""

        response = self.generate_text(prompt, temperature=0.1)
        
        # Try to parse JSON response
        try:
            import json
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        
        return {"intent": "unknown", "action": user_input, "entities": {}}
