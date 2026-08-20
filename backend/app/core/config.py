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
    
    # LLM Providers & Model Profiles
    GROQ_API_KEY: Optional[str] = None
    MODEL_PROVIDER: str = "mock"  # 'groq' or 'mock'
    MODEL_FALLBACK_ENABLED: bool = False
    
    # Configurable Generation Model Profiles
    AI_MODEL_FAST: str = "openai/gpt-oss-20b"
    AI_MODEL_BALANCED: str = "openai/gpt-oss-20b"
    AI_MODEL_REASONING: str = "openai/gpt-oss-120b"
    AI_MODEL_MOCK: str = "mock-deterministic-v1"
    # PPO configuration
    DECISION_POLICY: str = "rule_based"
    PPO_ALPHA: float = 0.40
    PPO_BETA: float = 0.20
    PPO_GAMMA: float = 0.20
    PPO_DELTA: float = 0.20
    PPO_SEED: int = 42
    
    # MCP Settings
    GITHUB_TOKEN: Optional[str] = None
    MCP_PROVIDER: str = "mock"  # 'mock' or 'github'
    MCP_GITHUB_MODE: str = "mock"  # 'mock' or 'live'
    GITHUB_ALLOWED_REPOS: str = "pranavvm/AI-Fabric,owner/repo,username/repository-name,owner1/repo1,owner2/repo2"
    GITHUB_ALLOW_ALL: bool = False
    MCP_TOOL_TIMEOUT_SECONDS: int = 10
    ALLOWED_MCP_TOOLS: list[str] = [
        "github_mcp.list_files",
        "github_mcp.get_file",
        "github_mcp.search_code",
        "github_mcp.get_repo_structure"
    ]
    
    # API Security
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Fabric"
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
