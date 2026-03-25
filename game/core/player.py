from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import config

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_items() -> dict[str, Any]:
    with open(DATA_DIR / "items.json", encoding="utf-8") as f:
        return json.load(f)


ALL_ITEMS = None


def _items() -> dict[str, Any]:
    global ALL_ITEMS
    if ALL_ITEMS is None:
        raw = load_items()
        flat: dict[str, Any] = {}
        for category in raw.values():
            flat.update(category)
        ALL_ITEMS = flat
    return ALL_ITEMS


def get_item(item_id: str) -> Optional[dict[str, Any]]:
    return _items().get(item_id)


def xp_for_level(level: int) -> int:
    return int(config.XP_PER_LEVEL_BASE * (config.XP_PER_LEVEL_MULTIPLIER ** (level - 1)))


def format_player_stats(player: Any) -> str:
    faction_name = player.faction_id or "Нет"
    lines = [
        f"🏴‍☠️ <b>{player.display_name}</b>",
        f"📊 Уровень: {player.level}  |  XP: {player.xp}/{xp_for_level(player.level + 1)}",
        f"❤️ HP: {player.health}/{player.max_health}",
        f"⚡ Энергия: {player.energy}/{player.max_energy}",
        f"💰 Золото: {player.gold}",
        f"⚔️ Атака: {player.attack}  |  🛡 Защита: {player.defense}",
        f"💨 Скорость: {player.speed}  |  🍀 Удача: {player.luck}",
        f"🏝️ Остров: {player.current_island}",
        f"⚓ Фракция: {faction_name}",
        f"🎯 PVP рейтинг: {player.pvp_rating}",
        f"📦 Инвентарь: {len(player.inventory or [])}/{config.MAX_INVENTORY_SIZE}",
    ]
    return "\n".join(lines)


def format_inventory(player: Any) -> str:
    inventory = player.inventory or []
    if not inventory:
        return "📦 Инвентарь пуст."
    lines = ["📦 <b>Инвентарь:</b>"]
    for i, entry in enumerate(inventory, 1):
        item_id = entry.get("id", "") if isinstance(entry, dict) else entry
        qty = entry.get("qty", 1) if isinstance(entry, dict) else 1
        item = get_item(item_id)
        name = item["name"] if item else item_id
        lines.append(f"  {i}. {name} x{qty}")
    return "\n".join(lines)


def add_to_inventory(player: Any, item_id: str, quantity: int = 1) -> bool:
    inventory: list = player.inventory if player.inventory else []
    if len(inventory) >= config.MAX_INVENTORY_SIZE:
        return False
    for entry in inventory:
        if isinstance(entry, dict) and entry.get("id") == item_id:
            entry["qty"] = entry.get("qty", 1) + quantity
            player.inventory = inventory
            return True
    inventory.append({"id": item_id, "qty": quantity})
    player.inventory = inventory
    return True


def remove_from_inventory(player: Any, item_id: str, quantity: int = 1) -> bool:
    inventory: list = player.inventory if player.inventory else []
    for entry in inventory:
        if isinstance(entry, dict) and entry.get("id") == item_id:
            current = entry.get("qty", 1)
            if current < quantity:
                return False
            entry["qty"] = current - quantity
            if entry["qty"] <= 0:
                inventory.remove(entry)
            player.inventory = inventory
            return True
    return False


def has_item(player: Any, item_id: str, quantity: int = 1) -> bool:
    inventory: list = player.inventory if player.inventory else []
    for entry in inventory:
        if isinstance(entry, dict) and entry.get("id") == item_id:
            return entry.get("qty", 1) >= quantity
    return False


def equip_item(player: Any, item_id: str) -> Optional[str]:
    item = get_item(item_id)
    if not item:
        return "Предмет не найден."
    if not has_item(player, item_id):
        return "У вас нет этого предмета."
    item_type = item.get("type", "")
    if item_type not in ("weapon", "armor"):
        return "Этот предмет нельзя экипировать."
    if player.level < item.get("level_req", 1):
        return f"Требуется уровень {item['level_req']}."
    equipped: dict = player.equipped_items if player.equipped_items else {}
    slot = "weapon" if item_type == "weapon" else "armor"
    old = equipped.get(slot)
    if old:
        add_to_inventory(player, old)
        if item_type == "weapon":
            old_item = get_item(old)
            if old_item:
                player.attack -= old_item.get("attack", 0)
        elif item_type == "armor":
            old_item = get_item(old)
            if old_item:
                player.defense -= old_item.get("defense", 0)
    remove_from_inventory(player, item_id)
    equipped[slot] = item_id
    player.equipped_items = equipped
    if item_type == "weapon":
        player.attack += item.get("attack", 0)
    elif item_type == "armor":
        player.defense += item.get("defense", 0)
    return None
