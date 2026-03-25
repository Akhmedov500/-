from __future__ import annotations

import random
from typing import Any, Optional

import config


class CombatResult:
    def __init__(self) -> None:
        self.winner: str = ""  # "player" or "enemy"
        self.rounds: list[dict[str, Any]] = []
        self.xp_gained: int = 0
        self.gold_gained: int = 0
        self.loot: list[str] = []
        self.player_damage_taken: int = 0
        self.enemy_damage_taken: int = 0
        self.log: list[str] = []


def calculate_damage(attacker_atk: int, defender_def: int, is_crit: bool = False) -> int:
    base = max(1, attacker_atk - defender_def // 2)
    variance = random.uniform(0.85, 1.15)
    damage = int(base * variance)
    if is_crit:
        damage = int(damage * config.CRITICAL_HIT_MULTIPLIER)
    return max(1, damage)


def is_critical_hit(luck: int = 5) -> bool:
    crit_chance = config.BASE_CRIT_CHANCE + (luck * 0.005)
    return random.random() < crit_chance


def is_dodge(speed: int = 5, opponent_speed: int = 5) -> bool:
    dodge_chance = config.BASE_DODGE_CHANCE + (speed - opponent_speed) * 0.01
    dodge_chance = max(0.01, min(0.3, dodge_chance))
    return random.random() < dodge_chance


def run_combat(
    player: Any,
    enemy: dict[str, Any],
    weather_effects: Optional[dict[str, Any]] = None,
) -> CombatResult:
    result = CombatResult()

    p_hp = player.health
    p_atk = player.attack
    p_def = player.defense
    p_spd = player.speed
    p_luck = player.luck

    e_hp = enemy["hp"]
    e_atk = enemy["attack"]
    e_def = enemy["defense"]
    e_spd = enemy.get("speed", 5)
    e_name = enemy["name"]

    if weather_effects:
        damage_mod = weather_effects.get("bonus_damage", 0)
        p_atk = int(p_atk * (1 + damage_mod))
        e_atk = int(e_atk * (1 + damage_mod))

    result.log.append(f"⚔️ Бой начался: Вы vs {e_name}!")
    result.log.append(f"❤️ Ваше HP: {p_hp}  |  👹 HP врага: {e_hp}")
    result.log.append("")

    max_rounds = 30
    for rnd in range(1, max_rounds + 1):
        round_data: dict[str, Any] = {"round": rnd}

        # Player attacks first if faster
        if p_spd >= e_spd:
            first_attacker = "player"
        else:
            first_attacker = "enemy"

        for attacker in [first_attacker, "enemy" if first_attacker == "player" else "player"]:
            if attacker == "player":
                if is_dodge(e_spd, p_spd):
                    result.log.append(f"  Раунд {rnd}: {e_name} уклонился от вашей атаки!")
                    round_data["player_dodged_by_enemy"] = True
                    continue
                crit = is_critical_hit(p_luck)
                dmg = calculate_damage(p_atk, e_def, crit)
                e_hp -= dmg
                result.enemy_damage_taken += dmg
                crit_text = " 💥КРИТ!" if crit else ""
                result.log.append(f"  Раунд {rnd}: Вы наносите {dmg} урона{crit_text} (HP врага: {max(0, e_hp)})")
                round_data["player_damage"] = dmg
                round_data["player_crit"] = crit
            else:
                if is_dodge(p_spd, e_spd):
                    result.log.append(f"  Раунд {rnd}: Вы уклонились от атаки {e_name}!")
                    round_data["enemy_dodged_by_player"] = True
                    continue
                crit = is_critical_hit(5)
                dmg = calculate_damage(e_atk, p_def, crit)
                p_hp -= dmg
                result.player_damage_taken += dmg
                crit_text = " 💥КРИТ!" if crit else ""
                result.log.append(f"  Раунд {rnd}: {e_name} наносит {dmg} урона{crit_text} (Ваше HP: {max(0, p_hp)})")
                round_data["enemy_damage"] = dmg
                round_data["enemy_crit"] = crit

            if e_hp <= 0:
                result.winner = "player"
                result.xp_gained = enemy.get("xp", 0)
                result.gold_gained = enemy.get("gold", 0)
                loot_table = enemy.get("loot", [])
                for item in loot_table:
                    if random.random() < 0.3 + (p_luck * 0.01):
                        result.loot.append(item)
                result.log.append("")
                result.log.append(f"🎉 Победа! Вы одолели {e_name}!")
                result.log.append(f"📊 +{result.xp_gained} XP  |  💰 +{result.gold_gained} золота")
                if result.loot:
                    result.log.append(f"📦 Добыча: {', '.join(result.loot)}")
                result.rounds = [round_data]
                return result

            if p_hp <= 0:
                result.winner = "enemy"
                gold_lost = max(0, int(player.gold * 0.1))
                result.gold_gained = -gold_lost
                result.log.append("")
                result.log.append(f"💀 Поражение! {e_name} победил вас!")
                result.log.append(f"💰 Потеряно: {gold_lost} золота")
                result.rounds = [round_data]
                return result

        result.rounds.append(round_data)

    result.winner = "draw"
    result.log.append("")
    result.log.append("⏰ Ничья! Бой затянулся слишком долго.")
    return result


def format_combat_result(result: CombatResult) -> str:
    return "\n".join(result.log)
