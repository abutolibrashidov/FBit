from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.texts import UzbekTexts
from bot.keyboards import get_main_keyboard
from modules.users.services import UserService
from database.session import async_session

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    async with async_session() as session:
        user_service = UserService(session)
        
        # Handle referral if any
        referral_id = None
        anon_receiver_id = None
        friend_owner_id = None
        if message.text and len(message.text.split()) > 1:
            start_param = message.text.split()[1]
            if start_param.startswith("ref_"):
                referral_id = int(start_param.replace("ref_", ""))
            elif start_param.startswith("msg_"):
                try:
                    anon_receiver_id = int(start_param.replace("msg_", ""))
                except ValueError:
                    pass
            elif start_param.startswith("friend_"):
                try:
                    friend_owner_id = int(start_param.replace("friend_", ""))
                except ValueError:
                    pass
            elif start_param.startswith("poll_"):
                poll_id_str = start_param.replace("poll_", "")

        user = await user_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            language_code=message.from_user.language_code,
            referred_by_id=referral_id
        )

        from modules.analytics.services import AnalyticsService
        analytics = AnalyticsService(session)
        await analytics.track_event(user.id, "start", {"ref": referral_id})

        if getattr(user, 'is_banned', False):
            await message.answer("Siz platformadan bloklangansiz. Barcha tizimlar yopilgan.")
            return
            
        if anon_receiver_id and anon_receiver_id != message.from_user.id:
            from modules.anonymous.handlers import handle_anonymous_start
            await handle_anonymous_start(message, anon_receiver_id, state)
            return
        elif anon_receiver_id == message.from_user.id:
            await message.answer("Siz o'zingizga anonim xabar yubora olmaysiz! 😅")
            
        if friend_owner_id:
            from modules.friendship.handlers import handle_friend_start
            await handle_friend_start(message, friend_owner_id, state)
            return
            
        poll_id_str = locals().get('poll_id_str')
        if poll_id_str:
            if UXControlLayer.can_participate_in_polls(user):
                from modules.polls.handlers import handle_poll_start
                await handle_poll_start(message, poll_id_str, state)
            else:
                await message.answer("Siz so'rovnomalarda qatnashish ruxsatini o'chirgansiz. Sozlamalar orqali yoqing. 🔒")
            return
            
        await message.answer(UzbekTexts.WELCOME, reply_markup=get_main_keyboard())

def setup_handlers(dp):
    from modules.anonymous.handlers import router as anonymous_router
    from modules.friendship.handlers import router as friendship_router
    from modules.polls.handlers import router as polls_router
    from modules.inbox.handlers import router as inbox_router
    from modules.users.handlers import router as users_router
    
    dp.include_router(router)
    dp.include_router(users_router)
    dp.include_router(anonymous_router)
    dp.include_router(friendship_router)
    dp.include_router(polls_router)
    dp.include_router(inbox_router)
