from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from modules.analytics.models import AnalyticsEvent

class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def track_event(self, event_type: str, user_id: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            metadata_json=metadata or {}
        )
        self.session.add(event)
        await self.session.commit()

    async def track_registration(self, user_id: int, referral_id: Optional[int] = None):
        await self.track_event("registration", user_id, {"referral_id": referral_id})

    async def track_message_sent(self, sender_id: Optional[int], receiver_id: int):
        await self.track_event("msg_sent", sender_id, {"receiver_id": receiver_id})
