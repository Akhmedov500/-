from __future__ import annotations

import random
from typing import Any



class FleetBattleResult:
    def __init__(self) -> None:
        self.winner: str = ""
        self.ships_lost: list[str] = []
        self.ships_damaged: list[dict[str, Any]] = []
        self.xp_gained: int = 0
        self.gold_gained: int = 0
        self.log: list[str] = []


def calculate_fleet_power(ships: list[Any]) -> int:
    total = 0
    for ship in ships:
        hp_score = ship.hull_hp * 0.5
        dmg_score = ship.cannon_damage * 2
        crew_score = ship.crew_count * 0.3
        total += int(hp_score + dmg_score + crew_score)
    return total


def run_fleet_battle(player_ships: list[Any], enemy_fleet: list[dict[str, Any]]) -> FleetBattleResult:
    result = FleetBattleResult()

    p_ships = [{"name": s.name, "hp": s.hull_hp, "dmg": s.cannon_damage, "obj": s} for s in player_ships if s.hull_hp > 0]
    e_ships = [{"name": s["name"], "hp": s["hp"], "dmg": s["dmg"]} for s in enemy_fleet]

    result.log.append(f"⚓ Морское сражение! Ваш флот ({len(p_ships)}) vs Враги ({len(e_ships)})!")
    result.log.append("")

    rnd = 0
    while p_ships and e_ships and rnd < 20:
        rnd += 1
        result.log.append(f"🔄 Раунд {rnd}:")

        # Player ships fire
        for ps in p_ships[:]:
            if not e_ships:
                break
            target = random.choice(e_ships)
            dmg = random.randint(int(ps["dmg"] * 0.8), int(ps["dmg"] * 1.2))
            target["hp"] -= dmg
            result.log.append(f"  {ps['name']} → {target['name']}: {dmg} урона")
            if target["hp"] <= 0:
                result.log.append(f"  💥 {target['name']} потоплен!")
                e_ships.remove(target)

        # Enemy ships fire
        for es in e_ships[:]:
            if not p_ships:
                break
            target = random.choice(p_ships)
            dmg = random.randint(int(es["dmg"] * 0.8), int(es["dmg"] * 1.2))
            target["hp"] -= dmg
            result.log.append(f"  {es['name']} → {target['name']}: {dmg} урона")
            if target["hp"] <= 0:
                result.log.append(f"  💥 {target['name']} потоплен!")
                result.ships_lost.append(target["name"])
                p_ships.remove(target)

        result.log.append("")

    if not e_ships:
        result.winner = "player"
        result.xp_gained = 100 * len(enemy_fleet)
        result.gold_gained = 200 * len(enemy_fleet)
        result.log.append("🎉 Победа! Вражеский флот уничтожен!")
        result.log.append(f"📊 +{result.xp_gained} XP  |  💰 +{result.gold_gained} золота")
    elif not p_ships:
        result.winner = "enemy"
        result.log.append("💀 Поражение! Ваш флот уничтожен!")
    else:
        result.winner = "draw"
        result.log.append("⏰ Ничья! Обе стороны отступили.")

    # Update remaining ships' HP
    for ps in p_ships:
        ship_obj = ps.get("obj")
        if ship_obj:
            result.ships_damaged.append({"ship": ship_obj, "remaining_hp": ps["hp"]})

    return result


def create_enemy_fleet(level: int, count: int = 3) -> list[dict[str, Any]]:
    fleet = []
    for i in range(count):
        hp = 100 + level * 20 + random.randint(-20, 20)
        dmg = 10 + level * 5 + random.randint(-5, 5)
        fleet.append({
            "name": f"Вражеский корабль #{i + 1}",
            "hp": hp,
            "dmg": dmg,
        })
    return fleet


def format_fleet_power(ships: list[Any]) -> str:
    power = calculate_fleet_power(ships)
    return f"⚓ Мощь флота: {power}"
