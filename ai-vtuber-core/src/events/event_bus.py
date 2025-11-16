"""
Event Bus System for AI VTuber Core

This module provides a central event bus for communication between different components.
"""

import asyncio
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the system."""
    # User input events
    USER_TEXT_INPUT = "user_text_input"
    USER_VOICE_INPUT = "user_voice_input"
    
    # AI processing events
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    LLM_ERROR = "llm_error"
    
    # Memory events
    MEMORY_STORE = "memory_store"
    MEMORY_RETRIEVE = "memory_retrieve"
    
    # Persona events
    PERSONA_CHANGE = "persona_change"
    PERSONA_LOADED = "persona_loaded"
    
    # Output events
    TEXT_OUTPUT = "text_output"
    VOICE_OUTPUT = "voice_output"
    EMOTION_OUTPUT = "emotion_output"
    
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_READY = "system_ready"
    SYSTEM_SHUTDOWN = "system_shutdown"


@dataclass
class Event:
    """Represents an event in the system."""
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    
    def __str__(self):
        return f"Event({self.type.value}, source={self.source}, data={self.data})"


class EventBus:
    """
    Central event bus for the AI VTuber system.
    
    Supports:
    - Event publishing and subscription
    - Async event handling
    - Event history
    - Error handling
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the event bus.
        
        Args:
            max_history: Maximum number of events to keep in history
        """
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = max_history
        self._running = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        
    def subscribe(self, event_type: EventType, handler: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type.value}")
        
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                logger.info(f"Unsubscribed handler from {event_type.value}")
    
    async def publish(self, event: Event):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        logger.info(f"Publishing event: {event}")
        
        # Get subscribers for this event type
        handlers = self._subscribers.get(event.type, [])
        
        # Call all handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.type.value}: {e}")
                # Publish error event
                error_event = Event(
                    type=EventType.SYSTEM_ERROR,
                    data={
                        "error": str(e),
                        "original_event": event.type.value,
                        "handler": handler.__name__
                    },
                    source="event_bus"
                )
                # Avoid infinite loop by not publishing error events for error handlers
                if event.type != EventType.SYSTEM_ERROR:
                    await self.publish(error_event)
    
    def publish_sync(self, event: Event):
        """
        Publish an event synchronously (for non-async contexts).
        
        Args:
            event: Event to publish
        """
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        logger.info(f"Publishing event (sync): {event}")
        
        # Get subscribers for this event type
        handlers = self._subscribers.get(event.type, [])
        
        # Call all handlers (sync only)
        for handler in handlers:
            try:
                if not asyncio.iscoroutinefunction(handler):
                    handler(event)
                else:
                    logger.warning(f"Skipping async handler in sync publish: {handler.__name__}")
            except Exception as e:
                logger.error(f"Error in event handler for {event.type.value}: {e}")
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 10) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        if event_type:
            filtered = [e for e in self._event_history if e.type == event_type]
            return filtered[-limit:]
        return self._event_history[-limit:]
    
    def clear_history(self):
        """Clear event history."""
        self._event_history.clear()
        logger.info("Event history cleared")


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


# Example usage
if __name__ == "__main__":
    async def main():
        # Create event bus
        bus = EventBus()
        
        # Subscribe to events
        def on_text_input(event: Event):
            print(f"Received text input: {event.data.get('text')}")
        
        async def on_llm_response(event: Event):
            print(f"Received LLM response: {event.data.get('response')}")
        
        bus.subscribe(EventType.USER_TEXT_INPUT, on_text_input)
        bus.subscribe(EventType.LLM_RESPONSE, on_llm_response)
        
        # Publish events
        await bus.publish(Event(
            type=EventType.USER_TEXT_INPUT,
            data={"text": "Hello, AI!"},
            source="user"
        ))
        
        await bus.publish(Event(
            type=EventType.LLM_RESPONSE,
            data={"response": "Hello! How can I help you?", "emotion": "happy"},
            source="llm"
        ))
        
        # Get history
        print("\nEvent History:")
        for event in bus.get_history():
            print(f"  {event}")
    
    asyncio.run(main())
