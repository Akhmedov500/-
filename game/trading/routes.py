from __future__ import annotations

import random
from typing import Any, Optional

from game.core.economy import get_trade_price
from game.world.map import get_island


TRADE_ROUTES: list[dict[str, Any]] = [
    {"id": "rum_run", "name": "Ромовый путь", "from": "tortuga", "to": "port_royal", "goods": ["rum"], "danger": 0.1, "level_req": 1},
    {"id": "spice_trade", "name": "Торговля пряностями", "from": "spice_islands", "to": "havana", "goods": ["spices"], "danger": 0.15, "level_req": 5},
    {"id": "silk_road", "name": "Шёлковый путь", "from": "havana", "to": "nassau", "goods": ["silk_goods"], "danger": 0.2, "level_req": 10},
    {"id": "weapons_run", "name": "Оружейный маршрут", "from": "port_royal", "to": "tortuga", "goods": ["weapons_cargo"], "danger": 0.25, "level_req": 15},
    {"id": "pearl_route", "name": "Жемчужный маршрут", "from": "pearl_lagoon", "to": "havana", "goods": ["pearls_cargo"], "danger": 0.2, "level_req": 12},
    {"id": "medicine_route", "name": "Маршрут лекарств", "from": "voodoo_isle", "to": "port_royal", "goods": ["medicine"], "danger": 0.15, "level_req": 8},
    {"id": "gold_convoy", "name": "Золотой конвой", "from": "havana", "to": "port_royal", "goods": ["gold_cargo"], "danger": 0.35, "level_req": 20},
    {"id": "artifact_trade", "name": "Торговля артефактами", "from": "ancient_ruins", "to": "coral_citadel", "goods": ["magical_artifacts"], "danger": 0.4, "level_req": 25},
]


def get_route(route_id: str) -> Optional[dict[str, Any]]:
    for route in TRADE_ROUTES:
        if route["id"] == route_id:
            return route
    return None


def get_available_routes(player_level: int) -> list[dict[str, Any]]:
    return [r for r in TRADE_ROUTES if player_level >= r["level_req"]]


def calculate_route_profit(route: dict[str, Any]) -> dict[str, Any]:
    total_buy = 0
    total_sell = 0
    for good_id in route["goods"]:
        buy = get_trade_price(good_id, route["from"], is_buy=True)
        sell = get_trade_price(good_id, route["to"], is_buy=False)
        total_buy += buy
        total_sell += sell
    profit = total_sell - total_buy
    return {"buy_cost": total_buy, "sell_price": total_sell, "profit": profit}


def run_trade_route(player: Any, route_id: str) -> tuple[bool, int, str]:
    route = get_route(route_id)
    if not route:
        return False, 0, "Маршрут не найден."
    if player.level < route["level_req"]:
        return False, 0, f"Требуется уровень {route['level_req']}."
    if player.current_island != route["from"]:
        from_island = get_island(route["from"])
        name = from_island["name"] if from_island else route["from"]
        return False, 0, f"Вы должны быть на острове: {name}."

    profit_data = calculate_route_profit(route)
    buy_cost = profit_data["buy_cost"]
    if player.gold < buy_cost:
        return False, 0, f"Недостаточно золота. Нужно: {buy_cost}."

    danger = route["danger"] - (player.luck * 0.005)
    danger = max(0.05, danger)

    if random.random() < danger:
        loss = buy_cost // 2
        player.gold -= loss
        return False, -loss, f"⚠️ Вы были атакованы пиратами на маршруте! Потеряно: {loss} 💰"

    profit = profit_data["profit"]
    bonus = int(profit * (player.luck * 0.01))
    total_profit = profit + bonus
    player.gold += total_profit
    player.current_island = route["to"]
    return True, total_profit, f"✅ Маршрут завершён! Прибыль: {total_profit} 💰"


def format_routes(player_level: int) -> str:
    routes = get_available_routes(player_level)
    if not routes:
        return "🚢 Нет доступных торговых маршрутов."
    lines = ["🚢 <b>Торговые маршруты:</b>", ""]
    for route in routes:
        from_isl = get_island(route["from"])
        to_isl = get_island(route["to"])
        from_name = from_isl["name"] if from_isl else route["from"]
        to_name = to_isl["name"] if to_isl else route["to"]
        profit_data = calculate_route_profit(route)
        danger_pct = int(route["danger"] * 100)
        lines.append(f"  🔹 {route['name']}")
        lines.append(f"     📍 {from_name} → {to_name}")
        lines.append(f"     💰 Прибыль: ~{profit_data['profit']}  |  ⚠️ Опасность: {danger_pct}%")
        lines.append(f"     📊 Мин. уровень: {route['level_req']}")
        lines.append("")
    return "\n".join(lines)
