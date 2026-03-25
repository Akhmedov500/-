from __future__ import annotations

import random
from typing import Any

import config


TRADE_GOODS: dict[str, dict[str, Any]] = {
    "rum": {"name": "Ром", "base_price": 30, "emoji": "🍺", "origin": ["tortuga", "nassau"]},
    "spices": {"name": "Пряности", "base_price": 60, "emoji": "🌶️", "origin": ["spice_islands"]},
    "silk_goods": {"name": "Шёлковые товары", "base_price": 80, "emoji": "🧵", "origin": ["havana"]},
    "weapons_cargo": {"name": "Оружейный груз", "base_price": 100, "emoji": "⚔️", "origin": ["port_royal"]},
    "exotic_fruits": {"name": "Экзотические фрукты", "base_price": 40, "emoji": "🍍", "origin": ["jungle_island"]},
    "pearls_cargo": {"name": "Партия жемчуга", "base_price": 120, "emoji": "🦪", "origin": ["pearl_lagoon", "mermaid_cove"]},
    "gunpowder_barrel": {"name": "Бочка пороха", "base_price": 70, "emoji": "💣", "origin": ["port_royal", "tortuga"]},
    "medicine": {"name": "Лекарства", "base_price": 90, "emoji": "💊", "origin": ["voodoo_isle"]},
    "gold_cargo": {"name": "Золотой груз", "base_price": 200, "emoji": "💰", "origin": ["havana"]},
    "magical_artifacts": {"name": "Магические артефакты", "base_price": 250, "emoji": "🔮", "origin": ["coral_citadel", "ancient_ruins"]},
}


def get_trade_price(good_id: str, island_id: str, is_buy: bool = True) -> int:
    good = TRADE_GOODS.get(good_id)
    if not good:
        return 0
    base = good["base_price"]
    # Price is lower at origin islands
    if island_id in good.get("origin", []):
        modifier = random.uniform(0.7, 0.9) if is_buy else random.uniform(0.5, 0.7)
    else:
        modifier = random.uniform(1.1, 1.5) if is_buy else random.uniform(0.9, 1.3)
    price = int(base * modifier)
    if not is_buy:
        price = int(price * (1 - config.TRADE_TAX_PERCENT / 100))
    return max(1, price)


def calculate_auction_fee(price: int) -> int:
    return int(price * config.AUCTION_FEE_PERCENT / 100)


def get_smuggling_goods() -> list[dict[str, Any]]:
    goods = [
        {"id": "contraband_rum", "name": "Контрабандный ром", "risk": 0.2, "reward": 500, "emoji": "🍺"},
        {"id": "stolen_artifacts", "name": "Краденые артефакты", "risk": 0.35, "reward": 1000, "emoji": "🏺"},
        {"id": "forbidden_weapons", "name": "Запрещённое оружие", "risk": 0.45, "reward": 1500, "emoji": "🗡️"},
        {"id": "dark_magic_items", "name": "Тёмные магические предметы", "risk": 0.5, "reward": 2000, "emoji": "🔮"},
        {"id": "cursed_treasure", "name": "Проклятое сокровище", "risk": 0.6, "reward": 3000, "emoji": "💀"},
    ]
    return goods


def attempt_smuggling(player: Any, good: dict[str, Any]) -> tuple[bool, int, str]:
    risk = good["risk"] - (player.luck * 0.005)
    risk = max(0.05, min(0.9, risk))

    skills: dict = player.skills if player.skills else {}
    smuggler_level = skills.get("smuggler", 0)
    risk -= smuggler_level * 0.05

    if random.random() > risk:
        reward = good["reward"]
        bonus = int(reward * (player.luck * 0.01))
        total = reward + bonus
        return True, total, f"✅ Контрабанда доставлена! Награда: {total} 💰"
    else:
        fine = good["reward"] // 2
        return False, -fine, f"❌ Вас поймали! Штраф: {fine} 💰"


def format_trade_goods(island_id: str) -> str:
    lines = ["🏪 <b>Торговые товары:</b>", ""]
    for good_id, good in TRADE_GOODS.items():
        buy_price = get_trade_price(good_id, island_id, is_buy=True)
        sell_price = get_trade_price(good_id, island_id, is_buy=False)
        is_origin = island_id in good.get("origin", [])
        tag = " 📍" if is_origin else ""
        lines.append(
            f"{good['emoji']} {good['name']}{tag}\n"
            f"   Покупка: {buy_price} 💰 | Продажа: {sell_price} 💰"
        )
    return "\n".join(lines)
