"""
Text-to-Speech Module

Converts text to speech using Edge TTS (free, no API key needed).
Saves audio files without requiring audio playback libraries.
"""

import asyncio
import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import edge-tts
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge-tts not installed. Install with: pip install edge-tts")


class TTSEngine(Enum):
    """Available TTS engines."""
    EDGE = "edge"  # Microsoft Edge TTS (free)
    SYSTEM = "system"  # System default TTS


@dataclass
class TTSConfig:
    """Configuration for TTS."""
    engine: TTSEngine = TTSEngine.EDGE
    voice: str = "th-TH-PremwadeeNeural"  # Thai female voice
    rate: str = "+0%"  # Speech rate (-50% to +50%)
    volume: str = "+0%"  # Volume (-50% to +50%)
    pitch: str = "+12Hz"  # Pitch adjustment
    output_dir: str = "./data/tts_cache"
    auto_play: bool = True
    cache_enabled: bool = True


class TTSModule:
    """Text-to-Speech module."""
    
    def __init__(self, config: TTSConfig):
        """Initialize TTS module.
        
        Args:
            config: TTS configuration
        """
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"TTS module initialized with engine: {config.engine.value}")
    
    async def speak(self, text: str, output_file: Optional[str] = None) -> Optional[str]:
        """Convert text to speech and optionally play it.
        
        Args:
            text: Text to convert to speech
            output_file: Optional output file path. If None, uses cache.
            
        Returns:
            Path to the generated audio file, or None if failed
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return None
        
        # Generate output filename
        if output_file is None:
            # Use hash of text as filename for caching
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
            output_file = str(self.output_dir / f"tts_{text_hash}.mp3")
        
        # Check cache
        if self.config.cache_enabled and os.path.exists(output_file):
            logger.info(f"Using cached TTS: {output_file}")
            if self.config.auto_play:
                await self._play_audio(output_file)
            return output_file
        
        # Generate speech
        try:
            if self.config.engine == TTSEngine.EDGE:
                await self._generate_edge_tts(text, output_file)
            else:
                logger.error(f"Unsupported TTS engine: {self.config.engine}")
                return None
            
            logger.info(f"Generated TTS: {output_file}")
            
            # Play audio if auto_play is enabled
            if self.config.auto_play:
                await self._play_audio(output_file)
            
            return output_file
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
    
    async def _generate_edge_tts(self, text: str, output_file: str):
        """Generate speech using Edge TTS.
        
        Args:
            text: Text to convert
            output_file: Output file path
        """
        if not EDGE_TTS_AVAILABLE:
            raise ImportError("edge-tts is not installed")
        
        # Create communicate object
        communicate = edge_tts.Communicate(
            text,
            self.config.voice,
            rate=self.config.rate,
            volume=self.config.volume,
            pitch=self.config.pitch
        )
        
        # Save to file
        await communicate.save(output_file)
    
    async def _play_audio(self, audio_file: str):
        """Play audio file using system audio player.
        
        Args:
            audio_file: Path to audio file
        """
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Use PowerShell to play audio without opening a window
                ps_command = f'(New-Object Media.SoundPlayer "{audio_file}").PlaySync()'
                # Run in background thread to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        ["powershell", "-Command", ps_command],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                )
            elif system == "Darwin":  # macOS
                await asyncio.create_subprocess_exec("afplay", audio_file)
            else:  # Linux
                await asyncio.create_subprocess_exec("aplay", audio_file)
                
            logger.info(f"Played audio: {audio_file}")
                
        except Exception as e:
            logger.warning(f"Could not play audio: {e}")
            logger.info(f"Audio file saved at: {audio_file}")
    
    async def list_voices(self) -> list:
        """List available voices for current engine.
        
        Returns:
            List of available voice names
        """
        if self.config.engine == TTSEngine.EDGE and EDGE_TTS_AVAILABLE:
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
                logger.error(f"Failed to list voices: {e}")
                return []
        return []
    
    async def get_thai_voices(self) -> list:
        """Get available Thai voices.
        
        Returns:
            List of Thai voice names
        """
        voices = await self.list_voices()
        return [v for v in voices if v["locale"].startswith("th-")]
    
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


# Recommended Thai voices
THAI_VOICES = {
    "premwadee": "th-TH-PremwadeeNeural",  # Female, friendly
    "niwat": "th-TH-NiwatNeural",  # Male, clear
    "achara": "th-TH-AcharaNeural",  # Female, professional
}


def get_recommended_voice(persona_name: str = "saku") -> str:
    """Get recommended voice for a persona.
    
    Args:
        persona_name: Name of the persona
        
    Returns:
        Voice name for Edge TTS
    """
    # Map persona to voice
    voice_map = {
        "saku": THAI_VOICES["premwadee"],  # Friendly female
        "luna": THAI_VOICES["premwadee"],  # Friendly female
        "sage": THAI_VOICES["achara"],  # Professional female
    }
    
    return voice_map.get(persona_name.lower(), THAI_VOICES["premwadee"])
