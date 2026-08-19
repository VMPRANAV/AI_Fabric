import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class FeedbackRecord(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(36), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    reward = Column(Float, nullable=False, default=0.0)
    quality_score = Column(Float, default=1.0)
    latency_penalty = Column(Float, default=0.0)
    cost_penalty = Column(Float, default=0.0)
    tool_success_reward = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    request = relationship("RequestRecord", back_populates="feedback")
