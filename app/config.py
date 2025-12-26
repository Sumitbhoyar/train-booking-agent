"""
Configuration management for the application
"""
import os
from typing import Optional


class Settings:
    """Application settings"""
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCOUNT_ID: Optional[str] = os.getenv("AWS_ACCOUNT_ID")
    
    # Application Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API Configuration
    API_TITLE: str = os.getenv("API_TITLE", "Train Booking API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    
    # Bedrock Configuration
    BEDROCK_AGENT_ID: Optional[str] = os.getenv("BEDROCK_AGENT_ID")
    BEDROCK_AGENT_ALIAS_ID: Optional[str] = os.getenv("BEDROCK_AGENT_ALIAS_ID")
    FOUNDATION_MODEL: str = os.getenv(
        "FOUNDATION_MODEL", 
        "anthropic.claude-3-5-sonnet-20241022-v2:0"
    )


settings = Settings()

