from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date, update
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from jose import jwt, JWTError

from database.session import get_db
from core.config import settings

from modules.users.models import User
from modules.analytics.models import AnalyticsEvent
from modules.moderation.models import Report
from modules.anonymous.models import AnonymousMessage
from modules.friendship.models import FriendshipTestResult
from modules.polls.models import PollAnswer

admin_router = APIRouter()
bearer_scheme = HTTPBearer()

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


# ── Auth helpers ──────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, settings.ADMIN_SECRET, algorithm=ALGORITHM)


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    try:
        payload = jwt.decode(credentials.credentials, settings.ADMIN_SECRET, algorithms=[ALGORITHM])
        if payload.get("sub") != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    return credentials.credentials


# ── Auth endpoint (public) ────────────────────────────────────────────────────

@admin_router.post("/login")
async def login(body: LoginRequest):
    if body.username != settings.ADMIN_USERNAME or body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": "admin"})
    return {"token": token}


# ── Protected endpoints ───────────────────────────────────────────────────────

@admin_router.get("/dashboard", dependencies=[Depends(verify_admin_token)])
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    return {"status": "operational", "message": "FBit Admin API"}


@admin_router.get("/users", dependencies=[Depends(verify_admin_token)])
async def list_users(db: AsyncSession = Depends(get_db), limit: int = 50, offset: int = 0):
    result = await db.execute(select(User).order_by(User.created_at.desc()).limit(limit).offset(offset))
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "is_banned": u.is_banned,
            "is_muted": u.is_muted,
            "is_muted_until": u.is_muted_until.isoformat() if u.is_muted_until else None,
            "risk_score": u.risk_score,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@admin_router.post("/users/{user_id}/ban", dependencies=[Depends(verify_admin_token)])
async def ban_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_banned = True
    await db.commit()
    return {"status": "banned", "user_id": user_id}


@admin_router.post("/users/{user_id}/unban", dependencies=[Depends(verify_admin_token)])
async def unban_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_banned = False
    await db.commit()
    return {"status": "unbanned", "user_id": user_id}


@admin_router.post("/users/{user_id}/mute", dependencies=[Depends(verify_admin_token)])
async def mute_user(user_id: int, hours: int = 24, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_muted = True
    user.is_muted_until = datetime.utcnow() + timedelta(hours=hours)
    await db.commit()
    return {"status": "muted", "user_id": user_id, "until": user.is_muted_until.isoformat()}


@admin_router.get("/reports", dependencies=[Depends(verify_admin_token)])
async def get_reports(db: AsyncSession = Depends(get_db), status: str = "pending"):
    result = await db.execute(
        select(Report).where(Report.status == status).order_by(Report.created_at.desc()).limit(50)
    )
    reports = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "receiver_id": r.receiver_id,
            "sender_id": r.sender_id,
            "report_reason": r.report_reason,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


@admin_router.post("/moderation", dependencies=[Depends(verify_admin_token)])
async def execute_moderation(report_id: str, action: str, note: str = "", db: AsyncSession = Depends(get_db)):
    from modules.moderation.services import ModerationService
    import uuid
    service = ModerationService(db)
    result = await service.execute_moderation_action(uuid.UUID(report_id), action, note)
    if result:
        await db.commit()
        return {"status": "success", "action": action}
    raise HTTPException(status_code=404, detail="Report not found")


@admin_router.get("/analytics", dependencies=[Depends(verify_admin_token)])
async def get_analytics(db: AsyncSession = Depends(get_db)):
    today = date.today()

    total_users = await db.scalar(select(func.count(User.id)))
    new_users_today = await db.scalar(select(func.count(User.id)).where(cast(User.created_at, Date) == today))
    active_users_today = await db.scalar(
        select(func.count(func.distinct(AnalyticsEvent.user_id)))
        .where(cast(AnalyticsEvent.created_at, Date) == today)
    )

    anonymous_messages_today = await db.scalar(select(func.count(AnonymousMessage.id)).where(cast(AnonymousMessage.created_at, Date) == today))
    friendship_tests_today = await db.scalar(select(func.count(FriendshipTestResult.id)).where(cast(FriendshipTestResult.created_at, Date) == today))
    poll_votes_today = await db.scalar(select(func.count(PollAnswer.id)).where(cast(PollAnswer.created_at, Date) == today))

    reports_today = await db.scalar(select(func.count(Report.id)).where(cast(Report.created_at, Date) == today))
    banned_users = await db.scalar(select(func.count(User.id)).where(User.is_banned == True))

    return {
        "total_users": total_users,
        "new_users_today": new_users_today,
        "active_users_today": active_users_today,
        "anonymous_messages_today": anonymous_messages_today,
        "friendship_tests_today": friendship_tests_today,
        "poll_votes_today": poll_votes_today,
        "reports_today": reports_today,
        "banned_users": banned_users
    }
