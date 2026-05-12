from typing import Optional, List
import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from modules.polls.models import PollTemplate, Poll, PollAnswer

class PollService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_templates(self, category: Optional[str] = None) -> List[PollTemplate]:
        query = select(PollTemplate)
        if category:
            query = query.where(PollTemplate.category == category)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_poll(self, owner_id: int, template_id: Optional[int] = None, custom_question: Optional[str] = None) -> Poll:
        poll = Poll(
            owner_id=owner_id,
            template_id=template_id,
            custom_question=custom_question
        )
        self.session.add(poll)
        await self.session.commit()
        await self.session.refresh(poll)
        return poll

    async def submit_answer(self, poll_id: uuid.UUID, answer_text: str, sender_id: Optional[int] = None) -> PollAnswer:
        answer = PollAnswer(
            poll_id=poll_id,
            sender_id=sender_id,
            answer_text=answer_text
        )
        self.session.add(answer)
        await self.session.commit()
        await self.session.refresh(answer)
        return answer

    async def get_poll(self, poll_id: uuid.UUID) -> Optional[Poll]:
        result = await self.session.execute(
            select(Poll).options(selectinload(Poll.template)).where(Poll.id == poll_id)
        )
        return result.scalar_one_or_none()

    async def get_poll_results(self, poll_id: uuid.UUID) -> List[PollAnswer]:
        result = await self.session.execute(
            select(PollAnswer).where(PollAnswer.poll_id == poll_id)
        )
        return result.scalars().all()
