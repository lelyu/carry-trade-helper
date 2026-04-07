import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    currency_pairs = Column(ARRAY(String), nullable=False, default=[
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", 
        "AUD/USD", "USD/CAD", "NZD/USD", "USD/CNY", "USD/HKD"
    ])
    email_frequency = Column(String(20), default="daily")
    alert_thresholds = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="preferences")