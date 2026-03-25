from __future__ import annotations

from typing import Any

import config
from game.combat.battle import calculate_damage, is_critical_hit, is_dodge


class PvPResult:
    def __init__(self) -> None:
        self.winner_id: int = 0
        self.loser_id: int = 0
        self.winner_name: str = ""
        self.loser_name: str = ""
        self.rating_change: int = 0
        self.gold_reward: int = 0
        self.xp_reward: int = 0
        self.log: list[str] = []


def calculate_rating_change(winner_rating: int, loser_rating: int) -> int:
    expected = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    change = int(config.PVP_RATING_K * (1 - expected))
    return max(1, change)


def run_pvp(player1: Any, player2: Any) -> PvPResult:
    result = PvPResult()

    p1_hp = player1.health
    p1_atk = player1.attack
    p1_def = player1.defense
    p1_spd = player1.speed
    p1_luck = player1.luck

    p2_hp = player2.health
    p2_atk = player2.attack
    p2_def = player2.defense
    p2_spd = player2.speed
    p2_luck = player2.luck

    result.log.append(f"⚔️ PVP: {player1.display_name} vs {player2.display_name}!")
    result.log.append(f"❤️ {player1.display_name}: {p1_hp} HP  |  {player2.display_name}: {p2_hp} HP")
    result.log.append("")

    for rnd in range(1, 31):
        if p1_spd >= p2_spd:
            order = [(player1, p1_atk, p1_luck, p1_spd, "p1"), (player2, p2_atk, p2_luck, p2_spd, "p2")]
        else:
            order = [(player2, p2_atk, p2_luck, p2_spd, "p2"), (player1, p1_atk, p1_luck, p1_spd, "p1")]

        for attacker, atk, luck, spd, tag in order:
            if tag == "p1":
                def_val = p2_def
                target_spd = p2_spd
                target_name = player2.display_name
            else:
                def_val = p1_def
                target_spd = p1_spd
                target_name = player1.display_name

            if is_dodge(target_spd, spd):
                result.log.append(f"  Раунд {rnd}: {target_name} уклонился!")
                continue

            crit = is_critical_hit(luck)
            dmg = calculate_damage(atk, def_val, crit)
            crit_text = " 💥КРИТ!" if crit else ""

            if tag == "p1":
                p2_hp -= dmg
                result.log.append(f"  Раунд {rnd}: {attacker.display_name} → {dmg}{crit_text} (HP {target_name}: {max(0, p2_hp)})")
            else:
                p1_hp -= dmg
                result.log.append(f"  Раунд {rnd}: {attacker.display_name} → {dmg}{crit_text} (HP {target_name}: {max(0, p1_hp)})")

            if p2_hp <= 0:
                _finalize_pvp(result, player1, player2)
                return result
            if p1_hp <= 0:
                _finalize_pvp(result, player2, player1)
                return result

    # Draw — higher HP wins
    if p1_hp >= p2_hp:
        _finalize_pvp(result, player1, player2)
    else:
        _finalize_pvp(result, player2, player1)
    return result


def _finalize_pvp(result: PvPResult, winner: Any, loser: Any) -> None:
    result.winner_id = winner.telegram_id
    result.loser_id = loser.telegram_id
    result.winner_name = winner.display_name
    result.loser_name = loser.display_name
    result.rating_change = calculate_rating_change(winner.pvp_rating, loser.pvp_rating)
    result.gold_reward = config.PVP_GOLD_REWARD + (winner.level * 10)
    result.xp_reward = config.PVP_XP_REWARD + (winner.level * 5)

    result.log.append("")
    result.log.append(f"🏆 Победитель: {winner.display_name}!")
    result.log.append(f"📊 Рейтинг: +{result.rating_change} для победителя, -{result.rating_change} для проигравшего")
    result.log.append(f"💰 Награда: {result.gold_reward} золота, {result.xp_reward} XP")


def format_pvp_result(result: PvPResult) -> str:
    return "\n".join(result.log)


def format_pvp_leaderboard(players: list[Any]) -> str:
    lines = ["🏆 <b>PVP Рейтинг:</b>", ""]
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(players[:20]):
        medal = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"  {medal} {p.display_name} — {p.pvp_rating} ⭐ (ур. {p.level})")
    return "\n".join(lines)
