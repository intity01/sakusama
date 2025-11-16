"""
LLM Module with Multiple Provider Support and Fallback

Supports OpenAI API, Ollama (local), and Google Gemini API.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    OpenAI = None
    AsyncOpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ..error import ErrorHandler, ErrorType, get_error_handler
from ..events import Event, EventType, get_event_bus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"


@dataclass
class LLMConfig:
    """Configuration for LLM."""
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4.1-mini"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 500
    system_prompt: str = "You are a friendly VTuber companion."
    
    # Ollama specific
    ollama_base_url: str = "http://localhost:11434"
    
    # Fallback configuration
    fallback_enabled: bool = False
    fallback_provider: Optional[LLMProvider] = None
    fallback_model: Optional[str] = None


class LLMModule:
    """
    LLM Module with error handling and fallback support.
    Supports OpenAI, Ollama (local), and Google Gemini.
    """
    
    def __init__(self, config: LLMConfig, error_handler: Optional[ErrorHandler] = None):
        """
        Initialize the LLM module.
        
        Args:
            config: LLM configuration
            error_handler: Optional error handler (uses global if not provided)
        """
        self.config = config
        self.error_handler = error_handler or get_error_handler()
        self.event_bus = get_event_bus()
        
        # Initialize client based on provider
        self.client = None
        self._initialize_client()
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        if self.config.provider == LLMProvider.OPENAI:
            self._init_openai()
        elif self.config.provider == LLMProvider.OLLAMA:
            self._init_ollama()
        elif self.config.provider == LLMProvider.GEMINI:
            self._init_gemini()
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        if OpenAI is None:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("No OpenAI API key provided. LLM will not work.")
        
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
    
    def _init_ollama(self):
        """Initialize Ollama client (uses OpenAI-compatible API)."""
        if OpenAI is None:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        # Ollama uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            base_url=self.config.ollama_base_url + "/v1",
            api_key="ollama"  # Ollama doesn't need real API key
        )
        logger.info(f"Initialized Ollama client at {self.config.ollama_base_url}")
    
    def _init_gemini(self):
        """Initialize Google Gemini client."""
        if genai is None:
            raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai")
        
        api_key = self.config.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("No Gemini API key provided. LLM will not work.")
            return
        
        genai.configure(api_key=api_key)
        # Gemini models need 'models/' prefix
        model_name = self.config.model if self.config.model.startswith('models/') else f'models/{self.config.model}'
        self.client = genai.GenerativeModel(model_name)
        logger.info(f"Initialized Gemini client with model {model_name}")
    
    async def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            user_message: User's message
            system_prompt: Optional override for system prompt
            include_history: Whether to include conversation history
            
        Returns:
            Dictionary containing response and metadata
        """
        # Use provided system prompt or default
        sys_prompt = system_prompt or self.config.system_prompt
        
        # Generate based on provider
        if self.config.provider == LLMProvider.GEMINI:
            return await self._generate_gemini(user_message, sys_prompt, include_history)
        else:
            return await self._generate_openai_compatible(user_message, sys_prompt, include_history)
    
    async def _generate_openai_compatible(
        self,
        user_message: str,
        system_prompt: str,
        include_history: bool
    ) -> Dict[str, Any]:
        """Generate response using OpenAI-compatible API (OpenAI, Ollama)."""
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if requested
        if include_history and self.conversation_history:
            messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response with error handling
        async def _generate():
            if not self.client:
                raise Exception("LLM client not initialized")
            
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return response
        
        # Fallback function
        async def _fallback():
            logger.warning("Using fallback response (LLM unavailable)")
            return {
                "response": "I'm sorry, I'm having trouble thinking right now. Could you try again?",
                "emotion": "confused",
                "fallback_used": True
            }
        
        try:
            # Try to generate with retry
            response = await self.error_handler.handle_with_retry_async(
                _generate,
                ErrorType.LLM_API_ERROR,
                fallback=None
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            # Simple emotion detection
            emotion = self._detect_emotion(response_text)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Keep only last 10 messages
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            result = {
                "response": response_text,
                "emotion": emotion,
                "model": self.config.model,
                "provider": self.config.provider.value,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                "fallback_used": False
            }
            
            # Publish LLM response event
            await self.event_bus.publish(Event(
                type=EventType.LLM_RESPONSE,
                data=result,
                source="llm_module"
            ))
            
            return result
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            
            # Publish error event
            await self.event_bus.publish(Event(
                type=EventType.LLM_ERROR,
                data={"error": str(e), "message": user_message},
                source="llm_module"
            ))
            
            # Use fallback
            return await _fallback()
    
    async def _generate_gemini(
        self,
        user_message: str,
        system_prompt: str,
        include_history: bool
    ) -> Dict[str, Any]:
        """Generate response using Google Gemini API."""
        async def _generate():
            if not self.client:
                raise Exception("Gemini client not initialized")
            
            # Build prompt with system prompt and history
            full_prompt = f"{system_prompt}\n\n"
            
            if include_history and self.conversation_history:
                for msg in self.conversation_history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    full_prompt += f"{role}: {msg['content']}\n"
            
            full_prompt += f"User: {user_message}\nAssistant:"
            
            # Generate response
            response = await asyncio.to_thread(
                self.client.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens
                )
            )
            
            return response
        
        # Fallback function
        async def _fallback():
            logger.warning("Using fallback response (Gemini unavailable)")
            return {
                "response": "I'm sorry, I'm having trouble thinking right now. Could you try again?",
                "emotion": "confused",
                "fallback_used": True
            }
        
        try:
            # Try to generate with retry
            response = await self.error_handler.handle_with_retry_async(
                _generate,
                ErrorType.LLM_API_ERROR,
                fallback=None
            )
            
            # Extract response text
            response_text = response.text
            
            # Simple emotion detection
            emotion = self._detect_emotion(response_text)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Keep only last 10 messages
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            result = {
                "response": response_text,
                "emotion": emotion,
                "model": self.config.model,
                "provider": "gemini",
                "tokens_used": 0,  # Gemini doesn't provide token count easily
                "fallback_used": False
            }
            
            # Publish LLM response event
            await self.event_bus.publish(Event(
                type=EventType.LLM_RESPONSE,
                data=result,
                source="llm_module"
            ))
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            
            # Publish error event
            await self.event_bus.publish(Event(
                type=EventType.LLM_ERROR,
                data={"error": str(e), "message": user_message},
                source="llm_module"
            ))
            
            # Use fallback
            return await _fallback()
    
    def _detect_emotion(self, text: str) -> str:
        """
        Simple emotion detection based on text content.
        
        Args:
            text: Response text
            
        Returns:
            Detected emotion
        """
        text_lower = text.lower()
        
        # Simple keyword-based detection
        if any(word in text_lower for word in ["!", "great", "awesome", "wonderful", "happy", "excited"]):
            return "happy"
        elif any(word in text_lower for word in ["sorry", "unfortunately", "sad", "disappointed"]):
            return "sad"
        elif any(word in text_lower for word in ["?", "hmm", "not sure", "maybe"]):
            return "confused"
        elif any(word in text_lower for word in ["wow", "amazing", "incredible", "surprising"]):
            return "surprised"
        else:
            return "neutral"
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()


# Example usage
if __name__ == "__main__":
    async def main():
        # Test Ollama
        print("Testing Ollama...")
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.2:3b",
            temperature=0.8,
            system_prompt="You are Luna, a cheerful VTuber!"
        )
        
        llm = LLMModule(config)
        result = await llm.generate_response("Hi! What's your name?")
        print(f"Response: {result['response']}")
        print(f"Emotion: {result['emotion']}")
    
    asyncio.run(main())
