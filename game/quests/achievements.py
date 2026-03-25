from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_ACHIEVEMENTS: Optional[dict[str, dict[str, Any]]] = None


def _load_achievements() -> dict[str, dict[str, Any]]:
    global _ACHIEVEMENTS
    if _ACHIEVEMENTS is None:
        with open(DATA_DIR / "achievements.json", encoding="utf-8") as f:
            _ACHIEVEMENTS = json.load(f)
    return _ACHIEVEMENTS


def get_achievement(achievement_id: str) -> Optional[dict[str, Any]]:
    return _load_achievements().get(achievement_id)


def all_achievements() -> dict[str, dict[str, Any]]:
    return _load_achievements()


def check_achievement(player: Any, achievement_id: str) -> bool:
    achievement = get_achievement(achievement_id)
    if not achievement:
        return False
    achieved: list = player.achievements if player.achievements else []
    if achievement_id in achieved:
        return False
    condition = achievement.get("condition", {})
    cond_type = condition.get("type", "")
    target = condition.get("target", 0)

    if cond_type == "level":
        return player.level >= target
    elif cond_type == "gold":
        return player.gold >= target
    elif cond_type == "kills":
        stats: dict = player.stats if player.stats else {}
        return stats.get("total_kills", 0) >= target
    elif cond_type == "pvp_wins":
        stats = player.stats if player.stats else {}
        return stats.get("pvp_wins", 0) >= target
    elif cond_type == "quests":
        qp: dict = player.quest_progress if player.quest_progress else {}
        completed = len(qp.get("completed_faction_quests", []))
        return completed >= target
    elif cond_type == "islands_visited":
        visited: list = player.visited_islands if player.visited_islands else []
        return len(visited) >= target
    elif cond_type == "crafted":
        stats = player.stats if player.stats else {}
        return stats.get("items_crafted", 0) >= target
    elif cond_type == "boss_kills":
        stats = player.stats if player.stats else {}
        return stats.get("bosses_killed", 0) >= target
    elif cond_type == "trades":
        stats = player.stats if player.stats else {}
        return stats.get("trades_completed", 0) >= target
    elif cond_type == "reputation":
        faction = condition.get("faction", "")
        rep = (player.faction_reputation or {}).get(faction, 0)
        return rep >= target
    elif cond_type == "main_story":
        qp = player.quest_progress if player.quest_progress else {}
        return qp.get("main_story_chapter", 1) > target
    return False


def grant_achievement(player: Any, achievement_id: str) -> Optional[dict[str, Any]]:
    achievement = get_achievement(achievement_id)
    if not achievement:
        return None
    achieved: list = player.achievements if player.achievements else []
    if achievement_id in achieved:
        return None
    achieved.append(achievement_id)
    player.achievements = achieved
    return achievement


def check_all_achievements(player: Any) -> list[dict[str, Any]]:
    new_achievements = []
    for aid in all_achievements():
        if check_achievement(player, aid):
            ach = grant_achievement(player, aid)
            if ach:
                new_achievements.append({**ach, "id": aid})
    return new_achievements


def format_achievements(player: Any) -> str:
    achieved: list = player.achievements if player.achievements else []
    total = len(all_achievements())
    lines = [
        f"🏆 <b>Достижения: {len(achieved)}/{total}</b>",
        "",
    ]
    for aid, ach in all_achievements().items():
        if aid in achieved:
            lines.append(f"  ✅ {ach['name']} — {ach.get('description', '')}")
        else:
            lines.append(f"  ⬜ {ach['name']} — {ach.get('description', '')}")
    return "\n".join(lines)


def format_new_achievement(achievement: dict[str, Any]) -> str:
    lines = [
        "🏆 <b>ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!</b>",
        f"🎖️ {achievement['name']}",
        f"📝 {achievement.get('description', '')}",
    ]
    rewards = achievement.get("rewards", {})
    if rewards:
        lines.append("🎁 <b>Награда:</b>")
        if "gold" in rewards:
            lines.append(f"  💰 {rewards['gold']} золота")
        if "xp" in rewards:
            lines.append(f"  📊 {rewards['xp']} опыта")
    return "\n".join(lines)
