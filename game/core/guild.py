from __future__ import annotations

from typing import Any, Optional



GUILD_LEVEL_XP = [0, 500, 1500, 3000, 6000, 10000, 15000, 25000, 40000, 60000]

GUILD_PERKS: dict[str, dict[str, Any]] = {
    "gold_bonus": {"name": "Золотой бонус", "description": "+5% золота для членов", "cost": 1000, "max_level": 5, "bonus_per_level": 0.05},
    "xp_bonus": {"name": "Бонус опыта", "description": "+5% опыта для членов", "cost": 1500, "max_level": 5, "bonus_per_level": 0.05},
    "member_slots": {"name": "Расширение", "description": "+5 мест в гильдии", "cost": 2000, "max_level": 5, "bonus_per_level": 5},
    "defense_bonus": {"name": "Гильдейская защита", "description": "+3% защиты для членов", "cost": 1200, "max_level": 5, "bonus_per_level": 0.03},
    "attack_bonus": {"name": "Гильдейская атака", "description": "+3% атаки для членов", "cost": 1200, "max_level": 5, "bonus_per_level": 0.03},
    "treasury_capacity": {"name": "Казна", "description": "+10000 к макс. казне", "cost": 3000, "max_level": 5, "bonus_per_level": 10000},
}


def guild_xp_for_level(level: int) -> int:
    if level < len(GUILD_LEVEL_XP):
        return GUILD_LEVEL_XP[level]
    return GUILD_LEVEL_XP[-1] + (level - len(GUILD_LEVEL_XP) + 1) * 20000


def format_guild(guild: Any) -> str:
    members_count = len(guild.members) if guild.members else 0
    lines = [
        f"🏰 <b>[{guild.tag}] {guild.name}</b>",
        f"📊 Уровень: {guild.level}  |  XP: {guild.xp}/{guild_xp_for_level(guild.level + 1)}",
        f"👥 Участники: {members_count}/{guild.max_members}",
        f"💰 Казна: {guild.gold} золота",
        f"📝 {guild.description}" if guild.description else "",
    ]
    territory = guild.territory or []
    if territory:
        lines.append(f"🗺️ Территории: {len(territory)}")
    perks = guild.perks or {}
    if perks:
        lines.append("")
        lines.append("⚡ <b>Перки:</b>")
        for perk_id, lvl in perks.items():
            perk_info = GUILD_PERKS.get(perk_id)
            if perk_info:
                lines.append(f"  • {perk_info['name']} (ур. {lvl})")
    return "\n".join([line for line in lines if line])


def format_guild_members(guild: Any) -> str:
    members = guild.members or []
    if not members:
        return "👥 В гильдии нет участников."
    lines = ["👥 <b>Участники гильдии:</b>"]
    for member in members:
        role = "👑 Лидер" if member.telegram_id == guild.leader_id else "⚔️ Член"
        lines.append(f"  {role} {member.display_name} (ур. {member.level})")
    return "\n".join(lines)


def can_join_guild(guild: Any) -> Optional[str]:
    members_count = len(guild.members) if guild.members else 0
    if members_count >= guild.max_members:
        return "Гильдия переполнена."
    return None


def get_guild_bonus(guild: Any, bonus_type: str) -> float:
    perks: dict = guild.perks if guild.perks else {}
    perk_info = GUILD_PERKS.get(bonus_type)
    if not perk_info:
        return 0.0
    level = perks.get(bonus_type, 0)
    return level * perk_info["bonus_per_level"]


def upgrade_perk(guild: Any, perk_id: str) -> Optional[str]:
    perk_info = GUILD_PERKS.get(perk_id)
    if not perk_info:
        return "Перк не найден."
    perks: dict = guild.perks if guild.perks else {}
    current_level = perks.get(perk_id, 0)
    if current_level >= perk_info["max_level"]:
        return "Перк уже максимального уровня."
    cost = perk_info["cost"] * (current_level + 1)
    if guild.gold < cost:
        return f"Недостаточно золота в казне. Нужно: {cost}."
    guild.gold -= cost
    perks[perk_id] = current_level + 1
    guild.perks = perks
    return None
