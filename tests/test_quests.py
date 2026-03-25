from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.quests.main_story import get_main_story, get_chapter
from game.quests.daily_quests import get_daily_quests
from game.quests.achievements import get_achievement, all_achievements, check_achievement
from game.crafting.materials import get_material, MATERIALS
from game.crafting.recipes import get_recipe, RECIPES


class MockPlayer:
    def __init__(self) -> None:
        self.level = 10
        self.gold = 5000
        self.achievements: list = []
        self.stats: dict = {
            "monsters_killed": 50,
            "quests_completed": 10,
            "items_crafted": 5,
            "islands_visited": 8,
            "gold_earned": 10000,
            "pvp_battles": 3,
        }
        self.pvp_wins = 3
        self.quest_progress: dict = {}
        self.inventory: list = []
        self.skills: dict = {}
        self.faction_reputation: dict = {}


def test_get_main_story() -> None:
    story = get_main_story()
    assert isinstance(story, list)
    assert len(story) > 0, "Main story should have at least one chapter"


def test_get_chapter() -> None:
    story = get_main_story()
    if story:
        chapter = get_chapter(1)
        assert chapter is not None
        assert "title" in chapter or "name" in chapter


def test_daily_quests() -> None:
    quests = get_daily_quests(10)
    assert isinstance(quests, list)
    assert len(quests) > 0, "Should have daily quests"


def test_achievements_exist() -> None:
    achievements = all_achievements()
    assert len(achievements) > 0, "Should have achievements"


def test_check_achievement_level() -> None:
    player = MockPlayer()
    player.level = 10
    player.achievements = []
    ach = get_achievement("first_steps")
    if ach and ach.get("condition", {}).get("type") == "level":
        result = check_achievement(player, "first_steps")
        if ach["condition"]["target"] <= 10:
            assert result is True


def test_materials_exist() -> None:
    assert len(MATERIALS) > 0, "Should have materials"
    wood = get_material("wood")
    assert wood is not None
    assert "name" in wood


def test_recipes_exist() -> None:
    assert len(RECIPES) > 0, "Should have recipes"
    for rid, recipe in RECIPES.items():
        assert "name" in recipe
        assert "materials" in recipe
        assert "category" in recipe


def test_daily_quests_consistency() -> None:
    quests1 = get_daily_quests(10)
    quests2 = get_daily_quests(10)
    ids1 = [q["id"] for q in quests1]
    ids2 = [q["id"] for q in quests2]
    assert ids1 == ids2, "Daily quests should be consistent for same day"


if __name__ == "__main__":
    test_get_main_story()
    test_get_chapter()
    test_daily_quests()
    test_achievements_exist()
    test_check_achievement_level()
    test_materials_exist()
    test_recipes_exist()
    test_daily_quests_consistency()
    print("All quest tests passed!")
