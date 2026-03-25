from __future__ import annotations

from typing import Any, Optional

from game.core.ship import SHIP_UPGRADES
from game.core.player import has_item, remove_from_inventory


def get_upgrade(upgrade_id: str) -> Optional[dict[str, Any]]:
    return SHIP_UPGRADES.get(upgrade_id)


def can_upgrade_ship(player: Any, ship: Any, upgrade_id: str) -> Optional[str]:
    upgrade = get_upgrade(upgrade_id)
    if not upgrade:
        return "Улучшение не найдено."
    ship_upgrades: dict = ship.upgrades if ship.upgrades else {}
    current_level = ship_upgrades.get(upgrade_id, 0)
    if current_level >= upgrade["max_level"]:
        return "Улучшение уже максимального уровня."
    if player.gold < upgrade["gold_cost"]:
        return f"Недостаточно золота. Нужно: {upgrade['gold_cost']}."
    for mat_id, qty in upgrade["materials"].items():
        if not has_item(player, mat_id, qty):
            return f"Недостаточно материалов: {mat_id} x{qty}."
    return None


def apply_upgrade(player: Any, ship: Any, upgrade_id: str) -> Optional[str]:
    error = can_upgrade_ship(player, ship, upgrade_id)
    if error:
        return error
    upgrade = get_upgrade(upgrade_id)
    if not upgrade:
        return "Улучшение не найдено."

    player.gold -= upgrade["gold_cost"]
    for mat_id, qty in upgrade["materials"].items():
        remove_from_inventory(player, mat_id, qty)

    ship_upgrades: dict = ship.upgrades if ship.upgrades else {}
    current_level = ship_upgrades.get(upgrade_id, 0)
    ship_upgrades[upgrade_id] = current_level + 1
    ship.upgrades = ship_upgrades

    # Apply bonuses
    bonus = upgrade["bonus"]
    if "hull_hp_pct" in bonus:
        ship.max_hull_hp = int(ship.max_hull_hp * (1 + bonus["hull_hp_pct"]))
        ship.hull_hp = min(ship.hull_hp, ship.max_hull_hp)
    if "speed_pct" in bonus:
        ship.sail_speed = int(ship.sail_speed * (1 + bonus["speed_pct"]))
    if "damage_pct" in bonus:
        ship.cannon_damage = int(ship.cannon_damage * (1 + bonus["damage_pct"]))
    if "cargo_pct" in bonus:
        ship.cargo_capacity = int(ship.cargo_capacity * (1 + bonus["cargo_pct"]))
    if "crew_pct" in bonus:
        ship.max_crew = int(ship.max_crew * (1 + bonus["crew_pct"]))

    return None


def format_ship_upgrades(ship: Any) -> str:
    ship_upgrades: dict = ship.upgrades if ship.upgrades else {}
    if not ship_upgrades:
        return "🔧 Корабль не улучшён."
    lines = ["🔧 <b>Улучшения корабля:</b>"]
    for uid, level in ship_upgrades.items():
        upgrade = get_upgrade(uid)
        if upgrade:
            lines.append(f"  • {upgrade['name']} — ур. {level}/{upgrade['max_level']}")
    return "\n".join(lines)


def format_available_upgrades(ship: Any) -> str:
    lines = ["🔧 <b>Доступные улучшения:</b>", ""]
    ship_upgrades: dict = ship.upgrades if ship.upgrades else {}
    for uid, upgrade in SHIP_UPGRADES.items():
        current_level = ship_upgrades.get(uid, 0)
        if current_level >= upgrade["max_level"]:
            status = "✅ МАКС"
        else:
            status = f"ур. {current_level}/{upgrade['max_level']}"
        lines.append(f"  🔹 {upgrade['name']} ({status})")
        lines.append(f"     📝 {upgrade['description']}")
        lines.append(f"     💰 {upgrade['gold_cost']} золота")
        mats = ", ".join(f"{k} x{v}" for k, v in upgrade["materials"].items())
        lines.append(f"     📋 {mats}")
        lines.append("")
    return "\n".join(lines)
