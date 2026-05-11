from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.texts import UzbekTexts
from app.modules.anonymous.services import AnonymousMessageService
from app.database.session import async_session
from app.services.notifications import NotificationService

router = Router()

class AnonymousStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_report = State()
    waiting_for_reply = State()

@router.message(F.text == "🤫 Anonim xabar havolasi")
async def show_link(message: types.Message):
    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=msg_{message.from_user.id}"
    await message.answer(UzbekTexts.ANONYMOUS_LINK.format(link=link))

# Handler for start with msg_ parameter is usually in main handlers or separated
# For now, let's assume it's handled in a way that sets state

async def handle_anonymous_start(message: types.Message, receiver_id: int, state: FSMContext):
    await state.set_state(AnonymousStates.waiting_for_message)
    await state.update_data(receiver_id=receiver_id)
    await message.answer(UzbekTexts.SEND_MSG_PROMPT)

@router.message(AnonymousStates.waiting_for_message)
async def process_anonymous_message(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    receiver_id = data.get("receiver_id")
    
    async with async_session() as session:
        from app.modules.users.models import User
        user = await session.get(User, message.from_user.id)
        from app.core.permissions import UXControlLayer
        is_allowed, reason = UXControlLayer.check_global_action_block(user)
        if not is_allowed:
            await message.answer(reason)
            await state.clear()
            return
            
        if user:
            from app.modules.moderation.services import ModerationService
            mod_service = ModerationService(session)
            if mod_service.check_text_toxicity(message.text):
                user.risk_score += 10

        service = AnonymousMessageService(session)
        notif_service = NotificationService(bot)
        
        from app.modules.analytics.services import AnalyticsService
        analytics = AnalyticsService(session)
        await analytics.track_event(message.from_user.id, "message_sent")
        
        msg_obj = await service.send_anonymous_message(
            receiver_id=receiver_id,
            content=message.text,
            sender_id=message.from_user.id
        )
        
        await notif_service.notify_new_anonymous_message(receiver_id, str(msg_obj.id), message.text)
        await message.answer(UzbekTexts.MSG_SENT_SUCCESS)
        await state.clear()

@router.callback_query(F.data.startswith("anon_reply_"))
async def handle_anon_reply_cb(call: types.CallbackQuery, state: FSMContext):
    msg_id = call.data.replace("anon_reply_", "")
    await state.set_state(AnonymousStates.waiting_for_reply)
    await state.update_data(reply_to_msg_id=msg_id)
    await call.message.answer(UzbekTexts.REPLY_PROMPT)
    await call.answer()

@router.message(AnonymousStates.waiting_for_reply)
async def process_anon_reply(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    msg_id = data.get("reply_to_msg_id")
    
    async with async_session() as session:
        service = AnonymousMessageService(session)
        notif_service = NotificationService(bot)
        
        orig_msg = await service.get_message(msg_id)
        if orig_msg and orig_msg.sender_id:
            await notif_service.notify_reply_message(orig_msg.sender_id, message.text)
            await message.answer(UzbekTexts.REPLY_SENT)
        else:
            await message.answer("Siz bu anonim xabarga javob yoza olmaysiz. Jo'natuvchi noma'lum.")
    await state.clear()

@router.callback_query(F.data.startswith("anon_report_"))
async def handle_anon_report_cb(call: types.CallbackQuery, state: FSMContext):
    msg_id = call.data.replace("anon_report_", "")
    await state.set_state(AnonymousStates.waiting_for_report)
    await state.update_data(report_msg_id=msg_id)
    await call.message.answer(UzbekTexts.REPORT_PROMPT)
    await call.answer()

@router.message(AnonymousStates.waiting_for_report)
async def process_anon_report(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("report_msg_id")
    
    async with async_session() as session:
        service = AnonymousMessageService(session)
        orig_msg = await service.get_message(msg_id)
        if orig_msg:
            from app.modules.moderation.services import ModerationService
            mod = ModerationService(session)
            import uuid
            
            try:
                m_id = uuid.UUID(msg_id)
            except:
                m_id = orig_msg.id
                
            await mod.submit_report(m_id, orig_msg.receiver_id, orig_msg.sender_id, message.text)
            
            from app.modules.analytics.services import AnalyticsService
            analytics = AnalyticsService(session)
            await analytics.track_event(message.from_user.id, "report_sent")
            
        await service.report_message(msg_id, message.text)
        
    await message.answer(UzbekTexts.REPORT_SUCCESS)
    await state.clear()
