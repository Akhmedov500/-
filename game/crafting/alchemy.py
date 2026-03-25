from __future__ import annotations

from typing import Any, Optional

from game.core.player import has_item, remove_from_inventory, add_to_inventory


POTIONS: dict[str, dict[str, Any]] = {
    "health_potion": {
        "name": "Зелье здоровья",
        "description": "Восстанавливает 50 HP.",
        "emoji": "❤️",
        "effect": {"heal": 50},
        "materials": {"herbs": 3, "rare_herbs": 1},
        "level_req": 5,
        "xp": 15,
    },
    "greater_health_potion": {
        "name": "Великое зелье здоровья",
        "description": "Восстанавливает 150 HP.",
        "emoji": "💖",
        "effect": {"heal": 150},
        "materials": {"rare_herbs": 3, "magic_crystal": 1},
        "level_req": 20,
        "xp": 40,
    },
    "energy_potion": {
        "name": "Зелье энергии",
        "description": "Восстанавливает 30 энергии.",
        "emoji": "⚡",
        "effect": {"energy": 30},
        "materials": {"herbs": 2, "rare_herbs": 2},
        "level_req": 8,
        "xp": 20,
    },
    "strength_potion": {
        "name": "Зелье силы",
        "description": "+10 к атаке на 5 боёв.",
        "emoji": "💪",
        "effect": {"attack_buff": 10, "duration": 5},
        "materials": {"rare_herbs": 3, "magic_crystal": 1},
        "level_req": 15,
        "xp": 35,
    },
    "defense_potion": {
        "name": "Зелье защиты",
        "description": "+10 к защите на 5 боёв.",
        "emoji": "🛡",
        "effect": {"defense_buff": 10, "duration": 5},
        "materials": {"rare_herbs": 3, "coral": 2},
        "level_req": 15,
        "xp": 35,
    },
    "speed_potion": {
        "name": "Зелье скорости",
        "description": "+5 к скорости на 5 боёв.",
        "emoji": "💨",
        "effect": {"speed_buff": 5, "duration": 5},
        "materials": {"rare_herbs": 2, "herbs": 3},
        "level_req": 12,
        "xp": 25,
    },
    "luck_potion": {
        "name": "Зелье удачи",
        "description": "+10 к удаче на 10 боёв.",
        "emoji": "🍀",
        "effect": {"luck_buff": 10, "duration": 10},
        "materials": {"rare_herbs": 4, "pearl": 1},
        "level_req": 18,
        "xp": 45,
    },
    "invisibility_potion": {
        "name": "Зелье невидимости",
        "description": "Позволяет избежать следующей битвы.",
        "emoji": "🫥",
        "effect": {"avoid_combat": True},
        "materials": {"ghost_essence": 2, "rare_herbs": 3},
        "level_req": 25,
        "xp": 60,
    },
    "fire_potion": {
        "name": "Огненное зелье",
        "description": "Наносит 100 доп. урона в следующем бою.",
        "emoji": "🔥",
        "effect": {"fire_damage": 100},
        "materials": {"obsidian": 2, "rare_herbs": 2, "magic_crystal": 1},
        "level_req": 22,
        "xp": 50,
    },
    "kraken_elixir": {
        "name": "Эликсир Кракена",
        "description": "+20 ко всем статам на 3 боя.",
        "emoji": "🐙",
        "effect": {"all_buff": 20, "duration": 3},
        "materials": {"kraken_ink": 1, "rare_herbs": 5, "magic_crystal": 3},
        "level_req": 40,
        "xp": 100,
    },
    "dragon_elixir": {
        "name": "Эликсир Дракона",
        "description": "+30 к атаке, +20 к защите на 5 боёв.",
        "emoji": "🐉",
        "effect": {"attack_buff": 30, "defense_buff": 20, "duration": 5},
        "materials": {"dragon_scale": 1, "rare_herbs": 5, "magic_crystal": 3},
        "level_req": 45,
        "xp": 120,
    },
}


def get_potion(potion_id: str) -> Optional[dict[str, Any]]:
    return POTIONS.get(potion_id)


def can_brew(player: Any, potion_id: str) -> Optional[str]:
    potion = get_potion(potion_id)
    if not potion:
        return "Зелье не найдено."
    if player.level < potion["level_req"]:
        return f"Требуется уровень {potion['level_req']}."
    for mat_id, qty in potion["materials"].items():
        if not has_item(player, mat_id, qty):
            return f"Недостаточно материалов: {mat_id} x{qty}."
    return None


def brew_potion(player: Any, potion_id: str) -> Optional[str]:
    error = can_brew(player, potion_id)
    if error:
        return error
    potion = get_potion(potion_id)
    if not potion:
        return "Зелье не найдено."
    for mat_id, qty in potion["materials"].items():
        remove_from_inventory(player, mat_id, qty)
    add_to_inventory(player, potion_id, 1)
    return None


def use_potion(player: Any, potion_id: str) -> Optional[str]:
    if not has_item(player, potion_id):
        return "У вас нет этого зелья."
    potion = get_potion(potion_id)
    if not potion:
        return "Зелье не найдено."
    effect = potion["effect"]
    if "heal" in effect:
        player.health = min(player.max_health, player.health + effect["heal"])
    if "energy" in effect:
        player.energy = min(player.max_energy, player.energy + effect["energy"])
    # Buffs are tracked in player.active_effects
    buffs: list = player.active_effects if player.active_effects else []
    duration = effect.get("duration", 1)
    for key in ("attack_buff", "defense_buff", "speed_buff", "luck_buff", "all_buff", "fire_damage", "avoid_combat"):
        if key in effect:
            buffs.append({"type": key, "value": effect[key], "remaining": duration})
    player.active_effects = buffs
    remove_from_inventory(player, potion_id, 1)
    return None


def format_potions_list() -> str:
    lines = ["🧪 <b>Алхимия — Зелья:</b>", ""]
    for pid, potion in POTIONS.items():
        lines.append(f"  {potion['emoji']} {potion['name']} (ур. {potion['level_req']})")
        lines.append(f"     📝 {potion['description']}")
        mats = ", ".join(f"{k} x{v}" for k, v in potion["materials"].items())
        lines.append(f"     📋 {mats}")
        lines.append("")
    return "\n".join(lines)
