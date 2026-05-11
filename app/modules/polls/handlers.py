from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.texts import UzbekTexts
from app.modules.polls.services import PollService
from app.database.session import async_session

router = Router()

class PollStates(StatesGroup):
    choosing_template = State()
    answering_poll = State()

@router.message(F.text == "📊 Anonim so'rovnomalar")
async def show_poll_menu(message: types.Message):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🔥 Qiziqarli", callback_data="poll_cat_Fun")],
            [types.InlineKeyboardButton(text="🧠 Xarakter", callback_data="poll_cat_Personality")],
            [types.InlineKeyboardButton(text="🏫 Maktab", callback_data="poll_cat_School")],
            [types.InlineKeyboardButton(text="💫 Kelajak", callback_data="poll_cat_Future")]
        ]
    )
    await message.answer("So'rovnoma kategoriyasini tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("poll_cat_"))
async def show_poll_category(callback: types.CallbackQuery):
    cat = callback.data.replace("poll_cat_", "")
    async with async_session() as session:
        service = PollService(session)
        templates = await service.get_templates(category=cat)
        
        if not templates:
            await callback.message.edit_text("😕 Hozircha bu bo'lim uchun so'rovnomalar mavjud emas.")
            return
            
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=t.question_text, callback_data=f"poll_tpl_{t.id}")]
                for t in templates
            ]
        )
        await callback.message.edit_text(UzbekTexts.POLL_CREATE, reply_markup=kb)

@router.callback_query(F.data.startswith("poll_tpl_"))
async def create_tpl_poll(callback: types.CallbackQuery):
    tpl_id = int(callback.data.replace("poll_tpl_", ""))
    async with async_session() as session:
        service = PollService(session)
        poll = await service.create_poll(callback.from_user.id, template_id=tpl_id)
        
        bot_info = await callback.bot.get_me()
        link = f"https://t.me/{bot_info.username}?start=poll_{poll.id}"
        await callback.message.edit_text(UzbekTexts.POLL_SENT + f"\n\nHavola: `{link}`")
        await callback.answer()

async def handle_poll_start(message: types.Message, poll_id: str, state: FSMContext):
    async with async_session() as session:
        service = PollService(session)
        import uuid
        try:
            p_id = uuid.UUID(poll_id)
        except ValueError:
            return
            
        poll = await service.get_poll(p_id)
        if not poll or not poll.is_active:
            await message.answer("Ushbu so'rovnoma mavjud emas yoki yakunlangan.")
            return
            
        if poll.owner_id == message.from_user.id:
            await message.answer("O'zingizning so'rovnomangizga javob bera olmaysiz! 😅")
            return
            
        question_text = poll.template.question_text if poll.template else poll.custom_question
        
        await state.set_state(PollStates.answering_poll)
        await state.update_data(poll_id=poll_id, owner_id=poll.owner_id, question_text=question_text)
        
        await message.answer(f"Ushbu anonim so'rovnomaga javob bering:\n\n💬 {question_text}")

@router.message(PollStates.answering_poll)
async def process_poll_answer(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    poll_id_str = data.get("poll_id")
    owner_id = data.get("owner_id")
    question_text = data.get("question_text")
    
    async with async_session() as session:
        service = PollService(session)
        import uuid
        await service.submit_answer(uuid.UUID(poll_id_str), message.text, message.from_user.id)
        
        from app.bot.keyboards import get_main_keyboard
        await message.answer("Sizning javobingiz qabul qilindi, rahmat! ✅", reply_markup=get_main_keyboard())
        
        from app.services.notifications import NotificationService
        notif = NotificationService(bot)
        owner_msg = f"Sizning \"{question_text}\" so'rovnomangizga yangi anonim javob keldi:\n\n💬 {message.text}"
        await notif.send_message(owner_id, owner_msg)
        
    await state.clear()
