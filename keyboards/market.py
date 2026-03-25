from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def market_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Просмотр лотов"), KeyboardButton(text="📤 Выставить на продажу")],
            [KeyboardButton(text="📋 Мои лоты"), KeyboardButton(text="💰 Торговые товары")],
            [KeyboardButton(text="🚢 Маршруты"), KeyboardButton(text="📊 Экономика")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )
