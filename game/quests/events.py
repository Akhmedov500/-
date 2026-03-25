from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

from game.world.events import get_event_template, get_all_event_templates


def create_world_event(event_id: str) -> Optional[dict[str, Any]]:
    template = get_event_template(event_id)
    if not template:
        return None
    now = datetime.utcnow()
    return {
        "id": event_id,
        "name": template["name"],
        "description": template["description"],
        "type": template["type"],
        "effects": template.get("effects", {}),
        "rewards": template.get("rewards", {}),
        "min_level": template.get("min_level", 1),
        "started_at": now.isoformat(),
        "ends_at": (now + timedelta(hours=template.get("duration_hours", 24))).isoformat(),
        "participants": [],
    }


def join_event(player: Any, event_data: dict[str, Any]) -> Optional[str]:
    if player.level < event_data.get("min_level", 1):
        return f"Требуется уровень {event_data['min_level']}."
    participants: list = event_data.get("participants", [])
    if player.telegram_id in participants:
        return "Вы уже участвуете в этом событии."
    participants.append(player.telegram_id)
    event_data["participants"] = participants
    return None


def is_event_active(event_data: dict[str, Any]) -> bool:
    ends_at = datetime.fromisoformat(event_data["ends_at"])
    return datetime.utcnow() < ends_at


def complete_event_for_player(player: Any, event_data: dict[str, Any]) -> Optional[dict[str, Any]]:
    if player.telegram_id not in event_data.get("participants", []):
        return None
    return event_data.get("rewards")


def get_seasonal_events() -> list[dict[str, Any]]:
    return [e for e in get_all_event_templates() if e["type"] == "seasonal"]


def get_weekly_events() -> list[dict[str, Any]]:
    return [e for e in get_all_event_templates() if e["type"] == "weekly"]


def get_daily_events() -> list[dict[str, Any]]:
    return [e for e in get_all_event_templates() if e["type"] == "daily"]


def format_event_list() -> str:
    events = get_all_event_templates()
    if not events:
        return "🌍 Нет доступных событий."
    lines = ["🌍 <b>Мировые события:</b>", ""]
    by_type: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        t = ev["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(ev)
    type_names = {"seasonal": "🌸 Сезонные", "weekly": "📅 Еженедельные", "daily": "☀️ Ежедневные", "rare": "💎 Редкие"}
    for t, name in type_names.items():
        if t in by_type:
            lines.append(f"<b>{name}:</b>")
            for ev in by_type[t]:
                lines.append(f"  🌟 {ev['name']} (ур. {ev.get('min_level', 1)}+)")
            lines.append("")
    return "\n".join(lines)
