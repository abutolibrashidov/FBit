import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import BigInteger, String, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.session import Base

class PollTemplate(Base):
    __tablename__ = "poll_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_text: Mapped[str] = mapped_column(String(500)) # e.g. "Meni qanday tariflaysiz?"
    category: Mapped[str] = mapped_column(String(50), default="general")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Poll(Base):
    __tablename__ = "polls"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("poll_templates.id"), nullable=True)
    
    custom_question: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    owner = relationship("User", backref="polls")
    template = relationship("PollTemplate")

class PollAnswer(Base):
    __tablename__ = "poll_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("polls.id"))
    sender_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    
    answer_text: Mapped[str] = mapped_column(String(1000))
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    poll = relationship("Poll", backref="answers")
