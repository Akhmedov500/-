from __future__ import annotations

from typing import Any, Optional


def create_alliance(name: str, leader_guild_id: int) -> dict[str, Any]:
    return {
        "name": name,
        "leader_guild_id": leader_guild_id,
        "member_guilds": [leader_guild_id],
        "max_guilds": 5,
    }


def can_join_alliance(alliance: dict[str, Any]) -> Optional[str]:
    members = alliance.get("member_guilds", [])
    if len(members) >= alliance.get("max_guilds", 5):
        return "Альянс переполнен."
    return None


def join_alliance(alliance: dict[str, Any], guild_id: int) -> Optional[str]:
    error = can_join_alliance(alliance)
    if error:
        return error
    members: list = alliance.get("member_guilds", [])
    if guild_id in members:
        return "Гильдия уже в альянсе."
    members.append(guild_id)
    alliance["member_guilds"] = members
    return None


def leave_alliance(alliance: dict[str, Any], guild_id: int) -> Optional[str]:
    members: list = alliance.get("member_guilds", [])
    if guild_id not in members:
        return "Гильдия не в этом альянсе."
    if guild_id == alliance.get("leader_guild_id"):
        return "Лидер не может покинуть альянс. Передайте лидерство."
    members.remove(guild_id)
    alliance["member_guilds"] = members
    return None


def format_alliance(alliance: dict[str, Any]) -> str:
    members = alliance.get("member_guilds", [])
    lines = [
        f"🤝 <b>Альянс: {alliance['name']}</b>",
        f"👑 Лидер: Гильдия #{alliance['leader_guild_id']}",
        f"👥 Гильдии: {len(members)}/{alliance.get('max_guilds', 5)}",
    ]
    return "\n".join(lines)
