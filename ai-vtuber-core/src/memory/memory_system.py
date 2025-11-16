"""
Memory System with Encryption Support

Simple in-memory storage with optional encryption for conversation history.
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

from ..error import ErrorHandler, ErrorType, get_error_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a memory entry."""
    timestamp: str
    role: str  # "user" or "assistant"
    content: str
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class MemoryConfig:
    """Configuration for memory system."""
    storage_path: str = "./data/memory"
    max_entries: int = 100
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None  # Base64 encoded key


class MemorySystem:
    """
    Memory system for storing conversation history with encryption.
    """
    
    def __init__(self, config: MemoryConfig, error_handler: Optional[ErrorHandler] = None):
        """
        Initialize the memory system.
        
        Args:
            config: Memory configuration
            error_handler: Optional error handler
        """
        self.config = config
        self.error_handler = error_handler or get_error_handler()
        self.memories: List[MemoryEntry] = []
        
        # Create storage directory first
        Path(config.storage_path).mkdir(parents=True, exist_ok=True)
        
        # Create storage directory first
        Path(config.storage_path).mkdir(parents=True, exist_ok=True)

        # Setup encryption
        self.cipher = None
        if config.encryption_enabled:
            if Fernet is None:
                logger.warning("cryptography package not installed. Encryption disabled.")
                config.encryption_enabled = False

            else:
                self._setup_encryption()


    def _setup_encryption(self):
        """Setup encryption cipher."""
        if self.config.encryption_key:
            # Use provided key
            key = self.config.encryption_key.encode()
        else:
            # Generate new key
            key_file = Path(self.config.storage_path) / ".encryption_key"
            if key_file.exists():
                # Load existing key
                with open(key_file, "rb") as f:
                    key = f.read()
            else:
                # Generate and save new key
                key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(key)
                logger.info("Generated new encryption key")
        
        self.cipher = Fernet(key)
        logger.info("Encryption enabled")
    
    def add_memory(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a memory entry.
        
        Args:
            role: Role (user or assistant)
            content: Content of the message
            metadata: Optional metadata
        """
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.memories.append(entry)
        
        # Limit memory size
        if len(self.memories) > self.config.max_entries:
            self.memories = self.memories[-self.config.max_entries:]
        
        logger.debug(f"Added memory: {role} - {content[:50]}...")
    
    def get_recent_memories(self, limit: int = 10) -> List[MemoryEntry]:
        """
        Get recent memories.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of recent memory entries
        """
        return self.memories[-limit:]
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation history in LLM format.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in format [{"role": "user", "content": "..."}]
        """
        recent = self.get_recent_memories(limit)
        return [{"role": entry.role, "content": entry.content} for entry in recent]
    
    def search_memories(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """
        Simple keyword search in memories.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching memory entries
        """
        query_lower = query.lower()
        matches = [
            entry for entry in self.memories
            if query_lower in entry.content.lower()
        ]
        return matches[-limit:]
    
    def clear_memories(self):
        """Clear all memories."""
        self.memories.clear()
        logger.info("All memories cleared")
    
    def save_to_disk(self, filename: str = "memories.json"):
        """
        Save memories to disk.
        
        Args:
            filename: Filename to save to
        """
        filepath = Path(self.config.storage_path) / filename
        
        # Convert to dict
        data = {
            "memories": [entry.to_dict() for entry in self.memories],
            "saved_at": datetime.now().isoformat()
        }
        
        json_data = json.dumps(data, indent=2)
        
        # Encrypt if enabled
        if self.config.encryption_enabled and self.cipher:
            encrypted_data = self.cipher.encrypt(json_data.encode())
            with open(filepath, "wb") as f:
                f.write(encrypted_data)
            logger.info(f"Saved {len(self.memories)} encrypted memories to {filepath}")
        else:
            with open(filepath, "w") as f:
                f.write(json_data)
            logger.info(f"Saved {len(self.memories)} memories to {filepath}")
    
    def _load_memories(self, filename: str = "memories.json"):
        """
        Load memories from disk.
        
        Args:
            filename: Filename to load from
        """
        filepath = Path(self.config.storage_path) / filename
        
        if not filepath.exists():
            logger.info("No existing memories found")
            return
        
        try:
            # Read file
            with open(filepath, "rb") as f:
                file_data = f.read()
            
            # Decrypt if enabled
            if self.config.encryption_enabled and self.cipher:
                try:
                    json_data = self.cipher.decrypt(file_data).decode()
                except Exception as e:
                    logger.error(f"Failed to decrypt memories: {e}")
                    return
            else:
                json_data = file_data.decode()
            
            # Parse JSON
            data = json.loads(json_data)
            
            # Load memories
            self.memories = [MemoryEntry.from_dict(entry) for entry in data.get("memories", [])]
            logger.info(f"Loaded {len(self.memories)} memories from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_entries": len(self.memories),
            "max_entries": self.config.max_entries,
            "encryption_enabled": self.config.encryption_enabled,
            "storage_path": self.config.storage_path
        }


# Example usage
if __name__ == "__main__":
    # Create memory config
    config = MemoryConfig(
        storage_path="./test_memory",
        max_entries=50,
        encryption_enabled=True
    )
    
    # Create memory system
    memory = MemorySystem(config)
    
    # Add some memories
    print("Adding memories...")
    memory.add_memory("user", "Hello! What's your name?")
    memory.add_memory("assistant", "Hi! I'm Luna, your friendly VTuber companion!")
    memory.add_memory("user", "What can you help me with?")
    memory.add_memory("assistant", "I can chat with you, answer questions, and keep you company!")
    
    # Get recent memories
    print("\nRecent memories:")
    for entry in memory.get_recent_memories(4):
        print(f"  [{entry.timestamp}] {entry.role}: {entry.content}")
    
    # Search memories
    print("\nSearch for 'Luna':")
    for entry in memory.search_memories("Luna"):
        print(f"  {entry.role}: {entry.content}")
    
    # Get conversation history
    print("\nConversation history (LLM format):")
    for msg in memory.get_conversation_history():
        print(f"  {msg}")
    
    # Save to disk
    print("\nSaving to disk...")
    memory.save_to_disk()
    
    # Stats
    print("\nMemory Statistics:")
    for key, value in memory.get_stats().items():
        print(f"  {key}: {value}")
    
    # Test loading
    print("\nTesting load...")
    memory2 = MemorySystem(config)
    print(f"Loaded {len(memory2.memories)} memories")
