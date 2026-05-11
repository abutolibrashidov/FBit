import os
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.anonymous.models import AnonymousMessage
from app.modules.friendship.models import FriendshipTestResult, FriendshipTest
from app.modules.polls.models import Poll, PollAnswer, PollTemplate
from app.modules.users.models import User

class InboxService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_anonymous_messages(self, user_id: int, limit: int = 5, offset: int = 0):
        result = await self.session.execute(
            select(AnonymousMessage)
            .where(AnonymousMessage.receiver_id == user_id)
            .order_by(desc(AnonymousMessage.created_at))
            .limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_friendship_results(self, user_id: int, limit: int = 5, offset: int = 0):
        result = await self.session.execute(
            select(FriendshipTestResult, User)
            .join(FriendshipTest, FriendshipTestResult.test_id == FriendshipTest.id)
            .join(User, FriendshipTestResult.participant_id == User.id)
            .where(FriendshipTest.owner_id == user_id)
            .order_by(desc(FriendshipTestResult.created_at))
            .limit(limit).offset(offset)
        )
        return result.all()

    async def get_poll_results(self, user_id: int, limit: int = 5, offset: int = 0):
        result = await self.session.execute(
            select(Poll)
            .options(selectinload(Poll.template), selectinload(Poll.answers))
            .where(Poll.owner_id == user_id)
            .order_by(desc(Poll.created_at))
            .limit(limit).offset(offset)
        )
        return result.scalars().all()
