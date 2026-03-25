from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def crafting_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚔️ Оружие"), KeyboardButton(text="🛡 Броня")],
            [KeyboardButton(text="🧪 Алхимия"), KeyboardButton(text="📦 Материалы")],
            [KeyboardButton(text="🔧 Улучшения корабля"), KeyboardButton(text="🍖 Еда")],
            [KeyboardButton(text="🎒 Инвентарь"), KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )


def inventory_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Все предметы"), KeyboardButton(text="⚔️ Экипировка")],
            [KeyboardButton(text="🧪 Зелья"), KeyboardButton(text="⛏️ Ресурсы")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )
