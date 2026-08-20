import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime
from app.core.database import Base

class MCPToolExecutionRecord(Base):
    __tablename__ = "mcp_tool_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(36), nullable=True, index=True)
    server_name = Column(String(50), nullable=False)
    tool_name = Column(String(50), nullable=False)
    repository = Column(String(100), nullable=True)
    execution_time_ms = Column(Float, nullable=False, default=0.0)
    success = Column(Boolean, nullable=False, default=True)
    error_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
