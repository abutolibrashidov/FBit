import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 1):  # default 1 message per second
        self.limit = limit
        self.users = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()
        
        if user_id in self.users:
            last_time = self.users[user_id]
            if current_time - last_time < self.limit:
                return await event.answer("Iltimos, biroz kuting. ⏳")
        
        self.users[user_id] = current_time
        return await handler(event, data)
