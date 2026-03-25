from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗺️ Карта"), KeyboardButton(text="⚔️ Бой")],
            [KeyboardButton(text="🎒 Инвентарь"), KeyboardButton(text="🔧 Крафт")],
            [KeyboardButton(text="🏪 Аукцион"), KeyboardButton(text="📜 Квесты")],
            [KeyboardButton(text="🏰 Гильдия"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="🏆 Рейтинг"), KeyboardButton(text="⚙️ Настройки")],
        ],
        resize_keyboard=True,
    )


def settings_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🏆 Достижения")],
            [KeyboardButton(text="📬 Почта"), KeyboardButton(text="💬 Чат")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )


def back_to_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Главное меню")]],
        resize_keyboard=True,
    )
