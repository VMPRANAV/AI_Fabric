import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class RequestRecord(Base):
    __tablename__ = "requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_text = Column(Text, nullable=False)
    task_type = Column(String(50), nullable=True)
    complexity = Column(Float, default=0.5)
    tool_required = Column(String(50), nullable=True)
    reasoning_required = Column(String(10), default="medium")
    budget = Column(String(20), default="medium")
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    routing_decision = relationship("RoutingDecisionRecord", back_populates="request", uselist=False, cascade="all, delete-orphan")
    execution_metric = relationship("ExecutionMetricRecord", back_populates="request", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("FeedbackRecord", back_populates="request", uselist=False, cascade="all, delete-orphan")
