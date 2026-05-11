import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import BigInteger, String, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

class Question(Base):
    __tablename__ = "friendship_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(500))  # Question text in Uzbek
    options: Mapped[dict] = mapped_column(JSON)     # Options as JSON array
    correct_option_index: Mapped[int] = mapped_column(default=0)
    category: Mapped[str] = mapped_column(String(50), default="general")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class FriendshipTest(Base):
    __tablename__ = "friendship_tests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    
    # Answers by the owner to define the "correct" answers for others
    answers: Mapped[dict] = mapped_column(JSON) # Map of question_id -> answer_index
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    owner = relationship("User", backref="friendship_tests")

class FriendshipTestResult(Base):
    __tablename__ = "friendship_test_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("friendship_tests.id"))
    participant_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    
    score: Mapped[int] = mapped_column() # Percentage score
    answers: Mapped[dict] = mapped_column(JSON) # Map of question_id -> participant_answer_index
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    test = relationship("FriendshipTest", backref="results")
    participant = relationship("User")
