from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Any


def island_travel_kb(islands: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for isl in islands[:10]:
        buttons.append([InlineKeyboardButton(
            text=f"{isl.get('emoji', '🏝️')} {isl['name']} (💰{isl.get('cost', '?')})",
            callback_data=f"travel:{isl['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def boss_select_kb(bosses: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for boss in bosses:
        buttons.append([InlineKeyboardButton(
            text=f"💀 {boss['name']} (ур. {boss['level']})",
            callback_data=f"boss:{boss['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_kb(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm:{action}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel"),
        ]
    ])


def faction_select_kb(factions: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for faction in factions:
        buttons.append([InlineKeyboardButton(
            text=f"{faction.get('emoji', '🏴')} {faction['name']}",
            callback_data=f"faction:{faction['id']}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def ship_select_kb(ships: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for ship in ships:
        buttons.append([InlineKeyboardButton(
            text=f"{ship.get('emoji', '⛵')} {ship['name']} — {ship['price']} 💰",
            callback_data=f"buy_ship:{ship['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def recipe_select_kb(recipes: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for recipe in recipes[:10]:
        buttons.append([InlineKeyboardButton(
            text=f"🔧 {recipe['name']}",
            callback_data=f"craft:{recipe['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def potion_select_kb(potions: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for potion in potions[:10]:
        buttons.append([InlineKeyboardButton(
            text=f"{potion.get('emoji', '🧪')} {potion['name']}",
            callback_data=f"brew:{potion['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def pagination_kb(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    if current_page > 1:
        row.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}:page:{current_page - 1}"))
    row.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop"))
    if current_page < total_pages:
        row.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}:page:{current_page + 1}"))
    buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def quest_choice_kb(choices: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for i, choice in enumerate(choices):
        buttons.append([InlineKeyboardButton(
            text=choice["text"],
            callback_data=f"story_choice:{i}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def skill_select_kb(skills: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for skill in skills[:10]:
        s_type = "🔴" if skill["type"] == "active" else "🔵"
        buttons.append([InlineKeyboardButton(
            text=f"{s_type} {skill['name']} (ур. {skill.get('level_req', 1)})",
            callback_data=f"learn_skill:{skill['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def smuggling_kb(goods: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for i, good in enumerate(goods):
        buttons.append([InlineKeyboardButton(
            text=f"{good.get('emoji', '📦')} {good['name']} — {good['reward']} 💰",
            callback_data=f"smuggle:{i}",
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def trade_route_kb(routes: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons = []
    for route in routes:
        buttons.append([InlineKeyboardButton(
            text=f"🚢 {route['name']}",
            callback_data=f"trade_route:{route['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
