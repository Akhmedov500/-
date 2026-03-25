from __future__ import annotations

import random
from typing import Any, Optional

from game.world.map import get_island


ISLAND_MONSTERS: dict[str, dict[str, Any]] = {
    "aggressive_fish": {"name": "Агрессивная рыба", "level": 1, "hp": 30, "attack": 5, "defense": 2, "xp": 10, "gold": 5, "loot": ["herbs"]},
    "small_shark": {"name": "Малая акула", "level": 3, "hp": 50, "attack": 8, "defense": 3, "xp": 20, "gold": 10, "loot": ["leather"]},
    "skeleton_pirate": {"name": "Скелет-пират", "level": 5, "hp": 70, "attack": 12, "defense": 5, "xp": 30, "gold": 20, "loot": ["iron_ore", "rusty_cutlass"]},
    "giant_crab": {"name": "Гигантский краб", "level": 5, "hp": 90, "attack": 10, "defense": 12, "xp": 35, "gold": 15, "loot": ["coral"]},
    "wild_boar": {"name": "Дикий кабан", "level": 4, "hp": 60, "attack": 10, "defense": 4, "xp": 25, "gold": 10, "loot": ["leather"]},
    "reef_shark": {"name": "Рифовая акула", "level": 8, "hp": 120, "attack": 18, "defense": 8, "xp": 50, "gold": 30, "loot": ["leather"]},
    "drowned_sailor": {"name": "Утопленник", "level": 8, "hp": 100, "attack": 15, "defense": 6, "xp": 45, "gold": 25, "loot": ["rope", "cloth"]},
    "sea_witch": {"name": "Морская ведьма", "level": 10, "hp": 80, "attack": 22, "defense": 5, "xp": 60, "gold": 40, "loot": ["herbs", "magic_crystal"]},
    "zombie_pirate": {"name": "Зомби-пират", "level": 15, "hp": 150, "attack": 20, "defense": 10, "xp": 70, "gold": 35, "loot": ["ghost_essence"]},
    "voodoo_doll": {"name": "Кукла Вуду", "level": 16, "hp": 60, "attack": 30, "defense": 3, "xp": 65, "gold": 45, "loot": ["rare_herbs"]},
    "swamp_creature": {"name": "Болотное существо", "level": 18, "hp": 200, "attack": 22, "defense": 15, "xp": 80, "gold": 50, "loot": ["herbs", "rare_herbs"]},
    "ghost_pirate": {"name": "Пират-призрак", "level": 20, "hp": 180, "attack": 28, "defense": 12, "xp": 100, "gold": 60, "loot": ["ghost_essence"]},
    "phantom_sailor": {"name": "Фантом-моряк", "level": 22, "hp": 160, "attack": 32, "defense": 10, "xp": 110, "gold": 65, "loot": ["ghost_essence", "magic_crystal"]},
    "banshee": {"name": "Банши", "level": 24, "hp": 130, "attack": 40, "defense": 8, "xp": 120, "gold": 70, "loot": ["ghost_essence"]},
    "shadow_assassin": {"name": "Теневой убийца", "level": 12, "hp": 90, "attack": 25, "defense": 8, "xp": 55, "gold": 40, "loot": ["obsidian"]},
    "dark_corsair": {"name": "Тёмный корсар", "level": 14, "hp": 130, "attack": 22, "defense": 12, "xp": 65, "gold": 45, "loot": ["gunpowder", "iron_ingot"]},
    "corrupted_guardian": {"name": "Падший Страж", "level": 22, "hp": 250, "attack": 30, "defense": 20, "xp": 130, "gold": 80, "loot": ["coral", "magic_crystal"]},
    "sea_serpent": {"name": "Морской Змей", "level": 25, "hp": 300, "attack": 35, "defense": 18, "xp": 150, "gold": 100, "loot": ["dragon_scale"]},
    "jungle_panther": {"name": "Джунглевая пантера", "level": 9, "hp": 80, "attack": 18, "defense": 6, "xp": 40, "gold": 20, "loot": ["leather"]},
    "giant_spider": {"name": "Гигантский паук", "level": 10, "hp": 100, "attack": 16, "defense": 8, "xp": 50, "gold": 25, "loot": ["silk"]},
    "cannibals": {"name": "Каннибалы", "level": 10, "hp": 110, "attack": 14, "defense": 10, "xp": 55, "gold": 30, "loot": ["leather", "herbs"]},
    "jungle_snake": {"name": "Джунглевая змея", "level": 12, "hp": 70, "attack": 20, "defense": 4, "xp": 45, "gold": 20, "loot": ["herbs"]},
    "poison_frog": {"name": "Ядовитая лягушка", "level": 13, "hp": 40, "attack": 25, "defense": 2, "xp": 40, "gold": 30, "loot": ["rare_herbs"]},
    "stone_golem": {"name": "Каменный голем", "level": 16, "hp": 300, "attack": 20, "defense": 25, "xp": 90, "gold": 50, "loot": ["iron_ore", "obsidian"]},
    "trap_skeleton": {"name": "Скелет-ловушка", "level": 15, "hp": 100, "attack": 22, "defense": 8, "xp": 70, "gold": 40, "loot": ["gold_ore"]},
    "cursed_warrior": {"name": "Проклятый воин", "level": 18, "hp": 200, "attack": 28, "defense": 15, "xp": 100, "gold": 60, "loot": ["magic_crystal", "obsidian"]},
    "fire_elemental": {"name": "Огненный элементаль", "level": 25, "hp": 220, "attack": 40, "defense": 12, "xp": 140, "gold": 80, "loot": ["obsidian"]},
    "lava_crab": {"name": "Лавовый краб", "level": 26, "hp": 280, "attack": 30, "defense": 28, "xp": 130, "gold": 70, "loot": ["obsidian", "iron_ore"]},
    "magma_serpent": {"name": "Магма-змей", "level": 28, "hp": 250, "attack": 38, "defense": 15, "xp": 150, "gold": 90, "loot": ["dragon_scale"]},
    "tentacle_horror": {"name": "Щупальцевый ужас", "level": 35, "hp": 400, "attack": 45, "defense": 20, "xp": 200, "gold": 120, "loot": ["kraken_ink"]},
    "deep_one": {"name": "Глубоководный", "level": 38, "hp": 350, "attack": 50, "defense": 18, "xp": 220, "gold": 130, "loot": ["kraken_ink", "magic_crystal"]},
    "abyss_lurker": {"name": "Обитатель Бездны", "level": 40, "hp": 500, "attack": 55, "defense": 25, "xp": 250, "gold": 150, "loot": ["kraken_ink", "dragon_scale"]},
    "fog_wraith": {"name": "Туманный призрак", "level": 18, "hp": 150, "attack": 25, "defense": 10, "xp": 80, "gold": 50, "loot": ["ghost_essence"]},
    "mist_serpent": {"name": "Туманный змей", "level": 20, "hp": 200, "attack": 28, "defense": 14, "xp": 100, "gold": 60, "loot": ["magic_crystal"]},
    "ghost_crab": {"name": "Краб-призрак", "level": 19, "hp": 180, "attack": 20, "defense": 20, "xp": 90, "gold": 55, "loot": ["ghost_essence", "coral"]},
    "frost_giant": {"name": "Ледяной великан", "level": 32, "hp": 500, "attack": 40, "defense": 30, "xp": 200, "gold": 120, "loot": ["iron_ore", "magic_crystal"]},
    "ice_elemental": {"name": "Ледяной элементаль", "level": 30, "hp": 300, "attack": 35, "defense": 20, "xp": 170, "gold": 100, "loot": ["magic_crystal"]},
    "polar_bear": {"name": "Полярный медведь", "level": 30, "hp": 350, "attack": 30, "defense": 25, "xp": 160, "gold": 80, "loot": ["leather"]},
    "giant_jellyfish": {"name": "Гигантская медуза", "level": 10, "hp": 100, "attack": 15, "defense": 5, "xp": 45, "gold": 25, "loot": ["pearl"]},
    "electric_eel": {"name": "Электрический угорь", "level": 12, "hp": 70, "attack": 22, "defense": 4, "xp": 50, "gold": 30, "loot": ["magic_crystal"]},
    "cursed_pirate": {"name": "Проклятый пират", "level": 25, "hp": 250, "attack": 32, "defense": 15, "xp": 140, "gold": 85, "loot": ["ghost_essence", "obsidian"]},
    "shadow_beast": {"name": "Теневой зверь", "level": 27, "hp": 280, "attack": 38, "defense": 18, "xp": 160, "gold": 95, "loot": ["obsidian"]},
    "dark_mage": {"name": "Тёмный маг", "level": 26, "hp": 180, "attack": 45, "defense": 10, "xp": 170, "gold": 100, "loot": ["magic_crystal", "rare_herbs"]},
    "water_elemental": {"name": "Водный элементаль", "level": 30, "hp": 280, "attack": 32, "defense": 18, "xp": 160, "gold": 90, "loot": ["pearl", "magic_crystal"]},
    "temple_guardian": {"name": "Страж Храма", "level": 32, "hp": 400, "attack": 35, "defense": 28, "xp": 190, "gold": 110, "loot": ["magic_crystal", "gold_ingot"]},
    "siren": {"name": "Сирена", "level": 30, "hp": 200, "attack": 42, "defense": 12, "xp": 180, "gold": 100, "loot": ["pearl", "coral"]},
    "drake": {"name": "Дракончик", "level": 40, "hp": 450, "attack": 50, "defense": 25, "xp": 250, "gold": 150, "loot": ["dragon_scale"]},
    "dragon_hatchling": {"name": "Детёныш дракона", "level": 42, "hp": 500, "attack": 55, "defense": 28, "xp": 280, "gold": 170, "loot": ["dragon_scale", "magic_crystal"]},
    "berserker": {"name": "Берсерк", "level": 35, "hp": 350, "attack": 50, "defense": 15, "xp": 200, "gold": 120, "loot": ["iron_ingot", "leather"]},
    "shield_maiden": {"name": "Щитоносица", "level": 36, "hp": 300, "attack": 35, "defense": 35, "xp": 210, "gold": 110, "loot": ["iron_ingot"]},
    "war_troll": {"name": "Боевой тролль", "level": 38, "hp": 600, "attack": 45, "defense": 30, "xp": 250, "gold": 140, "loot": ["leather", "iron_ingot"]},
    "dimensional_horror": {"name": "Измерительный ужас", "level": 42, "hp": 550, "attack": 55, "defense": 22, "xp": 300, "gold": 180, "loot": ["magic_crystal", "ghost_essence"]},
    "void_walker": {"name": "Странник Пустоты", "level": 44, "hp": 480, "attack": 60, "defense": 20, "xp": 320, "gold": 200, "loot": ["black_pearl", "magic_crystal"]},
    "abyss_horror": {"name": "Ужас Бездны", "level": 50, "hp": 800, "attack": 70, "defense": 35, "xp": 500, "gold": 300, "loot": ["kraken_ink", "black_pearl"]},
    "deep_kraken": {"name": "Глубоководный кракен", "level": 52, "hp": 1000, "attack": 75, "defense": 30, "xp": 550, "gold": 350, "loot": ["kraken_ink", "dragon_scale"]},
    "chaos_elemental": {"name": "Элементаль Хаоса", "level": 55, "hp": 700, "attack": 80, "defense": 25, "xp": 600, "gold": 400, "loot": ["black_pearl", "dragon_scale"]},
}

