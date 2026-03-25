from __future__ import annotations

from typing import Any, Optional


DIPLOMACY_STATES = {
    "war": {"name": "Война", "emoji": "⚔️", "trade_allowed": False, "attack_allowed": True},
    "hostile": {"name": "Враждебность", "emoji": "😠", "trade_allowed": False, "attack_allowed": True},
    "neutral": {"name": "Нейтралитет", "emoji": "😐", "trade_allowed": True, "attack_allowed": True},
    "friendly": {"name": "Дружба", "emoji": "😊", "trade_allowed": True, "attack_allowed": False},
    "allied": {"name": "Альянс", "emoji": "🤝", "trade_allowed": True, "attack_allowed": False},
}


def get_guild_relations(guild: Any) -> dict[str, str]:
    return guild.diplomacy if guild.diplomacy else {}


def set_relation(guild1: Any, guild2_id: int, state: str) -> Optional[str]:
    if state not in DIPLOMACY_STATES:
        return "Неверное дипломатическое состояние."
    relations: dict = guild1.diplomacy if guild1.diplomacy else {}
    relations[str(guild2_id)] = state
    guild1.diplomacy = relations
    return None


def can_attack_guild(guild1: Any, guild2_id: int) -> bool:
    relations = get_guild_relations(guild1)
    state = relations.get(str(guild2_id), "neutral")
    return DIPLOMACY_STATES.get(state, {}).get("attack_allowed", True)


def can_trade_guild(guild1: Any, guild2_id: int) -> bool:
    relations = get_guild_relations(guild1)
    state = relations.get(str(guild2_id), "neutral")
    return DIPLOMACY_STATES.get(state, {}).get("trade_allowed", True)


def declare_war(guild1: Any, guild2: Any) -> str:
    set_relation(guild1, guild2.id, "war")
    set_relation(guild2, guild1.id, "war")
    return f"⚔️ {guild1.name} объявила войну {guild2.name}!"


def propose_peace(guild1: Any, guild2: Any) -> str:
    set_relation(guild1, guild2.id, "neutral")
    set_relation(guild2, guild1.id, "neutral")
    return f"🕊️ {guild1.name} и {guild2.name} заключили мир."


def format_diplomacy(guild: Any) -> str:
    relations = get_guild_relations(guild)
    if not relations:
        return "🌐 Нет дипломатических отношений."
    lines = ["🌐 <b>Дипломатия:</b>", ""]
    for gid, state in relations.items():
        state_info = DIPLOMACY_STATES.get(state, DIPLOMACY_STATES["neutral"])
        lines.append(f"  {state_info['emoji']} Гильдия #{gid}: {state_info['name']}")
    return "\n".join(lines)
