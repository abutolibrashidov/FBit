from sqlalchemy.ext.asyncio import AsyncSession
from modules.analytics.models import AnalyticsEvent

class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def track_event(self, user_id: int, event_type: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        event = AnalyticsEvent(user_id=user_id, event_type=event_type, metadata_json=metadata)
        self.session.add(event)
