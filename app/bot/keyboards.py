from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🤫 Anonim xabar havolasi"), KeyboardButton(text="📝 Do'stlik testi")],
            [KeyboardButton(text="📊 Anonim so'rovnomalar"), KeyboardButton(text="💬 So'zlashuvlar")],
            [KeyboardButton(text="⚙️ Sozlamalar")]
        ],
        resize_keyboard=True
    )

def get_settings_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 Tilni o'zgartirish", callback_data="set_lang")],
            [InlineKeyboardButton(text="🔔 Bildirishnomalar", callback_data="set_notif")]
        ]
    )
