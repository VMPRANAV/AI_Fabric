import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime
from app.core.database import Base

class LLMModelRecord(Base):
    __tablename__ = "llm_models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    provider = Column(String(50), nullable=False)  # 'groq', 'mock', etc.
    tier = Column(String(50), default="medium")  # 'fast', 'balanced', 'reasoning'
    cost_per_1k_prompt_tokens = Column(Float, default=0.0005)
    cost_per_1k_completion_tokens = Column(Float, default=0.0015)
    max_context_window = Column(Float, default=128000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
