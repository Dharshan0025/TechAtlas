"""
Configuration Manager Utility
Manages application configuration and feature flags
"""

import os
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages application configuration
    """
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Config Manager"""
        if not ConfigManager._config:
            self.load_config()
    
    def load_config(self):
        """Load configuration from environment variables"""
        ConfigManager._config = {
            # API Keys
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
            'FIREBASE_CREDENTIALS_PATH': os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-key.json'),
            
            # Server Configuration
            'PORT': int(os.getenv('PORT', 5000)),
            'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
            'HOST': os.getenv('HOST', '0.0.0.0'),
            
            # AI Models
            'GEMINI_MODEL': os.getenv('GEMINI_MODEL', 'models/gemini-pro-latest'),
            'GEMINI_EMBEDDING_MODEL': os.getenv('GEMINI_EMBEDDING_MODEL', 'models/text-embedding-004'),
            
            # Feature Flags
            'ENABLE_ANALYTICS': os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true',
            'ENABLE_NOTIFICATIONS': os.getenv('ENABLE_NOTIFICATIONS', 'False').lower() == 'true',
            'ENABLE_CACHING': os.getenv('ENABLE_CACHING', 'False').lower() == 'true',
            
            # Limits
            'MAX_DECISIONS_PER_PAGE': int(os.getenv('MAX_DECISIONS_PER_PAGE', 50)),
            'MAX_SEARCH_RESULTS': int(os.getenv('MAX_SEARCH_RESULTS', 100)),
            'MAX_UPLOAD_SIZE_MB': int(os.getenv('MAX_UPLOAD_SIZE_MB', 10)),
            
            # Timeouts
            'REQUEST_TIMEOUT_SECONDS': int(os.getenv('REQUEST_TIMEOUT_SECONDS', 30)),
            'AI_TIMEOUT_SECONDS': int(os.getenv('AI_TIMEOUT_SECONDS', 60)),
            
            # Logging
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', 'techatlas_backend.log'),
            
            # Cache Settings
            'CACHE_TTL_SECONDS': int(os.getenv('CACHE_TTL_SECONDS', 3600)),
            'CACHE_MAX_SIZE': int(os.getenv('CACHE_MAX_SIZE', 1000)),
            
            # Risk Assessment
            'HIGH_RISK_THRESHOLD': int(os.getenv('HIGH_RISK_THRESHOLD', 7)),
            'AGING_DECISION_DAYS': int(os.getenv('AGING_DECISION_DAYS', 60)),
            
            # Notification Settings
            'REMINDER_DAYS_BEFORE_DUE': int(os.getenv('REMINDER_DAYS_BEFORE_DUE', 7)),
            'NOTIFICATION_EMAIL_FROM': os.getenv('NOTIFICATION_EMAIL_FROM', 'noreply@techatlas.com'),
        }
        
        logger.info("Configuration loaded successfully")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        return ConfigManager._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value (runtime only)
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        ConfigManager._config[key] = value
        logger.info(f"Configuration updated: {key}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return ConfigManager._config.copy()
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled
        
        Args:
            feature_name: Feature flag name
        
        Returns:
            True if feature is enabled
        """
        key = f'ENABLE_{feature_name.upper()}'
        return self.get(key, False)
    
    def get_api_key(self, service: str) -> str:
        """
        Get API key for a service
        
        Args:
            service: Service name (e.g., 'GEMINI')
        
        Returns:
            API key
        """
        key = f'{service.upper()}_API_KEY'
        return self.get(key, '')
    
    def validate_config(self) -> tuple:
        """
        Validate required configuration
        
        Returns:
            Tuple of (is_valid, missing_keys)
        """
        required_keys = [
            'GEMINI_API_KEY',
            'FIREBASE_CREDENTIALS_PATH'
        ]
        
        missing = []
        for key in required_keys:
            if not self.get(key):
                missing.append(key)
        
        is_valid = len(missing) == 0
        
        if not is_valid:
            logger.error(f"Missing required configuration: {', '.join(missing)}")
        
        return (is_valid, missing)
    
    def reload(self):
        """Reload configuration from environment"""
        self.load_config()
        logger.info("Configuration reloaded")


# Global instance
config_manager = ConfigManager()
