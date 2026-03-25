from __future__ import annotations

import random
from typing import Any, Optional

from game.combat.battle import CombatResult, calculate_damage, is_critical_hit
from game.world.islands import get_boss, get_random_encounter, BOSSES


def run_boss_fight(player: Any, boss_id: str) -> CombatResult:
    boss = get_boss(boss_id)
    if not boss:
        result = CombatResult()
        result.log.append("Босс не найден!")
        result.winner = "error"
        return result

    from game.combat.battle import run_combat
    return run_combat(player, boss)


def run_random_encounter(player: Any, island_id: str) -> Optional[CombatResult]:
    encounter = get_random_encounter(island_id)
    if not encounter:
        return None
    from game.combat.battle import run_combat
    return run_combat(player, encounter)


def run_raid(players: list[Any], boss_id: str) -> CombatResult:
    boss = get_boss(boss_id)
    if not boss:
        result = CombatResult()
        result.log.append("Босс не найден!")
        result.winner = "error"
        return result

    result = CombatResult()
    boss_hp = boss["hp"]
    boss_atk = boss["attack"]
    boss_def = boss["defense"]
    boss_name = boss["name"]

    player_hp: dict[int, int] = {}
    for p in players:
        player_hp[p.telegram_id] = p.health

    result.log.append(f"⚔️ РЕЙД: Группа из {len(players)} героев vs {boss_name}!")
    result.log.append(f"👹 HP босса: {boss_hp}")
    result.log.append("")

    alive_players = list(players)

    for rnd in range(1, 50):
        if not alive_players:
            break

        result.log.append(f"📍 Раунд {rnd}:")

        # All players attack
        for p in alive_players[:]:
            if player_hp[p.telegram_id] <= 0:
                continue
            crit = is_critical_hit(p.luck)
            dmg = calculate_damage(p.attack, boss_def, crit)
            boss_hp -= dmg
            crit_text = " 💥" if crit else ""
            result.log.append(f"  {p.display_name} → {dmg}{crit_text}")
            if boss_hp <= 0:
                break

        if boss_hp <= 0:
            result.winner = "player"
            result.xp_gained = boss.get("xp", 0)
            result.gold_gained = boss.get("gold", 0)
            loot_table = boss.get("loot", [])
            for item in loot_table:
                if random.random() < 0.5:
                    result.loot.append(item)
            result.log.append("")
            result.log.append(f"🎉 ПОБЕДА! {boss_name} повержен!")
            result.log.append(f"📊 Каждый получает: +{result.xp_gained} XP, +{result.gold_gained // len(players)} 💰")
            if result.loot:
                result.log.append(f"📦 Добыча: {', '.join(result.loot)}")
            return result

        # Boss attacks random player
        if alive_players:
            target = random.choice(alive_players)
            crit = is_critical_hit(5)
            dmg = calculate_damage(boss_atk, target.defense, crit)
            player_hp[target.telegram_id] -= dmg
            crit_text = " 💥" if crit else ""
            result.log.append(f"  {boss_name} → {target.display_name}: {dmg}{crit_text}")

            if player_hp[target.telegram_id] <= 0:
                result.log.append(f"  💀 {target.display_name} пал в бою!")
                alive_players.remove(target)

        result.log.append(f"  👹 HP босса: {max(0, boss_hp)}")
        result.log.append("")

    if boss_hp > 0:
        result.winner = "enemy"
        result.log.append(f"💀 Рейд провален! {boss_name} слишком силён!")
    return result


def get_available_bosses(island_id: str) -> list[dict[str, Any]]:
    bosses = []
    for bid, bdata in BOSSES.items():
        if bdata.get("island") == island_id:
            bosses.append({**bdata, "id": bid})
    return bosses


def format_boss_list(island_id: str) -> str:
    bosses = get_available_bosses(island_id)
    if not bosses:
        return "🐲 На этом острове нет боссов."
    lines = ["🐲 <b>Боссы на этом острове:</b>", ""]
    for b in bosses:
        lines.append(f"  💀 {b['name']} (ур. {b['level']})")
        lines.append(f"     ❤️ HP: {b['hp']}  ⚔️ ATK: {b['attack']}  🛡 DEF: {b['defense']}")
        lines.append(f"     🎁 XP: {b['xp']}  💰 {b['gold']} золота")
        lines.append("")
    return "\n".join(lines)
