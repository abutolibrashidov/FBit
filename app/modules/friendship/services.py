from typing import Optional, List, Dict
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.friendship.models import Question, FriendshipTest, FriendshipTestResult
from datetime import datetime, timedelta
from pytz import timezone

class FriendshipService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_questions(self, category: str = "general", limit: int = 10) -> List[Question]:
        result = await self.session.execute(
            select(Question).where(Question.category == category).limit(limit)
        )
        return result.scalars().all()

    async def create_test(self, owner_id: int, answers: Dict[int, int]) -> FriendshipTest:
        test = FriendshipTest(
            owner_id=owner_id,
            answers=answers
        )
        self.session.add(test)
        await self.session.commit()
        await self.session.refresh(test)
        return test

    async def get_test(self, test_id: uuid.UUID) -> Optional[FriendshipTest]:
        result = await self.session.execute(select(FriendshipTest).where(FriendshipTest.id == test_id))
        return result.scalar_one_or_none()
        
    async def get_active_test_by_owner(self, owner_id: int) -> Optional[FriendshipTest]:
        result = await self.session.execute(
            select(FriendshipTest)
            .where(FriendshipTest.owner_id == owner_id, FriendshipTest.is_active == True)
            .order_by(FriendshipTest.created_at.desc())
        )
        return result.scalars().first()
        
    async def get_participant_action_count(self, participant_id: int) -> int:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        result = await self.session.execute(
            select(func.count(FriendshipTestResult.id))
            .where(FriendshipTestResult.participant_id == participant_id)
            .where(FriendshipTestResult.created_at >= one_hour_ago)
        )
        return result.scalar() or 0

    async def submit_result(self, test_id: uuid.UUID, participant_id: int, participant_answers: Dict[int, int]) -> FriendshipTestResult:
        test = await self.get_test(test_id)
        if not test:
            return None
        
        # Calculate score
        correct_answers = test.answers
        total_questions = len(correct_answers)
        score_count = 0
        
        for q_id, ans_idx in participant_answers.items():
            if str(q_id) in correct_answers and correct_answers[str(q_id)] == ans_idx:
                score_count += 1
            elif int(q_id) in correct_answers and correct_answers[int(q_id)] == ans_idx:
                 score_count += 1
        
        score_percentage = int((score_count / total_questions) * 100) if total_questions > 0 else 0
        
        result = FriendshipTestResult(
            test_id=test_id,
            participant_id=participant_id,
            score=score_percentage,
            answers=participant_answers
        )
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)
        return result
