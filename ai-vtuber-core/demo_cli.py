#!/usr/bin/env python3
"""
AI VTuber CLI Demo

A command-line demo of the AI VTuber Core system.
Supports OpenAI, Ollama (local), and Google Gemini.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.events import EventBus, Event, EventType
from src.error import ErrorHandler, ErrorConfig
from src.llm import LLMModule, LLMConfig, LLMProvider
from src.memory import MemorySystem, MemoryConfig
from src.persona import PersonaEngine, PersonaConfig
from src.tts import TTSModule, TTSConfig, TTSEngine, get_recommended_voice


class AIVTuberCLI:
    """CLI interface for AI VTuber."""
    
    def __init__(self):
        """Initialize the CLI application."""
        print("🎭 AI VTuber Core - CLI Demo")
        print("=" * 50)
        
        # Load config
        self.config = self.load_config()
        
        # Initialize components
        self.event_bus = EventBus()
        self.error_handler = ErrorHandler(ErrorConfig(max_retries=2))
        
        # Initialize memory
        memory_config = MemoryConfig(
            storage_path=self.config.get("memory", {}).get("path", "./data/memory"),
            max_entries=self.config.get("memory", {}).get("max_context_length", 100),
            encryption_enabled=self.config.get("memory", {}).get("encryption", {}).get("enabled", True)
        )
        self.memory = MemorySystem(memory_config, self.error_handler)
        
        # Initialize persona engine
        persona_dir = self.config.get("persona", {}).get("persona_directory", "./personas")
        self.persona_engine = PersonaEngine(persona_dir)
        
        # Create default personas if none exist
        if not self.persona_engine.list_personas():
            print("\n📝 Creating default personas...")
            self.persona_engine.create_default_personas()
        
        # Initialize TTS
        tts_settings = self.config.get("tts", {})
        engine_str = tts_settings.get("engine", "pyttsx3")
        engine = TTSEngine.PYTTSX3 if engine_str == "pyttsx3" else TTSEngine.EDGE
        
        tts_config = TTSConfig(
            engine=engine,
            rate=tts_settings.get("rate", 150),
            volume=tts_settings.get("volume", 0.9),
            voice_index=tts_settings.get("voice_index", 0),
            edge_voice=tts_settings.get("edge_voice", "th-TH-PremwadeeNeural"),
            cache_enabled=tts_settings.get("cache_enabled", True)
        )
        self.tts = TTSModule(tts_config)
        self.tts_enabled = self.config.get("tts", {}).get("enabled", True)
        
        # Initialize LLM (will be configured after provider and persona selection)
        self.llm = None
        self.llm_provider = None
        
        # Subscribe to events
        self.event_bus.subscribe(EventType.LLM_RESPONSE, self._on_llm_response)
        self.event_bus.subscribe(EventType.LLM_ERROR, self._on_llm_error)
        
        self.running = False
    
    def load_config(self):
        """Load configuration from config.json."""
        config_path = Path(__file__).parent / "config" / "config.json"
        
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load config: {e}")
                return {}
        else:
            print(f"⚠️  Config file not found: {config_path}")
            return {}
    
    def get_api_key(self, provider):
        """Get API key from config or environment."""
        # Try config first
        models_config = self.config.get("llm", {}).get("models", {})
        provider_config = models_config.get(provider, {})
        api_key = provider_config.get("api_key", "")
        
        # If empty, try environment variables
        if not api_key or api_key == "":
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY", "")
            elif provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
            elif provider == "ollama":
                api_key = "ollama"  # Ollama doesn't need real key
        
        return api_key if api_key else None
    
    def _on_llm_response(self, event: Event):
        """Handle LLM response event."""
        data = event.data
        emotion = data.get('emotion', 'neutral')
        response = data.get('response', '')
        provider = data.get('provider', 'unknown')
        
        # Map emotion through persona
        if self.persona_engine.current_persona:
            emotion = self.persona_engine.map_emotion(emotion)
        
        print(f"\n🤖 AI ({emotion}) [{provider}]: {response}")
        
        # Show token usage if available
        if data.get('tokens_used'):
            print(f"   💭 Tokens: {data['tokens_used']}")
        
        # Speak response using TTS
        if self.tts_enabled and response:
            asyncio.create_task(self._speak_response(response))
    
    def _on_llm_error(self, event: Event):
        """Handle LLM error event."""
        error = event.data.get('error', 'Unknown error')
        print(f"\n❌ Error: {error}")
    
    async def select_llm_provider(self):
        """Let user select LLM provider."""
        # Check default provider from config
        default_provider = self.config.get("llm", {}).get("provider", "ollama")
        
        print("\n🤖 Select LLM Provider:")
        print("  1. OpenAI (GPT-4, requires API key)")
        print("  2. Ollama (Local, FREE - requires Ollama installed)")
        print("  3. Google Gemini (Cloud, FREE - requires API key)")
        print(f"\n  Default: {default_provider}")
        
        while True:
            try:
                choice = input("\nSelect provider (1-3) or press Enter for default: ").strip()
                
                # Use default if empty
                if choice == "":
                    if default_provider == "openai":
                        choice = "1"
                    elif default_provider == "ollama":
                        choice = "2"
                    elif default_provider == "gemini":
                        choice = "3"
                
                if choice == "1":
                    api_key = self.get_api_key("openai")
                    if not api_key:
                        print("\n⚠️  Warning: OPENAI_API_KEY not set in config or environment!")
                        print("   Edit config/config.json or set environment variable")
                        confirm = input("   Continue anyway? (y/n): ").strip().lower()
                        if confirm != 'y':
                            continue
                    
                    self.llm_provider = LLMProvider.OPENAI
                    print("\n✅ Selected: OpenAI")
                    break
                    
                elif choice == "2":
                    print("\n⚠️  Make sure Ollama is running!")
                    print("   Install: https://ollama.com/download")
                    print("   Run: ollama pull llama3.2:3b")
                    confirm = input("   Is Ollama running? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                    
                    self.llm_provider = LLMProvider.OLLAMA
                    print("\n✅ Selected: Ollama (Local)")
                    break
                    
                elif choice == "3":
                    api_key = self.get_api_key("gemini")
                    if not api_key:
                        print("\n⚠️  Warning: GEMINI_API_KEY not set in config or environment!")
                        print("   Get free API key: https://ai.google.dev")
                        print("   Edit config/config.json or set environment variable")
                        confirm = input("   Continue anyway? (y/n): ").strip().lower()
                        if confirm != 'y':
                            continue
                    
                    self.llm_provider = LLMProvider.GEMINI
                    print("\n✅ Selected: Google Gemini (FREE)")
                    break
                    
                else:
                    print("Invalid choice. Try again.")
                    
            except (ValueError, KeyboardInterrupt):
                print("\nCancelled.")
                return False
        
        return True
    
    async def select_persona(self):
        """Let user select a persona."""
        # Check default persona from config
        default_persona = self.config.get("persona", {}).get("default_persona", "")
        
        print("\n📋 Available Personas:")
        personas = self.persona_engine.list_personas()
        
        for i, name in enumerate(personas, 1):
            persona = self.persona_engine.get_persona(name)
            default_mark = " (default)" if name == default_persona else ""
            print(f"  {i}. {persona.name}{default_mark} - {persona.description}")
        
        while True:
            try:
                choice = input(f"\nSelect persona (1-{len(personas)}) or press Enter for default: ").strip()
                
                # Use default if empty
                if choice == "" and default_persona:
                    try:
                        idx = personas.index(default_persona)
                    except ValueError:
                        idx = 0
                else:
                    idx = int(choice) - 1
                
                if 0 <= idx < len(personas):
                    persona_name = personas[idx]
                    await self.persona_engine.load_persona(persona_name)
                    
                    # Configure LLM with persona settings and selected provider
                    current_persona = self.persona_engine.get_current_persona()
                    
                    # Get model from config
                    models_config = self.config.get("llm", {}).get("models", {})
                    
                    if self.llm_provider == LLMProvider.OPENAI:
                        provider_key = "openai"
                        model = models_config.get(provider_key, {}).get("model", "gpt-4.1-mini")
                    elif self.llm_provider == LLMProvider.OLLAMA:
                        provider_key = "ollama"
                        model = models_config.get(provider_key, {}).get("model", "llama3.2:3b")
                    elif self.llm_provider == LLMProvider.GEMINI:
                        provider_key = "gemini"
                        model = models_config.get(provider_key, {}).get("model", "gemini-1.5-flash-latest")
                    
                    # Get API key
                    api_key = self.get_api_key(provider_key)
                    
                    # Get base URL for Ollama
                    base_url = models_config.get(provider_key, {}).get("base_url", "http://localhost:11434")
                    
                    llm_config = LLMConfig(
                        provider=self.llm_provider,
                        model=model,
                        api_key=api_key,
                        temperature=current_persona.temperature,
                        max_tokens=current_persona.max_tokens,
                        system_prompt=current_persona.system_prompt,
                        ollama_base_url=base_url
                    )
                    
                    self.llm = LLMModule(llm_config, self.error_handler)
                    
                    print(f"\n✅ Loaded persona: {current_persona.name}")
                    print(f"   {current_persona.description}")
                    print(f"   Using: {self.llm_provider.value} - {model}")
                    break
                else:
                    print("Invalid choice. Try again.")
            except (ValueError, IndexError):
                print("Invalid input. Try again.")
    
    async def _speak_response(self, text: str):
        """Speak response using TTS.
        
        Args:
            text: Text to speak
        """
        try:
            print("   🔊 Speaking...")
            await self.tts.speak(text)
        except Exception as e:
            print(f"   ⚠️  TTS error: {e}")
    
    async def chat_loop(self):
        """Main chat loop."""
        print("\n💬 Chat started!")
        tts_status = "ON" if self.tts_enabled else "OFF"
        print(f"   Commands: 'quit', 'persona', 'provider', 'history', 'clear', 'tts' (TTS: {tts_status})")
        print("-" * 50)
        
        # Show greeting
        greeting = self.persona_engine.get_greeting()
        print(f"\n🤖 AI: {greeting}")
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == 'quit':
                    farewell = self.persona_engine.get_farewell()
                    print(f"\n🤖 AI: {farewell}")
                    break
                
                if user_input.lower() == 'provider':
                    if await self.select_llm_provider():
                        await self.select_persona()
                        greeting = self.persona_engine.get_greeting()
                        print(f"\n🤖 AI: {greeting}")
                    continue
                
                if user_input.lower() == 'persona':
                    await self.select_persona()
                    greeting = self.persona_engine.get_greeting()
                    print(f"\n🤖 AI: {greeting}")
                    continue
                
                if user_input.lower() == 'history':
                    print("\n📜 Conversation History:")
                    for entry in self.memory.get_recent_memories(10):
                        print(f"   [{entry.role}] {entry.content[:60]}...")
                    continue
                
                if user_input.lower() == 'clear':
                    self.memory.clear_memories()
                    self.llm.clear_history()
                    print("\n🗑️  Memory cleared!")
                    continue
                
                if user_input.lower() == 'tts':
                    self.tts_enabled = not self.tts_enabled
                    status = "enabled" if self.tts_enabled else "disabled"
                    print(f"\n🔊 TTS {status}")
                    continue
                
                # Add to memory
                self.memory.add_memory("user", user_input)
                
                # Generate response
                print("\n⏳ Thinking...")
                result = await self.llm.generate_response(user_input)
                
                # Add response to memory
                self.memory.add_memory("assistant", result['response'])
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        # Save memory before exit
        print("\n💾 Saving conversation...")
        self.memory.save_to_disk()
    
    async def run(self):
        """Run the CLI application."""
        # Select LLM provider
        if not await self.select_llm_provider():
            print("\n❌ No provider selected. Exiting.")
            return
        
        # Select persona
        await self.select_persona()
        
        # Start chat
        self.running = True
        await self.chat_loop()
        
        print("\n👋 Thanks for chatting! Goodbye!")
        print("=" * 50)


async def main():
    """Main entry point."""
    cli = AIVTuberCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
