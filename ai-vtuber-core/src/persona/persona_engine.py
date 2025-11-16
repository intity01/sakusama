"""
Persona Engine for AI VTuber

Manages different AI personalities and behaviors.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import logging

from ..events import Event, EventType, get_event_bus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PersonaConfig:
    """Configuration for a persona."""
    name: str
    version: str
    description: str
    author: str = "Unknown"
    tags: List[str] = None
    
    # LLM Configuration
    system_prompt: str = "You are a friendly AI assistant."
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 200
    
    # Behavior
    use_emojis: bool = False
    emoji_frequency: float = 0.0
    casual_language: bool = False
    
    # Greetings and farewells
    greetings: List[str] = None
    farewells: List[str] = None
    
    # Emotion mapping
    emotion_map: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.tags is None:
            self.tags = []
        if self.greetings is None:
            self.greetings = ["Hello!", "Hi there!"]
        if self.farewells is None:
            self.farewells = ["Goodbye!", "See you later!"]
        if self.emotion_map is None:
            self.emotion_map = {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonaConfig':
        """Create PersonaConfig from dictionary."""
        # Extract LLM config
        llm_config = data.get('llm_config', {})
        behavior = data.get('behavior', {})
        
        return cls(
            name=data.get('name', 'Unknown'),
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            author=data.get('author', 'Unknown'),
            tags=data.get('tags', []),
            system_prompt=llm_config.get('system_prompt', ''),
            temperature=llm_config.get('temperature', 0.7),
            top_p=llm_config.get('top_p', 0.9),
            max_tokens=llm_config.get('max_tokens', 200),
            use_emojis=behavior.get('use_emojis', False),
            emoji_frequency=behavior.get('emoji_frequency', 0.0),
            casual_language=behavior.get('casual_language', False),
            greetings=behavior.get('greetings', ["Hello!"]),
            farewells=behavior.get('farewells', ["Goodbye!"]),
            emotion_map=data.get('emotion_map', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'tags': self.tags,
            'llm_config': {
                'system_prompt': self.system_prompt,
                'temperature': self.temperature,
                'top_p': self.top_p,
                'max_tokens': self.max_tokens
            },
            'behavior': {
                'use_emojis': self.use_emojis,
                'emoji_frequency': self.emoji_frequency,
                'casual_language': self.casual_language,
                'greetings': self.greetings,
                'farewells': self.farewells
            },
            'emotion_map': self.emotion_map
        }


class PersonaEngine:
    """
    Engine for managing and switching between different personas.
    """
    
    def __init__(self, persona_directory: str = "./personas"):
        """
        Initialize the persona engine.
        
        Args:
            persona_directory: Directory containing persona files
        """
        self.persona_directory = Path(persona_directory)
        self.personas: Dict[str, PersonaConfig] = {}
        self.current_persona: Optional[PersonaConfig] = None
        self.event_bus = get_event_bus()
        
        # Create directory if it doesn't exist
        self.persona_directory.mkdir(parents=True, exist_ok=True)
        
        # Load personas
        self._load_personas()
    
    def _load_personas(self):
        """Load all personas from directory."""
        if not self.persona_directory.exists():
            logger.warning(f"Persona directory not found: {self.persona_directory}")
            return
        
        # Load YAML and JSON files
        for file_path in self.persona_directory.glob("*.yaml"):
            self._load_persona_file(file_path)
        
        for file_path in self.persona_directory.glob("*.yml"):
            self._load_persona_file(file_path)
        
        for file_path in self.persona_directory.glob("*.json"):
            self._load_persona_file(file_path)
        
        logger.info(f"Loaded {len(self.personas)} personas")
    
    def _load_persona_file(self, file_path: Path):
        """Load a single persona file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            persona = PersonaConfig.from_dict(data)
            self.personas[persona.name.lower()] = persona
            logger.info(f"Loaded persona: {persona.name}")
            
        except Exception as e:
            logger.error(f"Failed to load persona from {file_path}: {e}")
    
    def get_persona(self, name: str) -> Optional[PersonaConfig]:
        """
        Get a persona by name.
        
        Args:
            name: Persona name
            
        Returns:
            PersonaConfig or None if not found
        """
        return self.personas.get(name.lower())
    
    def list_personas(self) -> List[str]:
        """Get list of available persona names."""
        return list(self.personas.keys())
    
    async def load_persona(self, name: str) -> bool:
        """
        Load and activate a persona.
        
        Args:
            name: Persona name
            
        Returns:
            True if successful, False otherwise
        """
        persona = self.get_persona(name)
        if not persona:
            logger.error(f"Persona not found: {name}")
            return False
        
        self.current_persona = persona
        logger.info(f"Loaded persona: {persona.name}")
        
        # Publish persona change event
        await self.event_bus.publish(Event(
            type=EventType.PERSONA_LOADED,
            data={
                'persona_name': persona.name,
                'system_prompt': persona.system_prompt,
                'temperature': persona.temperature,
                'behavior': {
                    'use_emojis': persona.use_emojis,
                    'casual_language': persona.casual_language
                }
            },
            source="persona_engine"
        ))
        
        return True
    
    def get_current_persona(self) -> Optional[PersonaConfig]:
        """Get the currently active persona."""
        return self.current_persona
    
    def get_greeting(self) -> str:
        """Get a random greeting from current persona."""
        if not self.current_persona or not self.current_persona.greetings:
            return "Hello!"
        
        import random
        return random.choice(self.current_persona.greetings)
    
    def get_farewell(self) -> str:
        """Get a random farewell from current persona."""
        if not self.current_persona or not self.current_persona.farewells:
            return "Goodbye!"
        
        import random
        return random.choice(self.current_persona.farewells)
    
    def map_emotion(self, emotion: str) -> str:
        """
        Map an emotion to persona-specific expression.
        
        Args:
            emotion: Original emotion
            
        Returns:
            Mapped emotion or original if no mapping exists
        """
        if not self.current_persona or not self.current_persona.emotion_map:
            return emotion
        
        return self.current_persona.emotion_map.get(emotion, emotion)
    
    def create_default_personas(self):
        """Create default personas if none exist."""
        # Luna - Playful Friend
        luna = PersonaConfig(
            name="Luna",
            version="1.0.0",
            description="A cheerful and playful friend",
            author="AI VTuber Team",
            tags=["playful", "cheerful", "friendly"],
            system_prompt="You are Luna, a cheerful and playful VTuber. You love to use emojis and make jokes. Be friendly and supportive!",
            temperature=0.85,
            use_emojis=True,
            emoji_frequency=0.7,
            casual_language=True,
            greetings=["Hey there! 👋", "Hiii! 😊", "What's up? ✨"],
            farewells=["See ya! 👋", "Bye bye! 💕", "Catch you later! 😄"],
            emotion_map={
                "happy": "excited_jump",
                "sad": "pout",
                "excited": "happy_bounce"
            }
        )
        
        # Sage - Wise Mentor
        sage = PersonaConfig(
            name="Sage",
            version="1.0.0",
            description="A calm and knowledgeable mentor",
            author="AI VTuber Team",
            tags=["wise", "calm", "mentor"],
            system_prompt="You are Sage, a wise and knowledgeable mentor. Speak calmly and provide thoughtful guidance. Be patient and educational.",
            temperature=0.6,
            use_emojis=False,
            emoji_frequency=0.1,
            casual_language=False,
            greetings=["Greetings.", "Welcome.", "Good day."],
            farewells=["Farewell.", "Until we meet again.", "Take care."],
            emotion_map={
                "happy": "gentle_smile",
                "sad": "concerned_nod",
                "excited": "approving_nod"
            }
        )
        
        # Save personas
        self._save_persona(luna)
        self._save_persona(sage)
        
        logger.info("Created default personas: Luna, Sage")
    
    def _save_persona(self, persona: PersonaConfig):
        """Save a persona to file."""
        filename = f"{persona.name.lower()}.yaml"
        filepath = self.persona_directory / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(persona.to_dict(), f, default_flow_style=False, allow_unicode=True)
        
        # Add to loaded personas
        self.personas[persona.name.lower()] = persona


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create persona engine
        engine = PersonaEngine("./test_personas")
        
        # Create default personas if none exist
        if not engine.list_personas():
            print("Creating default personas...")
            engine.create_default_personas()
        
        # List available personas
        print("\nAvailable personas:")
        for name in engine.list_personas():
            persona = engine.get_persona(name)
            print(f"  - {persona.name}: {persona.description}")
        
        # Load Luna persona
        print("\nLoading Luna persona...")
        await engine.load_persona("luna")
        
        current = engine.get_current_persona()
        print(f"Current persona: {current.name}")
        print(f"System prompt: {current.system_prompt[:100]}...")
        print(f"Temperature: {current.temperature}")
        print(f"Greeting: {engine.get_greeting()}")
        print(f"Farewell: {engine.get_farewell()}")
        
        # Switch to Sage
        print("\nLoading Sage persona...")
        await engine.load_persona("sage")
        
        current = engine.get_current_persona()
        print(f"Current persona: {current.name}")
        print(f"Greeting: {engine.get_greeting()}")
        print(f"Farewell: {engine.get_farewell()}")
    
    asyncio.run(main())
