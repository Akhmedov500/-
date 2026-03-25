from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_QUESTS: Optional[dict[str, Any]] = None


def _load_quests() -> dict[str, Any]:
    global _QUESTS
    if _QUESTS is None:
        with open(DATA_DIR / "quests.json", encoding="utf-8") as f:
            _QUESTS = json.load(f)
    return _QUESTS


def get_main_story() -> list[dict[str, Any]]:
    return _load_quests().get("main_story", [])


def get_chapter(chapter_num: int) -> Optional[dict[str, Any]]:
    for ch in get_main_story():
        if ch["chapter"] == chapter_num:
            return ch
    return None


def get_current_chapter(player: Any) -> Optional[dict[str, Any]]:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    current = quest_progress.get("main_story_chapter", 1)
    return get_chapter(current)


def advance_chapter(player: Any) -> Optional[dict[str, Any]]:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    current = quest_progress.get("main_story_chapter", 1)
    chapter = get_chapter(current)
    if not chapter:
        return None
    next_ch = chapter.get("next_chapter")
    if next_ch:
        quest_progress["main_story_chapter"] = next_ch
        player.quest_progress = quest_progress
        return get_chapter(next_ch)
    return None


def make_story_choice(player: Any, choice_index: int) -> Optional[dict[str, Any]]:
    chapter = get_current_chapter(player)
    if not chapter or "choices" not in chapter:
        return None
    choices = chapter["choices"]
    if choice_index < 0 or choice_index >= len(choices):
        return None
    choice = choices[choice_index]
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    quest_progress["main_story_chapter"] = choice.get("next_chapter", quest_progress.get("main_story_chapter", 1) + 1)
    story_choices: list = quest_progress.get("story_choices", [])
    story_choices.append({"chapter": chapter["chapter"], "choice": choice_index})
    quest_progress["story_choices"] = story_choices
    player.quest_progress = quest_progress
    return choice


def check_objectives(player: Any, chapter: dict[str, Any]) -> list[dict[str, Any]]:
    objectives = chapter.get("objectives", [])
    results = []
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    completed_objectives: list = quest_progress.get("completed_objectives", [])

    for obj in objectives:
        obj_key = f"ch{chapter['chapter']}_{obj['type']}_{obj.get('target', '')}"
        is_done = obj_key in completed_objectives
        results.append({**obj, "completed": is_done, "key": obj_key})
    return results


def complete_objective(player: Any, obj_key: str) -> None:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    completed: list = quest_progress.get("completed_objectives", [])
    if obj_key not in completed:
        completed.append(obj_key)
    quest_progress["completed_objectives"] = completed
    player.quest_progress = quest_progress


def format_chapter(chapter: dict[str, Any]) -> str:
    lines = [
        f"📖 <b>Глава {chapter['chapter']}: {chapter['title']}</b>",
        f"📝 {chapter['description']}",
        "",
        "📋 <b>Задачи:</b>",
    ]
    for i, obj in enumerate(chapter.get("objectives", []), 1):
        lines.append(f"  {i}. {obj['description']}")

    if "choices" in chapter:
        lines.append("")
        lines.append("⚖️ <b>Выбор:</b>")
        for i, choice in enumerate(chapter["choices"], 1):
            lines.append(f"  {i}. {choice['text']}")

    rewards = chapter.get("rewards", {})
    if rewards:
        lines.append("")
        lines.append("🎁 <b>Награды:</b>")
        if "gold" in rewards:
            lines.append(f"  💰 {rewards['gold']} золота")
        if "xp" in rewards:
            lines.append(f"  📊 {rewards['xp']} опыта")
        if "items" in rewards:
            lines.append(f"  📦 {', '.join(rewards['items'])}")
    return "\n".join(lines)


def format_story_progress(player: Any) -> str:
    quest_progress: dict = player.quest_progress if player.quest_progress else {}
    current_ch = quest_progress.get("main_story_chapter", 1)
    total_chapters = len(get_main_story())
    chapter = get_chapter(current_ch)
    lines = [
        "📖 <b>Сюжетная кампания</b>",
        f"📊 Прогресс: Глава {current_ch}/{total_chapters}",
    ]
    if chapter:
        lines.append(f"📍 Текущая: {chapter['title']}")
    return "\n".join(lines)
