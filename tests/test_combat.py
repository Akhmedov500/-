from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.combat.battle import calculate_damage, is_critical_hit, is_dodge, CombatResult, run_combat
from game.combat.pvp import calculate_rating_change
from game.combat.fleet import calculate_fleet_power


def test_calculate_damage_basic() -> None:
    dmg = calculate_damage(20, 10, is_crit=False)
    assert dmg >= 1, "Damage should be at least 1"


def test_calculate_damage_crit() -> None:
    dmg_normal = calculate_damage(20, 10, is_crit=False)
    # Run multiple times to check crit is generally higher
    crit_damages = [calculate_damage(20, 10, is_crit=True) for _ in range(100)]
    avg_crit = sum(crit_damages) / len(crit_damages)
    avg_normal = sum(calculate_damage(20, 10, is_crit=False) for _ in range(100)) / 100
    assert avg_crit > avg_normal, "Crit damage should on average be higher"


def test_calculate_damage_minimum() -> None:
    dmg = calculate_damage(1, 100, is_crit=False)
    assert dmg >= 1, "Damage should never be less than 1"


def test_is_critical_hit_returns_bool() -> None:
    result = is_critical_hit(5)
    assert isinstance(result, bool)


def test_is_dodge_returns_bool() -> None:
    result = is_dodge(5, 5)
    assert isinstance(result, bool)


def test_combat_result_init() -> None:
    r = CombatResult()
    assert r.winner == ""
    assert r.rounds == []
    assert r.xp_gained == 0
    assert r.gold_gained == 0
    assert r.loot == []


class MockPlayer:
    def __init__(self) -> None:
        self.health = 100
        self.max_health = 100
        self.attack = 15
        self.defense = 8
        self.speed = 5
        self.luck = 5
        self.gold = 500
        self.level = 5
        self.inventory: list = []
        self.skills: dict = {}
        self.stats: dict = {}


def test_run_combat_returns_result() -> None:
    player = MockPlayer()
    enemy = {"name": "Goblin", "hp": 30, "attack": 5, "defense": 2, "speed": 3, "xp": 10, "gold": 5, "loot": []}
    result = run_combat(player, enemy)
    assert isinstance(result, CombatResult)
    assert result.winner in ("player", "enemy", "draw")
    assert len(result.log) > 0


def test_run_combat_player_wins_weak_enemy() -> None:
    player = MockPlayer()
    player.attack = 50
    player.defense = 30
    enemy = {"name": "Rat", "hp": 10, "attack": 1, "defense": 0, "speed": 1, "xp": 5, "gold": 2, "loot": []}
    result = run_combat(player, enemy)
    assert result.winner == "player"
    assert result.xp_gained == 5
    assert result.gold_gained == 2


def test_rating_change() -> None:
    change = calculate_rating_change(1000, 1000)
    assert change > 0, "Rating change should be positive"
    high_vs_low = calculate_rating_change(1500, 1000)
    low_vs_high = calculate_rating_change(1000, 1500)
    assert low_vs_high > high_vs_low, "Beating a higher-rated player should give more rating"


def test_fleet_power() -> None:

    class MockShip:
        def __init__(self) -> None:
            self.hull_hp = 100
            self.cannon_damage = 10
            self.crew_count = 5

    ships = [MockShip(), MockShip()]
    power = calculate_fleet_power(ships)
    assert power > 0, "Fleet power should be positive"


if __name__ == "__main__":
    test_calculate_damage_basic()
    test_calculate_damage_crit()
    test_calculate_damage_minimum()
    test_is_critical_hit_returns_bool()
    test_is_dodge_returns_bool()
    test_combat_result_init()
    test_run_combat_returns_result()
    test_run_combat_player_wins_weak_enemy()
    test_rating_change()
    test_fleet_power()
    print("All combat tests passed!")
