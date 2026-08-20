from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class ExecutionTrace(Base):
    __tablename__ = "execution_traces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(36), unique=True, index=True, nullable=False)
    strategy = Column(String(50), nullable=True)
    task_type = Column(String(50), nullable=True)
    selected_model = Column(String(100), nullable=True)
    prompt_version = Column(String(50), nullable=True)
    start_timestamp = Column(DateTime, default=datetime.utcnow)
    end_timestamp = Column(DateTime, nullable=True)
    total_latency_ms = Column(Float, nullable=True)
    input_tokens = Column(Float, nullable=True)
    output_tokens = Column(Float, nullable=True)
    total_tokens = Column(Float, nullable=True)
    cost_usd = Column(Float, nullable=True)
    tool_success = Column(Boolean, nullable=True)
    model_success = Column(Boolean, nullable=True)
    quality_score = Column(Float, nullable=True)
    reward = Column(Float, nullable=True)
    state_vector = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    stages = Column(JSON, nullable=True)  # list of stage dicts
    created_at = Column(DateTime, default=datetime.utcnow)
