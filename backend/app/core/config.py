from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from pathlib import Path

# Resolve base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./ai_fabric.db",
        description="Async connection string (e.g., Supabase postgresql+asyncpg://... or sqlite+aiosqlite:///...)"
    )
    
    # LLM Providers
    GROQ_API_KEY: Optional[str] = None
    
    # MCP GitHub
    GITHUB_TOKEN: Optional[str] = None
    MCP_GITHUB_MODE: str = "mock"  # 'mock' or 'live'
    
    # API Security
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Fabric"
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
