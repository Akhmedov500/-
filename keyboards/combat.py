from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def combat_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗡️ Охота на монстров"), KeyboardButton(text="🐲 Бой с боссом")],
            [KeyboardButton(text="⚔️ PVP Арена"), KeyboardButton(text="⚓ Морской бой")],
            [KeyboardButton(text="📋 Навыки"), KeyboardButton(text="🧪 Зелья")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )


def battle_action_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚔️ Атака"), KeyboardButton(text="🛡 Защита")],
            [KeyboardButton(text="⚡ Навык"), KeyboardButton(text="🧪 Использовать зелье")],
            [KeyboardButton(text="🏃 Бегство")],
        ],
        resize_keyboard=True,
    )


def skill_tree_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚔️ Боевые"), KeyboardButton(text="🛡 Защитные")],
            [KeyboardButton(text="⛵ Мореходные"), KeyboardButton(text="💰 Торговые")],
            [KeyboardButton(text="🏕️ Выживание"), KeyboardButton(text="📋 Мои навыки")],
            [KeyboardButton(text="🔙 К бою")],
        ],
        resize_keyboard=True,
    )
