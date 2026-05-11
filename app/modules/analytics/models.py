from datetime import datetime
from sqlalchemy import BigInteger, String, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    event_type: Mapped[str] = mapped_column(String(100)) # e.g. "registration", "msg_sent", "poll_created"
    
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    def __repr__(self) -> str:
        return f"<AnalyticsEvent(type={self.event_type}, user={self.user_id})>"
