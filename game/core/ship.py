from __future__ import annotations

from typing import Any, Optional

SHIP_TYPES: dict[str, dict[str, Any]] = {
    "sloop": {
        "name": "Шлюп",
        "description": "Маленький и быстрый корабль. Идеален для начинающих.",
        "hull_hp": 100,
        "speed": 15,
        "damage": 10,
        "cargo": 30,
        "crew": 5,
        "max_crew": 10,
        "price": 0,
        "level_req": 1,
        "emoji": "⛵",
    },
    "brigantine": {
        "name": "Бригантина",
        "description": "Сбалансированный корабль среднего размера.",
        "hull_hp": 200,
        "speed": 12,
        "damage": 20,
        "cargo": 60,
        "crew": 10,
        "max_crew": 25,
        "price": 2000,
        "level_req": 10,
        "emoji": "🚢",
    },
    "frigate": {
        "name": "Фрегат",
        "description": "Мощный военный корабль с тяжёлым вооружением.",
        "hull_hp": 350,
        "speed": 10,
        "damage": 35,
        "cargo": 80,
        "crew": 20,
        "max_crew": 50,
        "price": 5000,
        "level_req": 20,
        "emoji": "⚓",
    },
    "galleon": {
        "name": "Галеон",
        "description": "Огромный корабль с максимальной грузоподъёмностью.",
        "hull_hp": 500,
        "speed": 8,
        "damage": 30,
        "cargo": 150,
        "crew": 30,
        "max_crew": 80,
        "price": 10000,
        "level_req": 30,
        "emoji": "🛳",
    },
    "man_o_war": {
        "name": "Линейный корабль",
        "description": "Самый мощный боевой корабль на морях.",
        "hull_hp": 700,
        "speed": 6,
        "damage": 55,
        "cargo": 100,
        "crew": 50,
        "max_crew": 120,
        "price": 25000,
        "level_req": 45,
        "emoji": "🏴‍☠️",
    },
    "ghost_ship": {
        "name": "Корабль-Призрак",
        "description": "Проклятый корабль, несущий страх и смерть.",
        "hull_hp": 600,
        "speed": 14,
        "damage": 50,
        "cargo": 60,
        "crew": 0,
        "max_crew": 0,
        "price": 30000,
        "level_req": 50,
        "emoji": "👻",
    },
    "dragon_ship": {
        "name": "Драконий Корабль",
        "description": "Легендарный корабль, украшенный головой дракона.",
        "hull_hp": 800,
        "speed": 12,
        "damage": 60,
        "cargo": 120,
        "crew": 40,
        "max_crew": 100,
        "price": 50000,
        "level_req": 60,
        "emoji": "🐉",
    },
}

SHIP_UPGRADES: dict[str, dict[str, Any]] = {
    "reinforced_hull": {
        "name": "Укреплённый корпус",
        "description": "+20% HP корпуса",
        "bonus": {"hull_hp_pct": 0.2},
        "materials": {"wood": 20, "iron_ingot": 10},
        "gold_cost": 500,
        "max_level": 5,
    },
    "silk_sails": {
        "name": "Шёлковые паруса",
        "description": "+15% скорости",
        "bonus": {"speed_pct": 0.15},
        "materials": {"silk": 15, "rope": 10},
        "gold_cost": 400,
        "max_level": 5,
    },
    "heavy_cannons": {
        "name": "Тяжёлые пушки",
        "description": "+20% урона пушек",
        "bonus": {"damage_pct": 0.2},
        "materials": {"iron_ingot": 15, "gunpowder": 20},
        "gold_cost": 600,
        "max_level": 5,
    },
    "expanded_cargo": {
        "name": "Расширенный трюм",
        "description": "+25% грузоподъёмности",
        "bonus": {"cargo_pct": 0.25},
        "materials": {"wood": 25, "iron_ingot": 5},
        "gold_cost": 300,
        "max_level": 5,
    },
    "crew_quarters": {
        "name": "Каюты экипажа",
        "description": "+20% максимума экипажа",
        "bonus": {"crew_pct": 0.2},
        "materials": {"wood": 15, "cloth": 10},
        "gold_cost": 350,
        "max_level": 3,
    },
    "magic_compass": {
        "name": "Магический компас",
        "description": "Показывает скрытые острова",
        "bonus": {"reveal_hidden": True},
        "materials": {"magic_crystal": 3, "gold_ingot": 2},
        "gold_cost": 2000,
        "max_level": 1,
    },
}


def format_ship(ship: Any) -> str:
    ship_info = SHIP_TYPES.get(ship.ship_type, {})
    emoji = ship_info.get("emoji", "🚢")
    lines = [
        f"{emoji} <b>{ship.name}</b> ({ship_info.get('name', ship.ship_type)})",
        f"   ❤️ Корпус: {ship.hull_hp}/{ship.max_hull_hp}",
        f"   💨 Скорость: {ship.sail_speed}",
        f"   💥 Урон пушек: {ship.cannon_damage}",
        f"   📦 Грузоподъёмность: {ship.cargo_capacity}",
        f"   👥 Экипаж: {ship.crew_count}/{ship.max_crew}",
        f"   🔧 Прочность: {ship.durability}%",
    ]
    if ship.is_active:
        lines[0] += " ⭐"
    return "\n".join(lines)


def format_fleet(ships: list[Any]) -> str:
    if not ships:
        return "🚢 У вас нет кораблей."
    lines = ["🚢 <b>Ваш флот:</b>"]
    for ship in ships:
        lines.append(format_ship(ship))
        lines.append("")
    return "\n".join(lines)


def get_ship_price(ship_type: str) -> int:
    return SHIP_TYPES.get(ship_type, {}).get("price", 0)


def can_buy_ship(player_level: int, ship_type: str) -> Optional[str]:
    info = SHIP_TYPES.get(ship_type)
    if not info:
        return "Неизвестный тип корабля."
    if player_level < info["level_req"]:
        return f"Требуется уровень {info['level_req']}."
    return None
