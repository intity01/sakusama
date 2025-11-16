"""
Error Handler with Retry and Fallback Logic

This module provides robust error handling for the AI VTuber system.
"""

import time
import asyncio
from typing import Optional, Callable, Any, TypeVar, Dict
from enum import Enum
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorType(Enum):
    """Types of errors that can occur in the system."""
    STT_FAILED = "stt_failed"
    TTS_FAILED = "tts_failed"
    LLM_TIMEOUT = "llm_timeout"
    LLM_API_ERROR = "llm_api_error"
    LLM_RATE_LIMIT = "llm_rate_limit"
    MEMORY_ERROR = "memory_error"
    ASSET_MISSING = "asset_missing"
    NETWORK_ERROR = "network_error"
    ENCRYPTION_ERROR = "encryption_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorConfig:
    """Configuration for error handling."""
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_multiplier: float = 2.0
    timeout_seconds: float = 30.0


class ErrorHandler:
    """
    Central error handler with retry and fallback mechanisms.
    """
    
    def __init__(self, config: Optional[ErrorConfig] = None):
        """
        Initialize the error handler.
        
        Args:
            config: Error handling configuration
        """
        self.config = config or ErrorConfig()
        self.error_counts: Dict[ErrorType, int] = {}
        
    async def handle_with_retry_async(
        self,
        func: Callable,
        error_type: ErrorType,
        fallback: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute an async function with retry logic and optional fallback.
        
        Args:
            func: The async function to execute
            error_type: Type of error being handled
            fallback: Optional fallback function if all retries fail
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Result from func or fallback
        """
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout_seconds
                )
                
                if attempt > 0:
                    logger.info(f"✓ Retry successful on attempt {attempt + 1} for {error_type.value}")
                
                # Reset error count on success
                if error_type in self.error_counts:
                    self.error_counts[error_type] = 0
                    
                return result
                
            except asyncio.TimeoutError as e:
                last_error = e
                logger.warning(f"⏱ Timeout on attempt {attempt + 1}/{self.config.max_retries} for {error_type.value}")
                
            except Exception as e:
                last_error = e
                logger.warning(f"✗ {error_type.value} failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                
            # Increment error count
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            
            # Wait before retry (except on last attempt)
            if attempt < self.config.max_retries - 1:
                logger.info(f"⏳ Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
                delay *= self.config.backoff_multiplier
        
        # All retries failed
        logger.error(f"✗ All {self.config.max_retries} retries failed for {error_type.value}")
        
        # Try fallback if available
        if fallback:
            logger.info(f"🔄 Using fallback for {error_type.value}")
            try:
                if asyncio.iscoroutinefunction(fallback):
                    return await fallback(*args, **kwargs)
                else:
                    return fallback(*args, **kwargs)
            except Exception as e:
                logger.error(f"✗ Fallback also failed: {e}")
                raise
        
        # No fallback available, raise the last error
        raise last_error
    
    def handle_with_retry_sync(
        self,
        func: Callable,
        error_type: ErrorType,
        fallback: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a sync function with retry logic and optional fallback.
        
        Args:
            func: The function to execute
            error_type: Type of error being handled
            fallback: Optional fallback function if all retries fail
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Result from func or fallback
        """
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✓ Retry successful on attempt {attempt + 1} for {error_type.value}")
                
                # Reset error count on success
                if error_type in self.error_counts:
                    self.error_counts[error_type] = 0
                    
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"✗ {error_type.value} failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                
            # Increment error count
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            
            # Wait before retry (except on last attempt)
            if attempt < self.config.max_retries - 1:
                logger.info(f"⏳ Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
                delay *= self.config.backoff_multiplier
        
        # All retries failed
        logger.error(f"✗ All {self.config.max_retries} retries failed for {error_type.value}")
        
        # Try fallback if available
        if fallback:
            logger.info(f"🔄 Using fallback for {error_type.value}")
            try:
                return fallback(*args, **kwargs)
            except Exception as e:
                logger.error(f"✗ Fallback also failed: {e}")
                raise
        
        # No fallback available, raise the last error
        raise last_error
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        return {error_type.value: count for error_type, count in self.error_counts.items()}
    
    def reset_stats(self):
        """Reset error statistics."""
        self.error_counts.clear()


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


# Example usage
if __name__ == "__main__":
    async def main():
        # Create error handler
        config = ErrorConfig(max_retries=3, retry_delay=0.5, backoff_multiplier=2.0)
        handler = ErrorHandler(config)
        
        # Example 1: Function that fails then succeeds
        attempt_count = 0
        async def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("Temporary failure")
            return "Success!"
        
        print("Test 1: Flaky function (should succeed on retry)")
        result = await handler.handle_with_retry_async(
            flaky_function,
            ErrorType.LLM_API_ERROR
        )
        print(f"Result: {result}\n")
        
        # Example 2: Function that always fails, with fallback
        async def always_fails():
            raise Exception("Always fails")
        
        async def fallback_function():
            return "Fallback result"
        
        print("Test 2: Always fails (should use fallback)")
        result = await handler.handle_with_retry_async(
            always_fails,
            ErrorType.LLM_TIMEOUT,
            fallback=fallback_function
        )
        print(f"Result: {result}\n")
        
        # Print error stats
        print("Error Statistics:")
        for error_type, count in handler.get_error_stats().items():
            print(f"  {error_type}: {count} failures")
    
    asyncio.run(main())
