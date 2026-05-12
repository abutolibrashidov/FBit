import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.session import Base

class AnonymousMessage(Base):
    __tablename__ = "anonymous_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    receiver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    sender_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True) # Optional link to sender if they are registered
    content: Mapped[str] = mapped_column(Text)
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_reported: Mapped[bool] = mapped_column(Boolean, default=False)
    report_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    replied_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("anonymous_messages.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    receiver = relationship("User", foreign_keys=[receiver_id])
    sender = relationship("User", foreign_keys=[sender_id])
