from __future__ import annotations

from typing import Any


CHAT_CHANNELS = {
    "global": {"name": "Мировой чат", "emoji": "🌍"},
    "trade": {"name": "Торговый чат", "emoji": "💰"},
    "guild": {"name": "Гильдейский чат", "emoji": "🏰"},
    "local": {"name": "Локальный чат", "emoji": "🏝️"},
}


def format_chat_message(msg: Any) -> str:
    channel_info = CHAT_CHANNELS.get(msg.channel, {"emoji": "💬"})
    timestamp = msg.created_at.strftime("%H:%M") if msg.created_at else ""
    return f"{channel_info['emoji']} [{timestamp}] <b>{msg.sender_name}</b>: {msg.content}"


def format_chat_messages(messages: list[Any]) -> str:
    if not messages:
        return "💬 Нет сообщений."
    lines = []
    for msg in messages:
        lines.append(format_chat_message(msg))
    return "\n".join(lines)


def validate_message(content: str) -> tuple[bool, str]:
    if not content or not content.strip():
        return False, "Сообщение не может быть пустым."
    if len(content) > 500:
        return False, "Сообщение слишком длинное (макс. 500 символов)."
    banned_words: list[str] = []
    for word in banned_words:
        if word.lower() in content.lower():
            return False, "Сообщение содержит запрещённые слова."
    return True, ""


def get_channel_name(channel: str) -> str:
    return CHAT_CHANNELS.get(channel, {}).get("name", channel)
