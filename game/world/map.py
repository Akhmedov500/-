from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_ISLANDS: Optional[dict[str, Any]] = None


def _load_islands() -> dict[str, Any]:
    global _ISLANDS
    if _ISLANDS is None:
        with open(DATA_DIR / "islands.json", encoding="utf-8") as f:
            _ISLANDS = json.load(f)
    return _ISLANDS


def get_island(island_id: str) -> Optional[dict[str, Any]]:
    return _load_islands().get(island_id)


def all_islands() -> dict[str, Any]:
    return _load_islands()


def get_connected_islands(island_id: str) -> list[str]:
    island = get_island(island_id)
    if not island:
        return []
    return island.get("connected_islands", [])


def get_distance(from_id: str, to_id: str) -> float:
    a = get_island(from_id)
    b = get_island(to_id)
    if not a or not b:
        return float("inf")
    dx = a["x"] - b["x"]
    dy = a["y"] - b["y"]
    return math.sqrt(dx * dx + dy * dy)


def get_travel_cost(from_id: str, to_id: str, ship_speed: int = 10) -> int:
    dist = get_distance(from_id, to_id)
    base_cost = max(1, int(dist / 5))
    speed_factor = max(0.5, 1.0 - (ship_speed - 10) * 0.03)
    return max(1, int(base_cost * speed_factor))


def can_travel(player: Any, to_id: str) -> Optional[str]:
    island = get_island(to_id)
    if not island:
        return "Остров не найден."
    if player.level < island.get("level_req", 1):
        return f"Требуется уровень {island['level_req']}."
    connected = get_connected_islands(player.current_island)
    if to_id not in connected:
        return "Этот остров недоступен напрямую. Найдите путь через другие острова."
    cost = get_travel_cost(player.current_island, to_id)
    if player.energy < cost:
        return f"Недостаточно энергии. Нужно: {cost}, у вас: {player.energy}."
    return None


def format_island_info(island_id: str) -> str:
    island = get_island(island_id)
    if not island:
        return "Остров не найден."

    type_emoji = {
        "city": "🏙️", "outpost": "🏕️", "wild": "🌴",
        "haunted": "👻", "fortress": "🏰", "resource": "⛏️",
        "dungeon": "🏚️", "raid": "💀", "special": "✨",
    }
    emoji = type_emoji.get(island["type"], "🏝️")

    lines = [
        f"{emoji} <b>{island['name']}</b>",
        f"📝 {island['description']}",
        f"📊 Мин. уровень: {island['level_req']}  |  Регион: {island['region']}",
    ]

    if island.get("faction"):
        lines.append(f"⚓ Фракция: {island['faction']}")

    resources = island.get("resources", [])
    if resources:
        lines.append(f"⛏️ Ресурсы: {', '.join(resources)}")

    shops = island.get("shops", [])
    if shops:
        lines.append(f"🏪 Магазины: {', '.join(shops)}")

    monsters = island.get("monsters", [])
    if monsters:
        lines.append(f"👹 Монстры: {', '.join(monsters)}")

    if island.get("boss"):
        lines.append(f"🐲 Босс: {island['boss']}")

    connected = island.get("connected_islands", [])
    if connected:
        names = []
        for cid in connected:
            ci = get_island(cid)
            names.append(ci["name"] if ci else cid)
        lines.append(f"🗺️ Пути: {', '.join(names)}")

    return "\n".join(lines)


def format_navigation(player: Any) -> str:
    current = get_island(player.current_island)
    if not current:
        return "Вы потерялись в море!"
    lines = [format_island_info(player.current_island), "", "🧭 <b>Доступные направления:</b>"]
    connected = get_connected_islands(player.current_island)
    for cid in connected:
        ci = get_island(cid)
        if ci:
            cost = get_travel_cost(player.current_island, cid)
            level_ok = "✅" if player.level >= ci.get("level_req", 1) else "❌"
            lines.append(f"  {level_ok} {ci['name']} (ур. {ci['level_req']}) — ⚡{cost}")
    return "\n".join(lines)
