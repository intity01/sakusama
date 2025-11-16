"""
Text-to-Speech Module

Supports two TTS engines:
1. py3-tts (pyttsx3) - Uses system TTS, works offline, plays audio directly
2. edge-tts - Microsoft Edge TTS, high quality, requires internet
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import hashlib

logger = logging.getLogger(__name__)

# Try to import py3-tts (pyttsx3 alternative)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("py3-tts not installed. Install with: pip install py3-tts")

# Try to import edge-tts
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge-tts not installed. Install with: pip install edge-tts")


class TTSEngine(Enum):
    """Available TTS engines."""
    PYTTSX3 = "pyttsx3"  # System TTS (Windows SAPI5, macOS nsss, Linux espeak)
    EDGE = "edge"  # Microsoft Edge TTS


@dataclass
class TTSConfig:
    """Configuration for TTS."""
    engine: TTSEngine = TTSEngine.PYTTSX3  # Default to system TTS
    
    # pyttsx3 settings
    rate: int = 150  # Speech rate (words per minute)
    volume: float = 0.9  # Volume (0.0 to 1.0)
    voice_index: int = 0  # Voice index (0 = default)
    
    # edge-tts settings
    edge_voice: str = "th-TH-PremwadeeNeural"  # Thai female voice
    edge_rate: str = "+0%"  # Speech rate for edge-tts
    edge_volume: str = "+0%"  # Volume for edge-tts
    edge_pitch: str = "+0Hz"  # Pitch adjustment for edge-tts
    
    # Common settings
    output_dir: str = "./data/tts_cache"
    cache_enabled: bool = True


class TTSModule:
    """Text-to-Speech module with multiple engine support."""
    
    def __init__(self, config: TTSConfig):
        """Initialize TTS module.
        
        Args:
            config: TTS configuration
        """
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize pyttsx3 engine if available
        self.pyttsx3_engine = None
        if config.engine == TTSEngine.PYTTSX3 and PYTTSX3_AVAILABLE:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self.pyttsx3_engine.setProperty('rate', config.rate)
                self.pyttsx3_engine.setProperty('volume', config.volume)
                
                # Set voice if available
                voices = self.pyttsx3_engine.getProperty('voices')
                if voices and len(voices) > config.voice_index:
                    self.pyttsx3_engine.setProperty('voice', voices[config.voice_index].id)
                
                logger.info(f"pyttsx3 TTS initialized (rate={config.rate}, volume={config.volume})")
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3: {e}")
                self.pyttsx3_engine = None
        
        logger.info(f"TTS module initialized with engine: {config.engine.value}")
    
    async def speak(self, text: str, output_file: Optional[str] = None) -> Optional[str]:
        """Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            output_file: Optional output file path (only for edge-tts)
            
        Returns:
            Path to the generated audio file (edge-tts only), or None
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return None
        
        try:
            if self.config.engine == TTSEngine.PYTTSX3:
                return await self._speak_pyttsx3(text)
            elif self.config.engine == TTSEngine.EDGE:
                return await self._speak_edge(text, output_file)
            else:
                logger.error(f"Unsupported TTS engine: {self.config.engine}")
                return None
                
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None
    
    async def _speak_pyttsx3(self, text: str) -> None:
        """Speak using pyttsx3 (system TTS).
        
        Args:
            text: Text to speak
        """
        if not self.pyttsx3_engine:
            raise RuntimeError("pyttsx3 engine not initialized")
        
        # Run pyttsx3 in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._pyttsx3_speak_sync, text)
        
        logger.info(f"Spoke with pyttsx3: {text[:50]}...")
        return None
    
    def _pyttsx3_speak_sync(self, text: str):
        """Synchronous pyttsx3 speak (for executor).
        
        Args:
            text: Text to speak
        """
        self.pyttsx3_engine.say(text)
        self.pyttsx3_engine.runAndWait()
    
    async def _speak_edge(self, text: str, output_file: Optional[str] = None) -> Optional[str]:
        """Speak using Edge TTS.
        
        Args:
            text: Text to speak
            output_file: Optional output file path
            
        Returns:
            Path to generated audio file
        """
        if not EDGE_TTS_AVAILABLE:
            raise ImportError("edge-tts is not installed")
        
        # Generate output filename
        if output_file is None:
            text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
            output_file = str(self.output_dir / f"tts_{text_hash}.mp3")
        
        # Check cache
        if self.config.cache_enabled and os.path.exists(output_file):
            logger.info(f"Using cached TTS: {output_file}")
            return output_file
        
        # Generate speech
        communicate = edge_tts.Communicate(
            text,
            self.config.edge_voice,
            rate=self.config.edge_rate,
            volume=self.config.edge_volume,
            pitch=self.config.edge_pitch
        )
        
        await communicate.save(output_file)
        logger.info(f"Generated TTS with edge-tts: {output_file}")
        
        return output_file
    
    def list_pyttsx3_voices(self) -> list:
        """List available pyttsx3 voices.
        
        Returns:
            List of voice information dicts
        """
        if not self.pyttsx3_engine:
            return []
        
        try:
            voices = self.pyttsx3_engine.getProperty('voices')
            return [
                {
                    "id": v.id,
                    "name": v.name,
                    "languages": v.languages,
                    "gender": getattr(v, 'gender', 'unknown')
                }
                for v in voices
            ]
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []
    
    async def list_edge_voices(self) -> list:
        """List available Edge TTS voices.
        
        Returns:
            List of voice information dicts
        """
        if not EDGE_TTS_AVAILABLE:
            return []
        
        try:
            voices = await edge_tts.list_voices()
            return [
                {
                    "name": v["ShortName"],
                    "gender": v["Gender"],
                    "locale": v["Locale"]
                }
                for v in voices
            ]
        except Exception as e:
            logger.error(f"Failed to list Edge voices: {e}")
            return []
    
    def clear_cache(self):
        """Clear TTS cache directory."""
        try:
            import shutil
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                self.output_dir.mkdir(parents=True, exist_ok=True)
                logger.info("TTS cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")


# Recommended voices
RECOMMENDED_VOICES = {
    "pyttsx3": {
        "default": 0,  # Use system default
    },
    "edge": {
        "saku": "th-TH-PremwadeeNeural",  # Thai female, friendly
        "luna": "th-TH-PremwadeeNeural",  # Thai female, friendly
        "sage": "th-TH-AcharaNeural",  # Thai female, professional
    }
}


def get_recommended_voice(engine: str, persona_name: str = "saku") -> str:
    """Get recommended voice for a persona.
    
    Args:
        engine: TTS engine name ("pyttsx3" or "edge")
        persona_name: Name of the persona
        
    Returns:
        Voice identifier
    """
    voices = RECOMMENDED_VOICES.get(engine, {})
    return voices.get(persona_name.lower(), voices.get("default", 0))
