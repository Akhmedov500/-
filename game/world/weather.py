from __future__ import annotations

import random
from datetime import datetime
from typing import Any

import config

WEATHER_TYPES: dict[str, dict[str, Any]] = {
    "clear": {
        "name": "Ясно",
        "emoji": "☀️",
        "description": "Прекрасная погода для плавания!",
        "effects": {},
    },
    "cloudy": {
        "name": "Облачно",
        "emoji": "⛅",
        "description": "Небо затянуто облаками.",
        "effects": {"speed_modifier": -0.05},
    },
    "rain": {
        "name": "Дождь",
        "emoji": "🌧️",
        "description": "Дождь затрудняет навигацию.",
        "effects": {"speed_modifier": -0.1, "accuracy_modifier": -0.05},
    },
    "storm": {
        "name": "Шторм",
        "emoji": "⛈️",
        "description": "Опасный шторм! Будьте осторожны!",
        "effects": {"speed_modifier": -0.3, "accuracy_modifier": -0.15, "damage_modifier": 0.1, "ship_damage_chance": 0.2},
    },
    "fog": {
        "name": "Туман",
        "emoji": "🌫️",
        "description": "Густой туман скрывает всё вокруг.",
        "effects": {"speed_modifier": -0.2, "dodge_bonus": 0.1, "encounter_chance": 0.15},
    },
    "wind": {
        "name": "Сильный ветер",
        "emoji": "💨",
        "description": "Попутный ветер ускоряет корабль!",
        "effects": {"speed_modifier": 0.2},
    },
    "calm": {
        "name": "Штиль",
        "emoji": "🌊",
        "description": "Море спокойно. Паруса не наполняются ветром.",
        "effects": {"speed_modifier": -0.4, "fishing_bonus": 0.2},
    },
    "hurricane": {
        "name": "Ураган",
        "emoji": "🌀",
        "description": "УРАГАН! Экстремально опасно!",
        "effects": {"speed_modifier": -0.5, "accuracy_modifier": -0.3, "ship_damage_chance": 0.5, "xp_bonus": 0.5},
    },
}

_current_weather: dict[str, str] = {}
_last_weather_change: dict[str, datetime] = {}


def get_weather(region: str = "caribbean") -> str:
    now = datetime.utcnow()
    last_change = _last_weather_change.get(region)
    if last_change is None or (now - last_change).total_seconds() > config.WEATHER_CHANGE_HOURS * 3600:
        _current_weather[region] = _generate_weather()
        _last_weather_change[region] = now
    return _current_weather.get(region, "clear")


def _generate_weather() -> str:
    weights = {
        "clear": 30,
        "cloudy": 20,
        "rain": 15,
        "storm": 8,
        "fog": 10,
        "wind": 12,
        "calm": 8,
        "hurricane": 2,
    }
    options = list(weights.keys())
    probs = list(weights.values())
    return random.choices(options, weights=probs, k=1)[0]


def get_weather_info(region: str = "caribbean") -> dict[str, Any]:
    weather_id = get_weather(region)
    return WEATHER_TYPES.get(weather_id, WEATHER_TYPES["clear"])


def format_weather(region: str = "caribbean") -> str:
    info = get_weather_info(region)
    lines = [
        f"{info['emoji']} <b>Погода: {info['name']}</b>",
        f"📝 {info['description']}",
    ]
    effects = info.get("effects", {})
    if effects:
        lines.append("⚡ <b>Эффекты:</b>")
        for k, v in effects.items():
            sign = "+" if v > 0 else ""
            lines.append(f"  • {k}: {sign}{v}")
    return "\n".join(lines)


def apply_weather_to_combat(weather_region: str, attacker_stats: dict, defender_stats: dict) -> tuple[dict, dict]:
    info = get_weather_info(weather_region)
    effects = info.get("effects", {})

    accuracy_mod = effects.get("accuracy_modifier", 0)
    damage_mod = effects.get("damage_modifier", 0)

    if accuracy_mod:
        attacker_stats["accuracy"] = attacker_stats.get("accuracy", 1.0) + accuracy_mod
        defender_stats["accuracy"] = defender_stats.get("accuracy", 1.0) + accuracy_mod
    if damage_mod:
        attacker_stats["bonus_damage"] = attacker_stats.get("bonus_damage", 0) + damage_mod
        defender_stats["bonus_damage"] = defender_stats.get("bonus_damage", 0) + damage_mod

    return attacker_stats, defender_stats