BOSSES: dict[str, dict[str, Any]] = {
    "skeleton_captain": {"name": "Капитан Скелетов", "level": 10, "hp": 500, "attack": 25, "defense": 15, "xp": 200, "gold": 300, "loot": ["iron_cutlass", "skeleton_key"], "island": "skull_island"},
    "ghost_ship_captain": {"name": "Капитан Корабля-Призрака", "level": 15, "hp": 700, "attack": 30, "defense": 18, "xp": 350, "gold": 500, "loot": ["ghost_essence", "shadow_dagger"], "island": "dead_mans_reef"},
    "baron_samedi": {"name": "Барон Самеди", "level": 22, "hp": 900, "attack": 40, "defense": 20, "xp": 500, "gold": 700, "loot": ["rare_herbs", "magic_crystal", "cursed_medallion"], "island": "voodoo_isle"},
    "ghost_admiral": {"name": "Призрачный Адмирал", "level": 28, "hp": 1200, "attack": 45, "defense": 25, "xp": 700, "gold": 1000, "loot": ["ghost_essence", "kraken_fang"], "island": "ghost_island"},
    "leviathan": {"name": "Левиафан", "level": 30, "hp": 1500, "attack": 50, "defense": 30, "xp": 900, "gold": 1200, "loot": ["dragon_scale", "magic_crystal"], "island": "coral_citadel"},
    "ancient_king": {"name": "Древний Король", "level": 25, "hp": 1000, "attack": 42, "defense": 28, "xp": 600, "gold": 800, "loot": ["ancient_coin", "golden_blade"], "island": "ancient_ruins"},
    "jungle_titan": {"name": "Титан Джунглей", "level": 15, "hp": 600, "attack": 28, "defense": 20, "xp": 300, "gold": 400, "loot": ["leather", "rare_herbs"], "island": "jungle_island"},
    "volcanic_dragon": {"name": "Вулканический Дракон", "level": 35, "hp": 2000, "attack": 60, "defense": 35, "xp": 1200, "gold": 2000, "loot": ["dragon_scale", "obsidian"], "island": "volcano_island"},
    "elder_sea_dragon": {"name": "Древний Морской Дракон", "level": 50, "hp": 3000, "attack": 80, "defense": 40, "xp": 2000, "gold": 5000, "loot": ["dragon_scale", "blade_of_the_deep"], "island": "dragon_peak"},
    "kraken": {"name": "Кракен", "level": 45, "hp": 2500, "attack": 70, "defense": 35, "xp": 1500, "gold": 3000, "loot": ["kraken_ink", "kraken_fang", "black_pearl"], "island": "abyss_island"},
    "ancient_kraken": {"name": "Древний Кракен", "level": 60, "hp": 5000, "attack": 100, "defense": 50, "xp": 5000, "gold": 10000, "loot": ["poseidons_trident", "black_pearl"], "island": "maelstrom"},
    "fog_giant": {"name": "Туманный Великан", "level": 25, "hp": 1100, "attack": 38, "defense": 22, "xp": 550, "gold": 700, "loot": ["ghost_essence", "magic_crystal"], "island": "misty_archipelago"},
    "ice_king": {"name": "Ледяной Король", "level": 38, "hp": 1800, "attack": 55, "defense": 35, "xp": 1000, "gold": 1500, "loot": ["magic_crystal", "iron_ingot"], "island": "frozen_coast"},
    "viking_king": {"name": "Король Викингов", "level": 42, "hp": 2200, "attack": 65, "defense": 38, "xp": 1300, "gold": 2000, "loot": ["stormbringer", "iron_ingot"], "island": "viking_stronghold"},
    "curse_lord": {"name": "Лорд Проклятий", "level": 35, "hp": 1600, "attack": 52, "defense": 25, "xp": 900, "gold": 1200, "loot": ["cursed_medallion", "ghost_essence"], "island": "cursed_atoll"},
    "poseidon_avatar": {"name": "Аватар Посейдона", "level": 45, "hp": 3500, "attack": 85, "defense": 45, "xp": 2500, "gold": 5000, "loot": ["poseidons_trident", "pearl"], "island": "sunken_temple"},
    "gate_guardian": {"name": "Страж Врат", "level": 48, "hp": 2800, "attack": 75, "defense": 40, "xp": 2000, "gold": 4000, "loot": ["black_pearl", "magic_crystal"], "island": "whirlpool_gates"},
}


def get_monster(monster_id: str) -> Optional[dict[str, Any]]:
    return ISLAND_MONSTERS.get(monster_id)


def get_boss(boss_id: str) -> Optional[dict[str, Any]]:
    return BOSSES.get(boss_id)


def get_island_monsters(island_id: str) -> list[dict[str, Any]]:
    island = get_island(island_id)
    if not island:
        return []
    monsters = []
    for mid in island.get("monsters", []):
        m = get_monster(mid)
        if m:
            monsters.append({**m, "id": mid})
    return monsters


def get_random_encounter(island_id: str) -> Optional[dict[str, Any]]:
    monsters = get_island_monsters(island_id)
    if not monsters:
        return None
    return random.choice(monsters)


def gather_resources(island_id: str, player_luck: int = 5) -> list[dict[str, Any]]:
    island = get_island(island_id)
    if not island:
        return []
    resources = island.get("resources", [])
    if not resources:
        return []
    gathered = []
    count = random.randint(1, 3) + (player_luck // 10)
    for _ in range(count):
        res = random.choice(resources)
        gathered.append({"id": res, "qty": 1})
    return gathered
