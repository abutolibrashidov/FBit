from typing import Optional, List
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.anonymous.models import AnonymousMessage
from services.notifications import NotificationService

class AnonymousMessageService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def send_anonymous_message(self, receiver_id: int, content: str, sender_id: Optional[int] = None) -> AnonymousMessage:
        msg = AnonymousMessage(
            receiver_id=receiver_id,
            sender_id=sender_id,
            content=content
        )
        self.session.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        return msg

    async def get_message(self, message_id: uuid.UUID) -> Optional[AnonymousMessage]:
        result = await self.session.execute(select(AnonymousMessage).where(AnonymousMessage.id == message_id))
        return result.scalar_one_or_none()

    async def report_message(self, message_id: uuid.UUID, reason: str):
        msg = await self.get_message(message_id)
        if msg:
            msg.is_reported = True
            msg.report_reason = reason
            await self.session.commit()
            return True
        return False
