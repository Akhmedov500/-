from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_EVENTS: Optional[list[dict[str, Any]]] = None


def _load_events() -> list[dict[str, Any]]:
    global _EVENTS
    if _EVENTS is None:
        with open(DATA_DIR / "events.json", encoding="utf-8") as f:
            data = json.load(f)
        _EVENTS = data.get("world_events", [])
    return _EVENTS


def get_all_event_templates() -> list[dict[str, Any]]:
    return _load_events()


def get_event_template(event_id: str) -> Optional[dict[str, Any]]:
    for ev in _load_events():
        if ev["id"] == event_id:
            return ev
    return None


def pick_random_event(player_level: int = 1) -> Optional[dict[str, Any]]:
    templates = [e for e in _load_events() if player_level >= e.get("min_level", 1)]
    if not templates:
        return None
    return random.choice(templates)


def format_event(event: dict[str, Any]) -> str:
    lines = [
        f"🌟 <b>{event['name']}</b>",
        f"📝 {event['description']}",
        f"⏰ Длительность: {event.get('duration_hours', 24)} ч.",
        f"📊 Мин. уровень: {event.get('min_level', 1)}",
    ]
    effects = event.get("effects", {})
    if effects:
        lines.append("⚡ <b>Эффекты:</b>")
        for k, v in effects.items():
            lines.append(f"  • {k}: {v}")
    rewards = event.get("rewards", {})
    if rewards:
        lines.append("🎁 <b>Награды:</b>")
        if "gold" in rewards:
            lines.append(f"  💰 {rewards['gold']} золота")
        if "xp" in rewards:
            lines.append(f"  📊 {rewards['xp']} опыта")
        if "items" in rewards:
            lines.append(f"  📦 {', '.join(rewards['items'])}")
    return "\n".join(lines)


def format_active_events(active_events: list[Any]) -> str:
    if not active_events:
        return "🌍 Сейчас нет активных мировых событий."
    lines = ["🌍 <b>Активные мировые события:</b>", ""]
    for ev in active_events:
        lines.append(f"🌟 <b>{ev.name}</b>")
        lines.append(f"   📝 {ev.description}")
        if ev.ends_at:
            remaining = ev.ends_at - datetime.utcnow()
            hours = int(remaining.total_seconds() / 3600)
            lines.append(f"   ⏰ Осталось: {hours} ч.")
        lines.append("")
    return "\n".join(lines)
