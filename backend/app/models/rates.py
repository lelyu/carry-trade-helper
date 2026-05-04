import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Date, DateTime, DECIMAL, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    base_currency = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    rate = Column(DECIMAL(20, 6), nullable=False)
    date = Column(Date, nullable=False)
    source = Column(String(50), default="frankfurter")
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("idx_exchange_rates_date", "date"),
        Index("idx_exchange_rates_pair", "base_currency", "target_currency"),
        UniqueConstraint(
            "base_currency", "target_currency", "date", name="unique_base_target_date"
        ),
    )


class InterestRate(Base):
    __tablename__ = "interest_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_code = Column(String(3), nullable=False)
    currency_code = Column(String(3), nullable=False)
    rate = Column(DECIMAL(10, 6), nullable=False)
    rate_type = Column(String(50), nullable=True)
    date = Column(Date, nullable=False)
    source = Column(String(50), default="fred")
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("idx_interest_rates_date", "date"),
        Index("idx_interest_rates_country", "country_code"),
    )
