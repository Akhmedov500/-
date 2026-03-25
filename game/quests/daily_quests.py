from __future__ import annotations

import json
import random
from datetime import datetime, date
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load_daily_pool() -> list[dict[str, Any]]:
    with open(DATA_DIR / "quests.json", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("daily_quest_pool", [])


def get_daily_quests(player_level: int = 1, count: int = 3) -> list[dict[str, Any]]:
    pool = _load_daily_pool()
    eligible = [q for q in pool if player_level >= q.get("min_level", 1)]
    if not eligible:
        return []
    seed = int(date.today().strftime("%Y%m%d"))
    rng = random.Random(seed)
    return rng.sample(eligible, min(count, len(eligible)))


def accept_daily_quest(player: Any, quest_id: str) -> Optional[str]:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    active_daily: list = quest_progress.get("active_daily_quests", [])
    if len(active_daily) >= 3:
        return "Слишком много активных ежедневных квестов."
    if any(d["id"] == quest_id for d in active_daily):
        return "Этот квест уже принят."
    completed_today: list = quest_progress.get("completed_daily_today", [])
    if quest_id in completed_today:
        return "Вы уже выполнили этот квест сегодня."
    active_daily.append({"id": quest_id, "progress": 0, "accepted_at": datetime.utcnow().isoformat()})
    quest_progress["active_daily_quests"] = active_daily
    player.quest_progress = quest_progress
    return None


def update_daily_progress(player: Any, quest_id: str, amount: int = 1) -> bool:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    active_daily: list = quest_progress.get("active_daily_quests", [])
    for dq in active_daily:
        if dq["id"] == quest_id:
            dq["progress"] = dq.get("progress", 0) + amount
            pool = _load_daily_pool()
            quest = None
            for q in pool:
                if q["id"] == quest_id:
                    quest = q
                    break
            if quest:
                target = quest.get("target_count", 1)
                if dq["progress"] >= target:
                    player.quest_progress = quest_progress
                    return True
            player.quest_progress = quest_progress
            return False
    return False


def complete_daily_quest(player: Any, quest_id: str) -> Optional[dict[str, Any]]:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    active_daily: list = quest_progress.get("active_daily_quests", [])
    entry = None
    for dq in active_daily:
        if dq["id"] == quest_id:
            entry = dq
            break
    if not entry:
        return None
    pool = _load_daily_pool()
    quest = None
    for q in pool:
        if q["id"] == quest_id:
            quest = q
            break
    if not quest:
        return None
    active_daily.remove(entry)
    completed_today: list = quest_progress.get("completed_daily_today", [])
    completed_today.append(quest_id)
    quest_progress["active_daily_quests"] = active_daily
    quest_progress["completed_daily_today"] = completed_today
    player.quest_progress = quest_progress
    return quest.get("rewards")


def reset_daily_quests(player: Any) -> None:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    quest_progress["completed_daily_today"] = []
    quest_progress["active_daily_quests"] = []
    player.quest_progress = quest_progress


def format_daily_quests(quests: list[dict[str, Any]]) -> str:
    if not quests:
        return "📋 Нет доступных ежедневных квестов."
    lines = ["📋 <b>Ежедневные квесты:</b>", ""]
    for q in quests:
        lines.append(f"  🔹 {q['title']}")
        lines.append(f"     📝 {q['description']}")
        rewards = q.get("rewards", {})
        r_parts = []
        if "gold" in rewards:
            r_parts.append(f"💰{rewards['gold']}")
        if "xp" in rewards:
            r_parts.append(f"📊{rewards['xp']}")
        if r_parts:
            lines.append(f"     🎁 {' '.join(r_parts)}")
        lines.append("")
    return "\n".join(lines)
