from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session
from app.modules.inbox.services import InboxService
from app.core.texts import UzbekTexts

router = Router()

@router.message(F.text == "💬 So'zlashuvlar")
async def show_inbox_menu(message: types.Message):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📩 Anonim xabarlar", callback_data="inbox_anon_0")],
            [types.InlineKeyboardButton(text="📝 Do'stlik natijalari", callback_data="inbox_friend_0")],
            [types.InlineKeyboardButton(text="📊 So'rovnoma natijalari", callback_data="inbox_poll_0")]
        ]
    )
    await message.answer("Sizning faollik tarixingiz: Quyidagilardan birini tanlang 👇", reply_markup=kb)

def format_time_ago(dt) -> str:
    from datetime import datetime
    import pytz
    now = datetime.now(pytz.utc)
    # the db times are naive or utc. Let's assume naive utc.
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return "hoziroq"
    elif seconds < 3600:
        return f"{int(seconds/60)} daqiqa oldin"
    elif seconds < 86400:
        return f"{int(seconds/3600)} soat oldin"
    else:
        return f"{int(seconds/86400)} kun oldin"

@router.callback_query(F.data.startswith("inbox_anon_"))
async def show_anon_history(callback: types.CallbackQuery):
    offset = int(callback.data.replace("inbox_anon_", ""))
    async with async_session() as session:
        service = InboxService(session)
        msgs = await service.get_anonymous_messages(callback.from_user.id, limit=5, offset=offset)
        
        if not msgs and offset == 0:
            await callback.message.edit_text("😕 Hozircha sizda anonim xabarlar mavjud emas.")
            return
        elif not msgs:
            await callback.answer("Boshqa xabar yo'q.", show_alert=True)
            return

        has_unread = False
        msgs.reverse() # Fix chronological order physically in UI
        for idx_rev, m in enumerate(msgs):
            idx = len(msgs) - 1 - idx_rev
            unread_marker = "🔴 Yangi\n" if not getattr(m, 'is_read', True) else ""
            if not getattr(m, 'is_read', True):
                m.is_read = True
                has_unread = True
                
            text = f"📩 Anonim xabar #{offset + idx + 1}\n{unread_marker}\"{m.content}\"\n\n🕒 {format_time_ago(m.created_at)}"
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text=UzbekTexts.ANON_REPLY_BTN, callback_data=f"anon_reply_{m.id}"),
                        types.InlineKeyboardButton(text=UzbekTexts.ANON_REPORT_BTN, callback_data=f"anon_report_{m.id}")
                    ]
                ]
            )
            await callback.message.answer(text, reply_markup=kb)

        if has_unread:
            await session.commit()

        # Pagination controls
        if len(msgs) == 5:
            nav_kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Keyingilari ➡️", callback_data=f"inbox_anon_{offset+5}")]
            ])
            await callback.message.answer("Ko'proq xabarlar:", reply_markup=nav_kb)

        await callback.answer()

@router.callback_query(F.data.startswith("inbox_friend_"))
async def show_friend_history(callback: types.CallbackQuery):
    offset = int(callback.data.replace("inbox_friend_", ""))
    async with async_session() as session:
        service = InboxService(session)
        results = await service.get_friendship_results(callback.from_user.id, limit=5, offset=offset)
        
        if not results and offset == 0:
            await callback.message.edit_text("😕 Hozircha do'stlik natijalari mavjud emas.")
            return
            
        lines = ["📝 Do'stlik Testi Natijalari:\n"]
        has_unread = False
        results.reverse()
        for res, user in results:
            unread_marker = "🔴 Yangi " if not getattr(res, 'is_read', True) else ""
            if not getattr(res, 'is_read', True):
                res.is_read = True
                has_unread = True
            lines.append(f"{unread_marker}👤 {user.full_name} — {res.score}/100 😎 ({format_time_ago(res.created_at)})")
            
        text = "\n".join(lines)
        if has_unread:
            await session.commit()
        
        nav_kb = None
        if len(results) == 5:
            nav_kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Keyingilari ➡️", callback_data=f"inbox_friend_{offset+5}")]
            ])
            
        if offset == 0:
            await callback.message.edit_text(text, reply_markup=nav_kb)
        else:
            await callback.message.answer(text, reply_markup=nav_kb)
            await callback.answer()

@router.callback_query(F.data.startswith("inbox_poll_"))
async def show_poll_history(callback: types.CallbackQuery):
    offset = int(callback.data.replace("inbox_poll_", ""))
    async with async_session() as session:
        service = InboxService(session)
        polls = await service.get_poll_results(callback.from_user.id, limit=5, offset=offset)
        
        if not polls and offset == 0:
            await callback.message.edit_text("😕 Hozircha so'rovnomalar mavjud emas.")
            return
            
        has_unread = False
        polls.reverse()
        for p in polls:
            q_text = p.template.question_text if p.template else "Maxsus so'rov"
            
            # Aggregate answers
            answers_count = len(p.answers)
            most_selected = "Yo'q"
            unread_count = 0
            from collections import Counter
            if answers_count > 0:
                counts = Counter([a.answer_text for a in p.answers])
                most_selected, _ = counts.most_common(1)[0]
                for a in p.answers:
                    if not getattr(a, 'is_read', True):
                        unread_count += 1
                        a.is_read = True
                        has_unread = True
                        
            unread_marker = f"🔴 {unread_count} ta yangi " if unread_count > 0 else ""
            text = f"📊 \"{q_text}\"\n{unread_marker}({answers_count} ta javob)\n\nEng ko'p tanlangan: \"{most_selected}\""
            await callback.message.answer(text)
            
        if has_unread:
            await session.commit()
            
        if len(polls) == 5:
            nav_kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Keyingilari ➡️", callback_data=f"inbox_poll_{offset+5}")]
            ])
            await callback.message.answer("Ko'proq so'rovnomalar:", reply_markup=nav_kb)
            
        await callback.answer()
