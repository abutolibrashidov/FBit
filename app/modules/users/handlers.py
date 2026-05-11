from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import async_session
from app.modules.users.models import User

router = Router()

def build_settings_kb(user: User):
    anon_text = "🟢 Yoqilgan" if user.allow_anonymous_messages else "🔴 O'chirilgan"
    friend_text = "🟢 Yoqilgan" if user.allow_friend_requests else "🔴 O'chirilgan"
    poll_text = "🟢 Yoqilgan" if user.allow_polls else "🔴 O'chirilgan"
    risk_text = "🟢 Ko'rsatish" if getattr(user, 'show_risk_status', True) else "🔴 Yashirish"
    
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f"Qabul qilish (Anonim): {anon_text}", callback_data="toggle_anon")],
            [types.InlineKeyboardButton(text=f"Qabul qilish (Do'stlik): {friend_text}", callback_data="toggle_friend")],
            [types.InlineKeyboardButton(text=f"Qabul qilish (So'rovnoma): {poll_text}", callback_data="toggle_poll")],
            [types.InlineKeyboardButton(text=f"Risk statusni ko'rsatish: {risk_text}", callback_data="toggle_risk")],
        ]
    )

@router.message(F.text == "⚙️ Sozlamalar")
async def show_settings_menu(message: types.Message):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            return
            
        risk_status = ""
        if getattr(user, 'show_risk_status', True):
            risk_status = f"\n\n🛡 Xavfsizlik statusi (Risk Score): {getattr(user, 'risk_score', 0)}"
            
        text = f"⚙️ *Shaxsiy Sozlamalar*\n\nProfil sozlamalari orqali akkauntingiz xavfsizligini nazorat qiling.{risk_status}"
        await message.answer(text, reply_markup=build_settings_kb(user), parse_mode="Markdown")

@router.callback_query(F.data.startswith("toggle_"))
async def handle_toggle(callback: types.CallbackQuery):
    action = callback.data.replace("toggle_", "")
    
    async with async_session() as session:
        user = await session.get(User, callback.from_user.id)
        if not user:
            return
            
        if action == "anon":
            user.allow_anonymous_messages = not getattr(user, 'allow_anonymous_messages', True)
        elif action == "friend":
            user.allow_friend_requests = not getattr(user, 'allow_friend_requests', True)
        elif action == "poll":
            user.allow_polls = not getattr(user, 'allow_polls', True)
        elif action == "risk":
            user.show_risk_status = not getattr(user, 'show_risk_status', True)
            
        await session.commit()
        await session.refresh(user)
        
        risk_status = ""
        if getattr(user, 'show_risk_status', True):
            risk_status = f"\n\n🛡 Xavfsizlik statusi (Risk Score): {getattr(user, 'risk_score', 0)}"
            
        text = f"⚙️ *Shaxsiy Sozlamalar*\n\nProfil sozlamalari orqali akkauntingiz xavfsizligini nazorat qiling.{risk_status}"
        
        try:
            await callback.message.edit_text(text, reply_markup=build_settings_kb(user), parse_mode="Markdown")
        except:
            pass # Message not modified error
        
        await callback.answer("Sozlamalar saqlandi ✅")
