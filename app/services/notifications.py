from aiogram import Bot
from core.config import settings

class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(self, user_id: int, text: str, **kwargs):
        try:
            await self.bot.send_message(user_id, text, **kwargs)
        except Exception as e:
            # Log error (e.g. user blocked bot)
            print(f"Failed to send message to {user_id}: {e}")

    async def notify_new_anonymous_message(self, user_id: int, message_id: str, content: str):
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from core.texts import UzbekTexts
        
        text = UzbekTexts.NEW_ANON_MSG.format(content=content)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=UzbekTexts.ANON_REPLY_BTN, callback_data=f"anon_reply_{message_id}"),
                    InlineKeyboardButton(text=UzbekTexts.ANON_REPORT_BTN, callback_data=f"anon_report_{message_id}")
                ]
            ]
        )
        await self.send_message(user_id, text, reply_markup=keyboard)

    async def notify_reply_message(self, user_id: int, content: str):
        from core.texts import UzbekTexts
        text = UzbekTexts.NEW_REPLY_MSG.format(content=content)
        await self.send_message(user_id, text)

    async def notify_poll_answer(self, user_id: int, question: str):
        text = f"Sizning '{question}' so'rovingizga yangi javob keldi! 📊"
        await self.send_message(user_id, text)
