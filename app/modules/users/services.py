from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.repositories import UserRepository
from app.modules.users.models import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def get_or_create_user(self, telegram_id: int, **kwargs) -> User:
        user = await self.repo.get_by_id(telegram_id)
        if not user:
            user_data = {
                "id": telegram_id,
                "username": kwargs.get("username"),
                "full_name": kwargs.get("full_name", "Unknown"),
                "language_code": kwargs.get("language_code", "uz"),
                "referred_by_id": kwargs.get("referred_by_id")
            }
            user = await self.repo.create(user_data)
        return user

    async def ban_user(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if user:
            return await self.repo.update(user, {"is_banned": True})
        return None

    async def toggle_premium(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if user:
            return await self.repo.update(user, {"is_premium": not user.is_premium})
        return None
