from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram ID
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    language_code: Mapped[str] = mapped_column(String(10), default="uz")
    
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_muted_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    risk_score: Mapped[int] = mapped_column(BigInteger, default=0)
    
    allow_anonymous_messages: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_friend_requests: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_polls: Mapped[bool] = mapped_column(Boolean, default=True)
    show_risk_status: Mapped[bool] = mapped_column(Boolean, default=True)
    
    referred_by_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
