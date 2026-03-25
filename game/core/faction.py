from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_FACTIONS: Optional[dict[str, Any]] = None


def _load_factions() -> dict[str, Any]:
    global _FACTIONS
    if _FACTIONS is None:
        with open(DATA_DIR / "factions.json", encoding="utf-8") as f:
            _FACTIONS = json.load(f)
    return _FACTIONS


def get_faction(faction_id: str) -> Optional[dict[str, Any]]:
    return _load_factions().get(faction_id)


def all_factions() -> dict[str, Any]:
    return _load_factions()


def get_rank(faction_id: str, reputation: int) -> str:
    faction = get_faction(faction_id)
    if not faction:
        return "Неизвестно"
    ranks = faction.get("ranks", [])
    current_rank = ranks[0]["name"] if ranks else "Неизвестно"
    for rank in ranks:
        if reputation >= rank["rep"]:
            current_rank = rank["name"]
    return current_rank


def get_next_rank(faction_id: str, reputation: int) -> Optional[dict[str, Any]]:
    faction = get_faction(faction_id)
    if not faction:
        return None
    ranks = faction.get("ranks", [])
    for rank in ranks:
        if reputation < rank["rep"]:
            return rank
    return None


def format_faction_info(faction_id: str) -> str:
    faction = get_faction(faction_id)
    if not faction:
        return "Фракция не найдена."
    lines = [
        f"{faction['emoji']} <b>{faction['name']}</b>",
        f"📝 {faction['description']}",
        "",
        "🏆 <b>Ранги:</b>",
    ]
    for rank in faction.get("ranks", []):
        lines.append(f"  • {rank['name']} ({rank['rep']} репутации)")
    bonuses = faction.get("bonuses", {})
    if bonuses:
        lines.append("")
        lines.append("💪 <b>Бонусы:</b>")
        for key, value in bonuses.items():
            lines.append(f"  • {key}: +{value}")
    return "\n".join(lines)


def format_player_reputation(player: Any) -> str:
    rep = player.faction_reputation or {}
    if not rep:
        return "📊 У вас нет репутации ни с одной фракцией."
    lines = ["📊 <b>Репутация:</b>"]
    for fid, value in rep.items():
        faction = get_faction(fid)
        if faction:
            rank = get_rank(fid, value)
            emoji = faction.get("emoji", "")
            lines.append(f"  {emoji} {faction['name']}: {value} ({rank})")
    return "\n".join(lines)


def change_reputation(player: Any, faction_id: str, amount: int) -> int:
    rep: dict = player.faction_reputation if player.faction_reputation else {}
    current = rep.get(faction_id, 0)
    new_val = max(0, current + amount)
    rep[faction_id] = new_val
    player.faction_reputation = rep

    faction = get_faction(faction_id)
    if faction and amount < 0:
        for ally_id in faction.get("allies", []):
            ally_rep = rep.get(ally_id, 0)
            rep[ally_id] = max(0, ally_rep + amount // 2)
        for enemy_id in faction.get("enemies", []):
            enemy_rep = rep.get(enemy_id, 0)
            rep[enemy_id] = max(0, enemy_rep - amount // 2)
    elif faction and amount > 0:
        for enemy_id in faction.get("enemies", []):
            enemy_rep = rep.get(enemy_id, 0)
            rep[enemy_id] = max(0, enemy_rep - amount // 3)

    player.faction_reputation = rep
    return new_val
