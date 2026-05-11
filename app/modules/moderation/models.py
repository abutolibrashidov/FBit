import uuid
from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("anonymous_messages.id"))
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True) # The person who wrote the toxic text, internal only
    receiver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))              # The person reporting
    
    report_reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, reviewed, ignored, warned, muted, banned
    moderator_note: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    message = relationship("AnonymousMessage")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
