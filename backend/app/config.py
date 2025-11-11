# Configuration settings for the Loan Processing AI Agent

from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "Loan Processing AI Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database (Neon DB - Serverless Postgres)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@host/dbname"
    DB_ECHO: bool = False  # Set to True for SQL query logging
    
    # API Keys (ONLY Groq)
    GROQ_API_KEY: str  # Required - no other providers supported
    
    # AI Provider Selection
    AI_PROVIDER: str = "groq"  # Fixed to groq only
    
    # Groq Model Configuration
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  # Fast inference with Llama 3.3
    
    # CORS - can be set as comma-separated string in .env
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return v
        return v
    
    def get_cors_list(self) -> list[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Business Rules
    MAX_LOAN_AMOUNT: float = 1000000.0
    MIN_CREDIT_SCORE: int = 300
    MAX_CREDIT_SCORE: int = 850
    MIN_DTI_RATIO: float = 0.0
    MAX_DTI_RATIO: float = 0.50
    
    # Agent Timeouts (seconds)
    AGENT_TIMEOUT: int = 30
    ORCHESTRATOR_TIMEOUT: int = 120
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
