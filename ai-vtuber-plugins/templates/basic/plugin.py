"""
Basic Plugin Template for AI VTuber Desktop Companion

This is a minimal example of how to create a plugin.
Copy this file and modify it to create your own plugin.
"""

from typing import Dict, Any, Optional


class Plugin:
    """
    Base class for all plugins.
    
    Your plugin should inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin.
        
        Args:
            config: Configuration dictionary for the plugin
        """
        self.name = "BasicPlugin"
        self.version = "0.1.0"
        self.description = "A basic plugin template"
        self.config = config or {}
        
    def on_load(self) -> bool:
        """
        Called when the plugin is loaded.
        
        Returns:
            True if the plugin loaded successfully, False otherwise
        """
        print(f"[{self.name}] Plugin loaded successfully!")
        return True
    
    def on_unload(self) -> bool:
        """
        Called when the plugin is unloaded.
        
        Returns:
            True if the plugin unloaded successfully, False otherwise
        """
        print(f"[{self.name}] Plugin unloaded successfully!")
        return True
    
    def on_event(self, event_type: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Called when an event occurs.
        
        Args:
            event_type: Type of the event (e.g., "user_message", "llm_response")
            event_data: Data associated with the event
            
        Returns:
            Optional response data to be sent back to the system
        """
        print(f"[{self.name}] Received event: {event_type}")
        print(f"[{self.name}] Event data: {event_data}")
        
        # Example: Respond to user messages
        if event_type == "user_message":
            message = event_data.get("message", "")
            if "hello" in message.lower():
                return {
                    "type": "plugin_response",
                    "message": "Hello from the plugin!",
                    "emotion": "happy"
                }
        
        return None
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.
        
        Returns:
            Dictionary containing plugin information
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description
        }


# This is the entry point for the plugin
# The plugin loader will look for this function
def create_plugin(config: Optional[Dict[str, Any]] = None) -> Plugin:
    """
    Create and return a plugin instance.
    
    Args:
        config: Configuration dictionary for the plugin
        
    Returns:
        Plugin instance
    """
    return Plugin(config)
