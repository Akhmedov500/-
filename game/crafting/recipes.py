from __future__ import annotations

from typing import Any, Optional


RECIPES: dict[str, dict[str, Any]] = {
    # Weapons
    "iron_cutlass": {"name": "Железный абордажник", "category": "weapon", "materials": {"iron_ingot": 3, "wood": 2, "leather": 1}, "result_qty": 1, "level_req": 5, "xp": 20},
    "steel_cutlass": {"name": "Стальной абордажник", "category": "weapon", "materials": {"iron_ingot": 5, "wood": 2, "coal": 3}, "result_qty": 1, "level_req": 15, "xp": 50},
    "golden_blade": {"name": "Золотой клинок", "category": "weapon", "materials": {"gold_ingot": 5, "iron_ingot": 3, "magic_crystal": 1}, "result_qty": 1, "level_req": 25, "xp": 100},
    "shadow_dagger": {"name": "Теневой кинжал", "category": "weapon", "materials": {"obsidian": 5, "ghost_essence": 3, "iron_ingot": 2}, "result_qty": 1, "level_req": 20, "xp": 80},
    "stormbringer": {"name": "Буреносец", "category": "weapon", "materials": {"iron_ingot": 10, "magic_crystal": 5, "dragon_scale": 2}, "result_qty": 1, "level_req": 40, "xp": 200},
    # Armor
    "leather_armor": {"name": "Кожаная броня", "category": "armor", "materials": {"leather": 5, "cloth": 3}, "result_qty": 1, "level_req": 3, "xp": 15},
    "iron_armor": {"name": "Железная броня", "category": "armor", "materials": {"iron_ingot": 5, "leather": 3, "cloth": 2}, "result_qty": 1, "level_req": 10, "xp": 40},
    "steel_armor": {"name": "Стальная броня", "category": "armor", "materials": {"iron_ingot": 8, "coal": 5, "leather": 3}, "result_qty": 1, "level_req": 20, "xp": 80},
    "dragon_armor": {"name": "Драконья броня", "category": "armor", "materials": {"dragon_scale": 5, "iron_ingot": 8, "magic_crystal": 3}, "result_qty": 1, "level_req": 45, "xp": 250},
    # Consumables
    "bandage": {"name": "Бинт", "category": "consumable", "materials": {"cloth": 2, "herbs": 1}, "result_qty": 3, "level_req": 1, "xp": 5},
    "health_potion": {"name": "Зелье здоровья", "category": "consumable", "materials": {"herbs": 3, "rare_herbs": 1}, "result_qty": 1, "level_req": 5, "xp": 15},
    "energy_potion": {"name": "Зелье энергии", "category": "consumable", "materials": {"herbs": 2, "rare_herbs": 2}, "result_qty": 1, "level_req": 8, "xp": 20},
    "strength_potion": {"name": "Зелье силы", "category": "consumable", "materials": {"rare_herbs": 3, "magic_crystal": 1}, "result_qty": 1, "level_req": 15, "xp": 40},
    # Ship materials
    "iron_ingot": {"name": "Железный слиток", "category": "material", "materials": {"iron_ore": 3, "coal": 1}, "result_qty": 1, "level_req": 1, "xp": 5},
    "gold_ingot": {"name": "Золотой слиток", "category": "material", "materials": {"gold_ore": 3}, "result_qty": 1, "level_req": 10, "xp": 15},
    "gunpowder": {"name": "Порох", "category": "material", "materials": {"coal": 2, "iron_ore": 1}, "result_qty": 2, "level_req": 5, "xp": 10},
    "rope": {"name": "Верёвка", "category": "material", "materials": {"cloth": 3}, "result_qty": 2, "level_req": 1, "xp": 3},
    "cannonball": {"name": "Ядро", "category": "ammo", "materials": {"iron_ingot": 1}, "result_qty": 5, "level_req": 5, "xp": 8},
    "explosive_cannonball": {"name": "Взрывное ядро", "category": "ammo", "materials": {"iron_ingot": 2, "gunpowder": 3}, "result_qty": 3, "level_req": 15, "xp": 25},
    # Jewelry
    "pearl_necklace": {"name": "Жемчужное ожерелье", "category": "jewelry", "materials": {"pearl": 5, "gold_ingot": 1}, "result_qty": 1, "level_req": 15, "xp": 40},
    "coral_amulet": {"name": "Коралловый амулет", "category": "jewelry", "materials": {"coral": 5, "magic_crystal": 2}, "result_qty": 1, "level_req": 20, "xp": 60},
    "obsidian_ring": {"name": "Обсидиановое кольцо", "category": "jewelry", "materials": {"obsidian": 3, "gold_ingot": 1}, "result_qty": 1, "level_req": 18, "xp": 50},
    "black_pearl_amulet": {"name": "Амулет чёрной жемчужины", "category": "jewelry", "materials": {"black_pearl": 1, "gold_ingot": 3, "magic_crystal": 5}, "result_qty": 1, "level_req": 40, "xp": 200},
    # Food
    "cooked_fish": {"name": "Жареная рыба", "category": "food", "materials": {"herbs": 1}, "result_qty": 1, "level_req": 1, "xp": 3},
    "rum_cocktail": {"name": "Ромовый коктейль", "category": "food", "materials": {"herbs": 2}, "result_qty": 1, "level_req": 5, "xp": 8},
    "feast": {"name": "Пиршество", "category": "food", "materials": {"herbs": 5, "rare_herbs": 2}, "result_qty": 1, "level_req": 15, "xp": 30},
}


def get_recipe(recipe_id: str) -> Optional[dict[str, Any]]:
    return RECIPES.get(recipe_id)


def can_craft(player: Any, recipe_id: str) -> Optional[str]:
    recipe = get_recipe(recipe_id)
    if not recipe:
        return "Рецепт не найден."
    if player.level < recipe["level_req"]:
        return f"Требуется уровень {recipe['level_req']}."
    from game.core.player import has_item
    for mat_id, qty in recipe["materials"].items():
        if not has_item(player, mat_id, qty):
            return f"Недостаточно материалов: {mat_id} x{qty}."
    return None


def craft_item(player: Any, recipe_id: str) -> Optional[str]:
    error = can_craft(player, recipe_id)
    if error:
        return error
    recipe = get_recipe(recipe_id)
    if not recipe:
        return "Рецепт не найден."
    from game.core.player import remove_from_inventory, add_to_inventory
    for mat_id, qty in recipe["materials"].items():
        remove_from_inventory(player, mat_id, qty)
    add_to_inventory(player, recipe_id, recipe["result_qty"])
    return None


def format_recipe(recipe_id: str) -> str:
    recipe = get_recipe(recipe_id)
    if not recipe:
        return "Рецепт не найден."
    lines = [
        f"🔧 <b>{recipe['name']}</b>",
        f"📊 Категория: {recipe['category']}",
        f"📊 Мин. уровень: {recipe['level_req']}",
        f"📊 XP за крафт: {recipe['xp']}",
        f"📦 Результат: x{recipe['result_qty']}",
        "",
        "📋 <b>Материалы:</b>",
    ]
    for mat_id, qty in recipe["materials"].items():
        lines.append(f"  • {mat_id} x{qty}")
    return "\n".join(lines)


def format_recipe_list(category: Optional[str] = None) -> str:
    lines = ["🔧 <b>Рецепты крафта:</b>", ""]
    for rid, recipe in RECIPES.items():
        if category and recipe["category"] != category:
            continue
        lines.append(f"  🔹 {recipe['name']} (ур. {recipe['level_req']})")
    if len(lines) <= 2:
        return "Рецепты не найдены."
    return "\n".join(lines)
