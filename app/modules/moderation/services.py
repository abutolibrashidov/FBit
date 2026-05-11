import json
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.moderation.models import Report
from app.modules.users.models import User

class ModerationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.bad_words = self._load_bad_words()

    def _load_bad_words(self):
        try:
            with open("bad_words_uz.json", "r", encoding="utf-8") as f:
                return [w.strip().lower() for w in json.load(f)]
        except Exception:
            return []

    def check_text_toxicity(self, text: str) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        for word in self.bad_words:
            if word in text_lower:
                return True
        return False

    async def submit_report(self, message_id: uuid.UUID, receiver_id: int, sender_id: Optional[int], reason: str):
        report = Report(
            message_id=message_id,
            receiver_id=receiver_id,
            sender_id=sender_id,
            report_reason=reason
        )
        self.session.add(report)
        return report

    async def execute_moderation_action(self, report_id: uuid.UUID, action: str, note: str = ""):
        report = await self.session.scalar(select(Report).where(Report.id == report_id))
        if not report:
            return None
            
        report.moderator_note = note
        
        user = None
        if report.sender_id:
            user = await self.session.scalar(select(User).where(User.id == report.sender_id))
            
        if action == "ignore":
            report.status = "ignored"
        elif action == "warn":
            report.status = "warned"
            if user:
                user.risk_score += 10
        elif action == "mute":
            report.status = "muted"
            if user:
                user.is_muted = True
                user.risk_score += 50
                from datetime import datetime, timedelta
                user.is_muted_until = datetime.utcnow() + timedelta(days=1)
        elif action == "ban":
            report.status = "banned"
            if user:
                user.is_banned = True
                user.risk_score += 100
        
        return report
