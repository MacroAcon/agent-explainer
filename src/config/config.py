from typing import Dict, Any, List, Optional
from pydantic import BaseSettings, SecretStr
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Settings(BaseSettings):
    """Base configuration."""
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Configuration
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4-1106-preview")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Agent Configuration
    MAX_CONSECUTIVE_AUTO_REPLY: int = 10
    TEMPERATURE: float = TEMPERATURE
    
    # Business Configuration
    BUSINESS_NAME: str = os.getenv("BUSINESS_NAME", "")
    BUSINESS_TYPE: str = os.getenv("BUSINESS_TYPE", "")
    BUSINESS_DESCRIPTION: str = os.getenv("BUSINESS_DESCRIPTION", "")
    LOCATION: str = os.getenv("LOCATION", "Calhoun, GA")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./business.db")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ALGORITHM: str = "HS256"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "business_automation.log")
    
    # Agent Configuration
    AGENT_MEMORY_TTL: int = int(os.getenv("AGENT_MEMORY_TTL", "3600"))  # 1 hour
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT: int = int(os.getenv("TIMEOUT", "300"))  # 5 minutes
    
    # Local Business Integration
    LOCAL_SUPPLIERS_FILE: str = os.getenv("LOCAL_SUPPLIERS_FILE", "local_suppliers.json")
    COMMUNITY_EVENTS_FILE: str = os.getenv("COMMUNITY_EVENTS_FILE", "community_events.json")
    
    # Feature Flags
    ENABLE_HIPAA: bool = os.getenv("ENABLE_HIPAA", "True").lower() == "true"
    ENABLE_AUDIT_LOGGING: bool = os.getenv("ENABLE_AUDIT_LOGGING", "True").lower() == "true"
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "True").lower() == "true"
    
    # HIPAA Compliance Configuration
    HIPAA_ENABLED: bool = ENABLE_HIPAA
    PHI_FIELDS: List[str] = [
        "name", "address", "email", "phone", "dob", "ssn", 
        "medical_record_number", "health_plan_number",
        "account_number", "biometric_identifiers",
        "full_face_photos", "any_other_unique_identifying_number"
    ]
    
    # Data Privacy Settings
    DATA_ENCRYPTION_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 30
    AUDIT_LOGGING_ENABLED: bool = ENABLE_AUDIT_LOGGING
    
    # Security Configuration
    REQUIRE_2FA: bool = True
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 3
    
    # Logging Configuration
    AUDIT_LOG_PATH: str = "audit_logs/"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 

def validate_settings() -> None:
    """Validate required settings are present."""
    required_settings = [
        ("API_KEY", settings.API_KEY),
        ("BUSINESS_NAME", settings.BUSINESS_NAME),
        ("BUSINESS_TYPE", settings.BUSINESS_TYPE),
        ("SECRET_KEY", settings.SECRET_KEY)
    ]
    
    missing_settings = [name for name, value in required_settings if not value]
    
    if missing_settings:
        raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")
    
    if settings.BUSINESS_TYPE not in ["restaurant", "retail"]:
        raise ValueError("BUSINESS_TYPE must be either 'restaurant' or 'retail'")

# Example environment-specific configurations
ENVIRONMENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "development": {
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "sqlite:///./dev_business.db"
    },
    "testing": {
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "sqlite:///./test_business.db"
    },
    "production": {
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "DATABASE_URL": os.getenv("PROD_DATABASE_URL", "sqlite:///./prod_business.db")
    }
}

# Update settings based on environment
env_config = ENVIRONMENT_CONFIGS.get(settings.ENV, {})
for key, value in env_config.items():
    setattr(settings, key, value)

# Ensure all paths exist
def ensure_paths() -> None:
    """Ensure required paths exist."""
    paths = [
        Path("logs"),
        Path("data"),
        Path("data/local_suppliers"),
        Path("data/community_events")
    ]
    
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)

# Initialize configuration
def init_config() -> None:
    """Initialize configuration."""
    validate_settings()
    ensure_paths() 