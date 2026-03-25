from __future__ import annotations

from typing import Optional

import config


def validate_display_name(name: str) -> Optional[str]:
    if not name or len(name.strip()) < 2:
        return "Имя должно быть не менее 2 символов."
    if len(name) > 20:
        return "Имя должно быть не более 20 символов."
    if not all(c.isalnum() or c in " _-" for c in name):
        return "Имя может содержать только буквы, цифры, пробелы, _ и -."
    return None


def validate_guild_name(name: str) -> Optional[str]:
    if not name or len(name.strip()) < 3:
        return "Название гильдии должно быть не менее 3 символов."
    if len(name) > 30:
        return "Название гильдии должно быть не более 30 символов."
    return None


def validate_price(price: int) -> Optional[str]:
    if price < 1:
        return "Цена должна быть положительной."
    if price > 1_000_000:
        return "Цена не может превышать 1 000 000."
    return None


def validate_quantity(qty: int) -> Optional[str]:
    if qty < 1:
        return "Количество должно быть положительным."
    if qty > 9999:
        return "Количество не может превышать 9999."
    return None


def validate_level(level: int) -> bool:
    return 1 <= level <= config.MAX_LEVEL


def validate_energy(energy: int) -> bool:
    return 0 <= energy <= config.MAX_ENERGY


def validate_message_content(content: str) -> Optional[str]:
    if not content or not content.strip():
        return "Сообщение не может быть пустым."
    if len(content) > 500:
        return "Сообщение слишком длинное (макс. 500 символов)."
    return None
