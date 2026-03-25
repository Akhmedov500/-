from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load_faction_quests() -> dict[str, list[dict[str, Any]]]:
    with open(DATA_DIR / "quests.json", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("faction_quests", {})


def get_faction_quests(faction_id: str) -> list[dict[str, Any]]:
    all_quests = _load_faction_quests()
    return all_quests.get(faction_id, [])


def get_available_faction_quests(player: Any, faction_id: str) -> list[dict[str, Any]]:
    quests = get_faction_quests(faction_id)
    available = []
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    completed_faction: list = quest_progress.get("completed_faction_quests", [])

    for q in quests:
        qid = q["id"]
        if qid in completed_faction and not q.get("repeatable", False):
            continue
        if player.level < q.get("level_req", 1):
            continue
        rep = (player.faction_reputation or {}).get(faction_id, 0)
        if rep < q.get("rep_req", 0):
            continue
        available.append(q)
    return available


def accept_faction_quest(player: Any, quest_id: str, faction_id: str) -> Optional[str]:
    quests = get_faction_quests(faction_id)
    quest = None
    for q in quests:
        if q["id"] == quest_id:
            quest = q
            break
    if not quest:
        return "Квест не найден."
    if player.level < quest.get("level_req", 1):
        return f"Требуется уровень {quest['level_req']}."
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    active: list = quest_progress.get("active_faction_quests", [])
    if len(active) >= 3:
        return "Слишком много активных квестов (макс. 3)."
    if any(aq["id"] == quest_id for aq in active):
        return "Этот квест уже принят."
    active.append({"id": quest_id, "faction": faction_id, "progress": {}})
    quest_progress["active_faction_quests"] = active
    player.quest_progress = quest_progress
    return None


def complete_faction_quest(player: Any, quest_id: str) -> Optional[dict[str, Any]]:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    active: list = quest_progress.get("active_faction_quests", [])
    quest_entry = None
    for aq in active:
        if aq["id"] == quest_id:
            quest_entry = aq
            break
    if not quest_entry:
        return None
    faction_id = quest_entry["faction"]
    quests = get_faction_quests(faction_id)
    quest = None
    for q in quests:
        if q["id"] == quest_id:
            quest = q
            break
    if not quest:
        return None
    active.remove(quest_entry)
    completed: list = quest_progress.get("completed_faction_quests", [])
    completed.append(quest_id)
    quest_progress["active_faction_quests"] = active
    quest_progress["completed_faction_quests"] = completed
    player.quest_progress = quest_progress
    return quest.get("rewards")


def format_faction_quest(quest: dict[str, Any]) -> str:
    lines = [
        f"📜 <b>{quest['title']}</b>",
        f"📝 {quest['description']}",
        f"📊 Мин. уровень: {quest.get('level_req', 1)}",
    ]
    objectives = quest.get("objectives", [])
    if objectives:
        lines.append("📋 <b>Задачи:</b>")
        for obj in objectives:
            lines.append(f"  • {obj['description']}")
    rewards = quest.get("rewards", {})
    if rewards:
        lines.append("🎁 <b>Награды:</b>")
        if "gold" in rewards:
            lines.append(f"  💰 {rewards['gold']} золота")
        if "xp" in rewards:
            lines.append(f"  📊 {rewards['xp']} опыта")
        if "reputation" in rewards:
            lines.append(f"  ⭐ +{rewards['reputation']} репутации")
    if quest.get("repeatable"):
        lines.append("🔄 Повторяемый")
    return "\n".join(lines)
