from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def navigation_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏝️ Текущий остров"), KeyboardButton(text="⛵ Плыть")],
            [KeyboardButton(text="🚢 Торговые маршруты"), KeyboardButton(text="🏴‍☠️ Контрабанда")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )


def island_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👀 Осмотреться"), KeyboardButton(text="⛏️ Собрать ресурсы")],
            [KeyboardButton(text="🐲 Боссы"), KeyboardButton(text="👥 NPC")],
            [KeyboardButton(text="🗺️ К навигации"), KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )
