from __future__ import annotations

from typing import Any, Optional


MATERIALS: dict[str, dict[str, Any]] = {
    "wood": {"name": "Дерево", "emoji": "🪵", "tier": 1, "description": "Базовый строительный материал."},
    "iron_ore": {"name": "Железная руда", "emoji": "⛏️", "tier": 1, "description": "Необработанная железная руда."},
    "coal": {"name": "Уголь", "emoji": "�ite", "tier": 1, "description": "Топливо для плавки."},
    "cloth": {"name": "Ткань", "emoji": "🧵", "tier": 1, "description": "Ткань для парусов и одежды."},
    "leather": {"name": "Кожа", "emoji": "🐂", "tier": 1, "description": "Кожа для брони и ремней."},
    "herbs": {"name": "Травы", "emoji": "🌿", "tier": 1, "description": "Обычные травы для зелий."},
    "rope": {"name": "Верёвка", "emoji": "🧶", "tier": 1, "description": "Прочная верёвка для кораблей."},
    "iron_ingot": {"name": "Железный слиток", "emoji": "🔩", "tier": 2, "description": "Обработанное железо."},
    "gold_ore": {"name": "Золотая руда", "emoji": "🪨", "tier": 2, "description": "Необработанное золото."},
    "gold_ingot": {"name": "Золотой слиток", "emoji": "🥇", "tier": 3, "description": "Обработанное золото."},
    "silk": {"name": "Шёлк", "emoji": "🕸️", "tier": 2, "description": "Тонкий шёлк для парусов."},
    "rare_herbs": {"name": "Редкие травы", "emoji": "🌺", "tier": 2, "description": "Редкие травы для алхимии."},
    "gunpowder": {"name": "Порох", "emoji": "💣", "tier": 2, "description": "Порох для пушек."},
    "coral": {"name": "Коралл", "emoji": "🪸", "tier": 2, "description": "Морской коралл."},
    "pearl": {"name": "Жемчуг", "emoji": "🦪", "tier": 3, "description": "Ценная жемчужина."},
    "obsidian": {"name": "Обсидиан", "emoji": "🖤", "tier": 3, "description": "Тёмное вулканическое стекло."},
    "magic_crystal": {"name": "Магический кристалл", "emoji": "💎", "tier": 3, "description": "Кристалл, наполненный магией."},
    "ghost_essence": {"name": "Эссенция призрака", "emoji": "👻", "tier": 3, "description": "Призрачная субстанция."},
    "dragon_scale": {"name": "Чешуя дракона", "emoji": "🐉", "tier": 4, "description": "Легендарная чешуя дракона."},
    "kraken_ink": {"name": "Чернила Кракена", "emoji": "🐙", "tier": 4, "description": "Чернила из щупальца Кракена."},
    "black_pearl": {"name": "Чёрная жемчужина", "emoji": "⚫", "tier": 5, "description": "Невероятно редкая чёрная жемчужина."},
    "ancient_coin": {"name": "Древняя монета", "emoji": "🪙", "tier": 3, "description": "Монета из затерянной цивилизации."},
}


def get_material(material_id: str) -> Optional[dict[str, Any]]:
    return MATERIALS.get(material_id)


def format_material(material_id: str) -> str:
    mat = get_material(material_id)
    if not mat:
        return "Материал не найден."
    return f"{mat['emoji']} <b>{mat['name']}</b> (тир {mat['tier']})\n📝 {mat['description']}"


def format_materials_list() -> str:
    lines = ["⛏️ <b>Материалы:</b>", ""]
    by_tier: dict[int, list[str]] = {}
    for mid, mat in MATERIALS.items():
        tier = mat["tier"]
        if tier not in by_tier:
            by_tier[tier] = []
        by_tier[tier].append(f"  {mat['emoji']} {mat['name']}")
    for tier in sorted(by_tier.keys()):
        lines.append(f"⭐ <b>Тир {tier}:</b>")
        lines.extend(by_tier[tier])
        lines.append("")
    return "\n".join(lines)
