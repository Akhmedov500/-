from __future__ import annotations

from datetime import datetime
from typing import Any

import config


class EconomySnapshot:
    def __init__(self) -> None:
        self.total_gold_in_circulation: int = 0
        self.total_listings: int = 0
        self.average_listing_price: float = 0.0
        self.total_trades_today: int = 0
        self.inflation_rate: float = 1.0
        self.timestamp: str = datetime.utcnow().isoformat()


def calculate_inflation(total_gold: int, total_players: int) -> float:
    if total_players == 0:
        return 1.0
    avg_gold = total_gold / total_players
    target = config.STARTING_GOLD * 10
    return max(0.5, min(2.0, avg_gold / target))


def adjust_prices(base_price: int, inflation: float) -> int:
    return max(1, int(base_price * inflation))


def calculate_tax(amount: int, tax_type: str = "trade") -> int:
    rates = {
        "trade": config.TRADE_TAX_PERCENT,
        "auction": config.AUCTION_FEE_PERCENT,
        "guild": 2,
    }
    rate = rates.get(tax_type, 5)
    return max(0, int(amount * rate / 100))


def format_economy_stats(snapshot: EconomySnapshot) -> str:
    lines = [
        "📊 <b>Экономика сервера:</b>",
        f"💰 Золото в обращении: {snapshot.total_gold_in_circulation}",
        f"🏪 Активных лотов: {snapshot.total_listings}",
        f"📈 Средняя цена лота: {snapshot.average_listing_price:.0f}",
        f"🔄 Сделок сегодня: {snapshot.total_trades_today}",
        f"📊 Инфляция: x{snapshot.inflation_rate:.2f}",
        f"🕐 Обновлено: {snapshot.timestamp}",
    ]
    return "\n".join(lines)


def get_gold_sinks() -> list[dict[str, Any]]:
    return [
        {"name": "Аукционная комиссия", "rate": f"{config.AUCTION_FEE_PERCENT}%"},
        {"name": "Торговый налог", "rate": f"{config.TRADE_TAX_PERCENT}%"},
        {"name": "Ремонт корабля", "rate": "Зависит от повреждений"},
        {"name": "Улучшения корабля", "rate": "500-3000 золота"},
        {"name": "Покупка кораблей", "rate": "2000-50000 золота"},
        {"name": "Штрафы за контрабанду", "rate": "50% от награды"},
        {"name": "Создание гильдии", "rate": f"{config.GUILD_CREATION_COST} золота"},
    ]
