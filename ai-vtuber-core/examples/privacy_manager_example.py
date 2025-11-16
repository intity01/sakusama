"""
Example implementation of Privacy Manager.

This demonstrates how to manage user privacy, encryption, and permissions.
"""

import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet


class PrivacyManager:
    """
    Central privacy management system.
    """
    
    def __init__(self, config: dict):
        """
        Initialize the privacy manager.
        
        Args:
            config: Privacy configuration
        """
        self.config = config
        self.encryption_enabled = config.get("encryption_at_rest", True)
        self.audit_enabled = config.get("audit_log", {}).get("enabled", True)
        self.audit_log = []
        
        # Initialize encryption
        if self.encryption_enabled:
            self.cipher = self._init_encryption()
        
    def _init_encryption(self) -> Fernet:
        """Initialize encryption cipher."""
        # In production, load key from secure key store
        # This is just an example
        key = Fernet.generate_key()
        return Fernet(key)
    
    def encrypt_data(self, data: str) -> bytes:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        if not self.encryption_enabled:
            return data.encode()
        
        encrypted = self.cipher.encrypt(data.encode())
        self._log_audit("data_encrypted", {"size": len(data)})
        return encrypted
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
        """
        if not self.encryption_enabled:
            return encrypted_data.decode()
        
        decrypted = self.cipher.decrypt(encrypted_data).decode()
        self._log_audit("data_decrypted", {"size": len(decrypted)})
        return decrypted
    
    def _log_audit(self, action: str, details: dict):
        """Log action to audit log."""
        if not self.audit_enabled:
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.audit_log.append(entry)
        print(f"[Audit] {action}: {details}")
    
    def get_audit_log(self) -> List[dict]:
        """Get audit log entries."""
        return self.audit_log


class PermissionController:
    """
    Controls plugin permissions.
    """
    
    def __init__(self, privacy_manager: PrivacyManager):
        """
        Initialize permission controller.
        
        Args:
            privacy_manager: Privacy manager instance
        """
        self.privacy_manager = privacy_manager
        self.granted_permissions: Dict[str, List[str]] = {}
        
    def request_permission(
        self,
        plugin_id: str,
        permission: str,
        auto_approve: bool = False
    ) -> bool:
        """
        Request permission for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            permission: Permission being requested
            auto_approve: Whether to auto-approve (for testing)
            
        Returns:
            True if permission granted, False otherwise
        """
        # Check if already granted
        if plugin_id in self.granted_permissions:
            if permission in self.granted_permissions[plugin_id]:
                return True
        
        # In production, this would show UI to user
        if auto_approve:
            approved = True
        else:
            # Simulate user approval
            print(f"[Permission] Plugin '{plugin_id}' requests '{permission}'")
            approved = input("Approve? (y/n): ").lower() == 'y'
        
        if approved:
            if plugin_id not in self.granted_permissions:
                self.granted_permissions[plugin_id] = []
            self.granted_permissions[plugin_id].append(permission)
            
            self.privacy_manager._log_audit(
                "permission_granted",
                {"plugin_id": plugin_id, "permission": permission}
            )
            return True
        else:
            self.privacy_manager._log_audit(
                "permission_denied",
                {"plugin_id": plugin_id, "permission": permission}
            )
            return False
    
    def check_permission(self, plugin_id: str, permission: str) -> bool:
        """
        Check if plugin has permission.
        
        Args:
            plugin_id: ID of the plugin
            permission: Permission to check
            
        Returns:
            True if plugin has permission
        """
        if plugin_id not in self.granted_permissions:
            return False
        return permission in self.granted_permissions[plugin_id]
    
    def revoke_permission(self, plugin_id: str, permission: str):
        """
        Revoke permission from plugin.
        
        Args:
            plugin_id: ID of the plugin
            permission: Permission to revoke
        """
        if plugin_id in self.granted_permissions:
            if permission in self.granted_permissions[plugin_id]:
                self.granted_permissions[plugin_id].remove(permission)
                
                self.privacy_manager._log_audit(
                    "permission_revoked",
                    {"plugin_id": plugin_id, "permission": permission}
                )


class AnalyticsManager:
    """
    Manages analytics with opt-in/out.
    """
    
    def __init__(self, privacy_manager: PrivacyManager, config: dict):
        """
        Initialize analytics manager.
        
        Args:
            privacy_manager: Privacy manager instance
            config: Analytics configuration
        """
        self.privacy_manager = privacy_manager
        self.enabled = config.get("enabled", False)
        self.anonymize = config.get("anonymize_data", True)
        
    def track_event(self, event_name: str, event_data: dict):
        """
        Track an analytics event.
        
        Args:
            event_name: Name of the event
            event_data: Event data
        """
        if not self.enabled:
            return
        
        # Anonymize data if required
        if self.anonymize:
            event_data = self._anonymize_data(event_data)
        
        # In production, send to analytics service
        print(f"[Analytics] Event: {event_name}, Data: {event_data}")
        
        self.privacy_manager._log_audit(
            "analytics_event",
            {"event": event_name, "anonymized": self.anonymize}
        )
    
    def _anonymize_data(self, data: dict) -> dict:
        """
        Anonymize sensitive data.
        
        Args:
            data: Data to anonymize
            
        Returns:
            Anonymized data
        """
        anonymized = {}
        for key, value in data.items():
            if key in ["user_id", "username", "email"]:
                # Hash sensitive fields
                anonymized[key] = hashlib.sha256(str(value).encode()).hexdigest()[:16]
            else:
                anonymized[key] = value
        return anonymized
    
    def set_enabled(self, enabled: bool):
        """Enable or disable analytics."""
        self.enabled = enabled
        self.privacy_manager._log_audit(
            "analytics_toggled",
            {"enabled": enabled}
        )


# Example usage
if __name__ == "__main__":
    # Initialize privacy manager
    config = {
        "encryption_at_rest": True,
        "audit_log": {"enabled": True}
    }
    privacy_mgr = PrivacyManager(config)
    
    # Test encryption
    original = "This is sensitive user data"
    encrypted = privacy_mgr.encrypt_data(original)
    decrypted = privacy_mgr.decrypt_data(encrypted)
    print(f"Original: {original}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    
    # Test permissions
    perm_ctrl = PermissionController(privacy_mgr)
    granted = perm_ctrl.request_permission("weather_plugin", "read_messages", auto_approve=True)
    print(f"Permission granted: {granted}")
    
    # Test analytics
    analytics_config = {"enabled": True, "anonymize_data": True}
    analytics = AnalyticsManager(privacy_mgr, analytics_config)
    analytics.track_event("user_message", {"user_id": "user123", "message_length": 50})
    
    # View audit log
    print("\nAudit Log:")
    for entry in privacy_mgr.get_audit_log():
        print(f"  {entry}")
