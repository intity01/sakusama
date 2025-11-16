"""
Example implementation of Error Handler with retry and fallback logic.

This demonstrates how to handle common errors in the AI VTuber system.
"""

import time
from typing import Optional, Callable, Any
from enum import Enum


class ErrorType(Enum):
    """Types of errors that can occur in the system."""
    STT_FAILED = "stt_failed"
    TTS_FAILED = "tts_failed"
    LLM_TIMEOUT = "llm_timeout"
    LLM_API_ERROR = "llm_api_error"
    ASSET_MISSING = "asset_missing"
    NETWORK_ERROR = "network_error"


class ErrorHandler:
    """
    Central error handler with retry and fallback mechanisms.
    """
    
    def __init__(self, config: dict):
        """
        Initialize the error handler.
        
        Args:
            config: Configuration dictionary with retry and fallback settings
        """
        self.config = config
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        self.backoff_multiplier = config.get("backoff_multiplier", 2.0)
        
    def handle_with_retry(
        self,
        func: Callable,
        error_type: ErrorType,
        fallback: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic and optional fallback.
        
        Args:
            func: The function to execute
            error_type: Type of error being handled
            fallback: Optional fallback function if all retries fail
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Result from func or fallback
        """
        last_error = None
        delay = self.retry_delay
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    print(f"[ErrorHandler] Retry successful on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                last_error = e
                print(f"[ErrorHandler] {error_type.value} failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    print(f"[ErrorHandler] Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= self.backoff_multiplier
        
        # All retries failed
        print(f"[ErrorHandler] All retries failed for {error_type.value}")
        
        if fallback:
            print(f"[ErrorHandler] Using fallback for {error_type.value}")
            try:
                return fallback(*args, **kwargs)
            except Exception as e:
                print(f"[ErrorHandler] Fallback also failed: {e}")
                raise
        
        raise last_error


class STTErrorHandler:
    """Specific error handler for Speech-to-Text."""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        
    def transcribe_with_fallback(self, audio_data: bytes, stt_func: Callable) -> str:
        """
        Transcribe audio with retry and fallback to text input.
        
        Args:
            audio_data: Audio data to transcribe
            stt_func: STT function to use
            
        Returns:
            Transcribed text or empty string if fallback to text mode
        """
        def fallback_to_text(*args, **kwargs):
            print("[STT] Falling back to text input mode")
            return ""  # Empty string signals text input mode
        
        return self.error_handler.handle_with_retry(
            stt_func,
            ErrorType.STT_FAILED,
            fallback=fallback_to_text,
            audio_data
        )


class LLMErrorHandler:
    """Specific error handler for LLM operations."""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.cache = {}
        
    def generate_with_fallback(
        self,
        prompt: str,
        llm_func: Callable,
        fallback_llm_func: Optional[Callable] = None
    ) -> str:
        """
        Generate LLM response with retry and fallback.
        
        Args:
            prompt: Input prompt
            llm_func: Primary LLM function
            fallback_llm_func: Optional fallback LLM (e.g., local model)
            
        Returns:
            Generated response
        """
        # Try primary LLM with retry
        try:
            return self.error_handler.handle_with_retry(
                llm_func,
                ErrorType.LLM_TIMEOUT,
                fallback=None,
                prompt
            )
        except Exception as e:
            print(f"[LLM] Primary LLM failed: {e}")
            
            # Try fallback LLM if available
            if fallback_llm_func:
                print("[LLM] Trying fallback LLM (local model)")
                try:
                    return fallback_llm_func(prompt)
                except Exception as e2:
                    print(f"[LLM] Fallback LLM also failed: {e2}")
            
            # Use cached response if available
            if prompt in self.cache:
                print("[LLM] Using cached response")
                return self.cache[prompt]
            
            # Last resort: generic response
            return "I'm sorry, I'm having trouble thinking right now. Could you try again?"


class AssetErrorHandler:
    """Specific error handler for asset loading."""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.default_assets = {
            "avatar": "default_avatar.vrm",
            "animation": "default_idle.anim"
        }
        
    def load_asset_with_fallback(
        self,
        asset_path: str,
        asset_type: str,
        load_func: Callable
    ) -> Any:
        """
        Load asset with fallback to default.
        
        Args:
            asset_path: Path to asset
            asset_type: Type of asset (e.g., "avatar", "animation")
            load_func: Function to load the asset
            
        Returns:
            Loaded asset
        """
        def fallback_to_default(*args, **kwargs):
            default_path = self.default_assets.get(asset_type)
            if default_path:
                print(f"[Asset] Loading default {asset_type}: {default_path}")
                return load_func(default_path)
            raise FileNotFoundError(f"No default asset for type: {asset_type}")
        
        return self.error_handler.handle_with_retry(
            load_func,
            ErrorType.ASSET_MISSING,
            fallback=fallback_to_default,
            asset_path
        )


# Example usage
if __name__ == "__main__":
    # Initialize error handler
    config = {
        "max_retries": 3,
        "retry_delay": 1.0,
        "backoff_multiplier": 2.0
    }
    error_handler = ErrorHandler(config)
    
    # Example: STT with retry
    stt_handler = STTErrorHandler(error_handler)
    
    def mock_stt(audio_data):
        # Simulate occasional failure
        import random
        if random.random() < 0.5:
            raise Exception("STT service unavailable")
        return "Hello, this is a test"
    
    try:
        result = stt_handler.transcribe_with_fallback(b"audio_data", mock_stt)
        print(f"STT Result: {result}")
    except Exception as e:
        print(f"STT Error: {e}")
