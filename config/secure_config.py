"""
Secure Configuration Management for My Prabh
Handles environment variables and sensitive configuration data
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import json
import logging

logger = logging.getLogger(__name__)

class SecureConfig:
    """Secure configuration management with environment variables"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Validate critical environment variables
        self._validate_required_vars()
        
        logger.info("🔒 Secure configuration loaded successfully")
    
    def _validate_required_vars(self):
        """Validate that all required environment variables are set"""
        required_vars = [
            'FIREBASE_API_KEY',
            'FIREBASE_PROJECT_ID',
            'SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    # Firebase Configuration
    @property
    def firebase_config(self) -> Dict[str, str]:
        """Get Firebase configuration for client-side use"""
        return {
            'apiKey': os.getenv('FIREBASE_API_KEY'),
            'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
            'projectId': os.getenv('FIREBASE_PROJECT_ID'),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
            'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            'appId': os.getenv('FIREBASE_APP_ID')
        }
    
    @property
    def firebase_project_id(self) -> str:
        """Get Firebase project ID"""
        return os.getenv('FIREBASE_PROJECT_ID')
    
    # Payment Configuration
    @property
    def razorpay_key_id(self) -> str:
        """Get Razorpay key ID"""
        return os.getenv('RAZORPAY_KEY_ID')
    
    @property
    def razorpay_key_secret(self) -> str:
        """Get Razorpay key secret"""
        return os.getenv('RAZORPAY_KEY_SECRET')
    
    # AI Configuration
    @property
    def openrouter_api_key(self) -> str:
        """Get OpenRouter API key"""
        return os.getenv('OPENROUTER_API_KEY')
    
    # Database Configuration
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return os.getenv('DATABASE_URL')
    
    # Security Configuration
    @property
    def secret_key(self) -> str:
        """Get Flask secret key"""
        return os.getenv('SECRET_KEY')
    
    @property
    def jwt_secret_key(self) -> str:
        """Get JWT secret key"""
        return os.getenv('JWT_SECRET_KEY', self.secret_key)
    
    # Email Configuration
    @property
    def email_config(self) -> Dict[str, str]:
        """Get email service configuration"""
        return {
            'api_key': os.getenv('EMAIL_SERVICE_API_KEY'),
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_username': os.getenv('SMTP_USERNAME'),
            'smtp_password': os.getenv('SMTP_PASSWORD')
        }
    
    # Phone Verification Configuration
    @property
    def twilio_config(self) -> Dict[str, str]:
        """Get Twilio configuration"""
        return {
            'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
            'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
            'phone_number': os.getenv('TWILIO_PHONE_NUMBER')
        }
    
    # Memory System Configuration
    @property
    def memory_config(self) -> Dict[str, Any]:
        """Get memory system configuration"""
        return {
            'vector_db_url': os.getenv('VECTOR_DB_URL'),
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
            'storage_path': os.getenv('MEMORY_STORAGE_PATH', './memory_storage')
        }
    
    # Environment Configuration
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return os.getenv('FLASK_ENV') == 'production'
    
    @property
    def debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Rate Limiting Configuration
    @property
    def rate_limits(self) -> Dict[str, int]:
        """Get rate limiting configuration"""
        return {
            'per_minute': int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),
            'per_hour': int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))
        }
    
    # Session Configuration
    @property
    def session_config(self) -> Dict[str, int]:
        """Get session configuration"""
        return {
            'timeout': int(os.getenv('SESSION_TIMEOUT', '3600')),
            'permanent_lifetime': int(os.getenv('PERMANENT_SESSION_LIFETIME', '86400'))
        }
    
    # Google Cloud Configuration
    @property
    def google_cloud_config(self) -> Dict[str, str]:
        """Get Google Cloud configuration"""
        return {
            'project_id': os.getenv('GOOGLE_CLOUD_PROJECT_ID'),
            'storage_bucket': os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET')
        }
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with optional default"""
        return os.getenv(key, default)
    
    def get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get environment variable as boolean"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def get_env_int(self, key: str, default: int = 0) -> int:
        """Get environment variable as integer"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def mask_sensitive_value(self, value: str, show_chars: int = 4) -> str:
        """Mask sensitive values for logging"""
        if not value or len(value) <= show_chars:
            return "***"
        return value[:show_chars] + "*" * (len(value) - show_chars)
    
    def get_config_summary(self) -> Dict[str, str]:
        """Get configuration summary for logging (with masked sensitive data)"""
        return {
            'firebase_project': self.firebase_project_id,
            'razorpay_key': self.mask_sensitive_value(self.razorpay_key_id or ""),
            'openrouter_key': self.mask_sensitive_value(self.openrouter_api_key or ""),
            'environment': os.getenv('FLASK_ENV', 'development'),
            'debug': str(self.debug_mode),
            'database_configured': bool(self.database_url)
        }

# Global configuration instance
config = SecureConfig()

# Export commonly used configurations
FIREBASE_CONFIG = config.firebase_config
SECRET_KEY = config.secret_key
IS_PRODUCTION = config.is_production
DEBUG_MODE = config.debug_mode