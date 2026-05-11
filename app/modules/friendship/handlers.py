from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.texts import UzbekTexts
from app.modules.friendship.services import FriendshipService
from app.database.session import async_session

router = Router()

class FriendshipStates(StatesGroup):
    answering_questions = State()
    participant_answering = State()

@router.message(F.text == "📝 Do'stlik testi")
async def start_friendship_test(message: types.Message, state: FSMContext):
    async with async_session() as session:
        service = FriendshipService(session)
        questions = await service.get_questions()
        
        if not questions:
            await message.answer("Hozircha savollar mavjud emas. 😔")
            return
            
        await state.set_state(FriendshipStates.answering_questions)
        await state.update_data(
            questions=[{"id": q.id, "text": q.text, "options": q.options} for q in questions],
            current_idx=0,
            answers={}
        )
        
        q = questions[0]
        kb = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=opt)] for opt in q.options],
            resize_keyboard=True
        )
        await message.answer(f"1-savol: {q.text}", reply_markup=kb)

@router.message(FriendshipStates.answering_questions)
async def process_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions")
    idx = data.get("current_idx")
    answers = data.get("answers")
    
    current_q = questions[idx]
    try:
        ans_idx = current_q["options"].index(message.text)
    except ValueError:
        await message.answer("Iltimos, tugmalardan birini tanlang.")
        return
        
    answers[current_q["id"]] = ans_idx
    
    if idx + 1 < len(questions):
        next_idx = idx + 1
        next_q = questions[next_idx]
        await state.update_data(current_idx=next_idx, answers=answers)
        
        kb = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=opt)] for opt in next_q["options"]],
            resize_keyboard=True
        )
        await message.answer(f"{next_idx + 1}-savol: {next_q['text']}", reply_markup=kb)
    else:
        # Finish test creation
        async with async_session() as session:
            service = FriendshipService(session)
            test = await service.create_test(message.from_user.id, answers)
            
            bot_info = await message.bot.get_me()
            link = f"https://t.me/{bot_info.username}?start=friend_{message.from_user.id}"
            from app.bot.keyboards import get_main_keyboard
            await message.answer(UzbekTexts.FRIENDSHIP_LINK.format(link=link), reply_markup=get_main_keyboard())
            await state.clear()

async def handle_friend_start(message: types.Message, owner_id: int, state: FSMContext):
    if owner_id == message.from_user.id:
        await message.answer("O'zingizning testingizni yecha olmaysiz! 😅")
        return
        
    async with async_session() as session:
        service = FriendshipService(session)
        # Rate Limiting
        actions = await service.get_participant_action_count(message.from_user.id)
        if actions >= 10:
            await message.answer("Siz 1 soatlik limitdan (10ta test) o'tdingiz. Iltimos, keyinroq urining.")
            return
            
        test = await service.get_active_test_by_owner(owner_id)
        if not test:
            await message.answer("Bu foydalanuvchi hozircha test yaratmagan yoki uning testi faol emas.")
            return
            
        questions = await service.get_questions()
        if not questions:
            return
            
        await state.set_state(FriendshipStates.participant_answering)
        await state.update_data(
            test_id=str(test.id),
            owner_id=owner_id,
            questions=[{"id": q.id, "text": q.text, "options": q.options} for q in questions],
            current_idx=0,
            answers={}
        )
        
        q = questions[0]
        kb = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=opt)] for opt in q.options],
            resize_keyboard=True
        )
        await message.answer(UzbekTexts.FRIENDSHIP_START)
        await message.answer(f"1-savol: {q.text}", reply_markup=kb)

@router.message(FriendshipStates.participant_answering)
async def process_participant_question(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    questions = data.get("questions")
    idx = data.get("current_idx")
    answers = data.get("answers")
    
    current_q = questions[idx]
    try:
        ans_idx = current_q["options"].index(message.text)
    except ValueError:
        await message.answer("Iltimos, tugmalardan birini tanlang.")
        return
        
    answers[str(current_q["id"])] = ans_idx
    
    if idx + 1 < len(questions):
        next_idx = idx + 1
        next_q = questions[next_idx]
        await state.update_data(current_idx=next_idx, answers=answers)
        
        kb = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=opt)] for opt in next_q["options"]],
            resize_keyboard=True
        )
        await message.answer(f"{next_idx + 1}-savol: {next_q['text']}", reply_markup=kb)
    else:
        async with async_session() as session:
            service = FriendshipService(session)
            from uuid import UUID
            test_id = UUID(data.get("test_id"))
            result = await service.submit_result(test_id, message.from_user.id, answers)
            
            # Send result to participant
            from app.bot.keyboards import get_main_keyboard
            score_text = UzbekTexts.FRIENDSHIP_RESULT.format(score=result.score)
            await message.answer(score_text, reply_markup=get_main_keyboard())
            
            # Notify owner
            owner_text = f"Kimdir do'stlik testingizni eson-omon tugatdi!\nNatija: {result.score}% 🏆"
            owner_id = data.get("owner_id")
            from app.services.notifications import NotificationService
            notif = NotificationService(bot)
            await notif.send_message(owner_id, owner_text)
            
        await state.clear()
