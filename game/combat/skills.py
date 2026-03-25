from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_SKILLS: Optional[dict[str, dict[str, Any]]] = None


def _load_skills() -> dict[str, dict[str, Any]]:
    global _SKILLS
    if _SKILLS is None:
        with open(DATA_DIR / "skills.json", encoding="utf-8") as f:
            raw = json.load(f)
        flat: dict[str, dict[str, Any]] = {}
        for tree in raw.values():
            flat.update(tree)
        _SKILLS = flat
    return _SKILLS


def get_skill(skill_id: str) -> Optional[dict[str, Any]]:
    return _load_skills().get(skill_id)


def all_skills() -> dict[str, dict[str, Any]]:
    return _load_skills()


def get_skill_tree(tree_name: str) -> dict[str, dict[str, Any]]:
    with open(DATA_DIR / "skills.json", encoding="utf-8") as f:
        raw = json.load(f)
    return raw.get(tree_name, {})


def can_learn_skill(player: Any, skill_id: str) -> Optional[str]:
    skill = get_skill(skill_id)
    if not skill:
        return "Навык не найден."
    if player.level < skill.get("level_req", 1):
        return f"Требуется уровень {skill['level_req']}."
    player_skills: dict = player.skills if player.skills else {}
    current_level = player_skills.get(skill_id, 0)
    max_level = skill.get("max_level", 5)
    if current_level >= max_level:
        return "Навык уже максимального уровня."
    # Check skill points
    skill_points = player.skill_points if hasattr(player, "skill_points") and player.skill_points else 0
    cost = skill.get("cost", 1)
    if skill_points < cost:
        return f"Недостаточно очков навыков. Нужно: {cost}, у вас: {skill_points}."
    return None


def learn_skill(player: Any, skill_id: str) -> Optional[str]:
    error = can_learn_skill(player, skill_id)
    if error:
        return error
    skill = get_skill(skill_id)
    if not skill:
        return "Навык не найден."
    player_skills: dict = player.skills if player.skills else {}
    current_level = player_skills.get(skill_id, 0)
    player_skills[skill_id] = current_level + 1
    player.skills = player_skills
    cost = skill.get("cost", 1)
    player.skill_points = (player.skill_points or 0) - cost
    return None


def get_active_skills(player: Any) -> list[dict[str, Any]]:
    player_skills: dict = player.skills if player.skills else {}
    actives = []
    for sid, level in player_skills.items():
        skill = get_skill(sid)
        if skill and skill.get("type") == "active" and level > 0:
            actives.append({**skill, "id": sid, "player_level": level})
    return actives


def get_passive_bonuses(player: Any) -> dict[str, float]:
    player_skills: dict = player.skills if player.skills else {}
    bonuses: dict[str, float] = {}
    for sid, level in player_skills.items():
        skill = get_skill(sid)
        if skill and skill.get("type") == "passive" and level > 0:
            effects = skill.get("effects", {})
            for key, value in effects.items():
                if isinstance(value, (int, float)):
                    per_level = value
                    bonuses[key] = bonuses.get(key, 0) + per_level * level
    return bonuses


def use_active_skill(player: Any, skill_id: str, target_hp: int, target_def: int) -> tuple[int, str]:
    player_skills: dict = player.skills if player.skills else {}
    level = player_skills.get(skill_id, 0)
    if level <= 0:
        return 0, "Вы не изучили этот навык."
    skill = get_skill(skill_id)
    if not skill or skill.get("type") != "active":
        return 0, "Это не активный навык."

    effects = skill.get("effects", {})
    multiplier = effects.get("damage_multiplier", 1.0)
    base_damage = int(player.attack * multiplier * (1 + level * 0.1))
    damage = max(1, base_damage - target_def // 3)

    return damage, f"⚡ {skill['name']} (ур. {level}): {damage} урона!"


def format_skill_tree(tree_name: str) -> str:
    tree = get_skill_tree(tree_name)
    if not tree:
        return "Дерево навыков не найдено."
    tree_emojis = {"combat": "⚔️", "defense": "🛡", "sailing": "⛵", "trade": "💰", "survival": "🏕️"}
    emoji = tree_emojis.get(tree_name, "📋")
    lines = [f"{emoji} <b>Дерево навыков: {tree_name.upper()}</b>", ""]
    for sid, skill in tree.items():
        s_type = "🔴" if skill["type"] == "active" else "🔵"
        lines.append(f"  {s_type} {skill['name']} (макс. ур. {skill.get('max_level', 5)})")
        lines.append(f"     📝 {skill['description']}")
        lines.append(f"     📊 Ур. требуется: {skill.get('level_req', 1)}  |  💎 Стоимость: {skill.get('cost', 1)}")
        lines.append("")
    return "\n".join(lines)


def format_player_skills(player: Any) -> str:
    player_skills: dict = player.skills if player.skills else {}
    if not player_skills:
        return "📋 У вас нет навыков."
    lines = ["📋 <b>Ваши навыки:</b>", ""]
    for sid, level in player_skills.items():
        skill = get_skill(sid)
        if skill:
            s_type = "🔴" if skill["type"] == "active" else "🔵"
            lines.append(f"  {s_type} {skill['name']} — ур. {level}/{skill.get('max_level', 5)}")
    sp = player.skill_points if hasattr(player, "skill_points") and player.skill_points else 0
    lines.append(f"\n💎 Очков навыков: {sp}")
    return "\n".join(lines)
