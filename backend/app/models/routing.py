import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base

class RoutingDecisionRecord(Base):
    __tablename__ = "routing_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(36), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    selected_model = Column(String(100), nullable=False)
    prompt_version = Column(String(50), nullable=True)
    selected_tool = Column(String(50), nullable=True)
    selected_resource = Column(String(50), default="node-1")
    decision_source = Column(String(50), default="rule_based")  # 'rule_based', 'ppo', 'federated'
    # PPO columns
    policy = Column(String(50), nullable=True)
    action = Column(Integer, nullable=True)
    reward = Column(Float, nullable=True)
    state_vector = Column(JSON, nullable=True)
    quality = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    tool_success = Column(Boolean, nullable=True)
    decision_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    request = relationship("RequestRecord", back_populates="routing_decision")
