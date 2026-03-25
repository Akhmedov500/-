from __future__ import annotations

from typing import Any, Optional

import config
from game.core.player import get_item


def create_listing(player: Any, item_id: str, quantity: int, price: int) -> Optional[str]:
    item = get_item(item_id)
    if not item:
        return "Предмет не найден."
    from game.core.player import has_item, remove_from_inventory
    if not has_item(player, item_id, quantity):
        return "Недостаточно предметов."
    if price < 1:
        return "Цена должна быть положительной."
    fee = int(price * config.AUCTION_FEE_PERCENT / 100)
    if player.gold < fee:
        return f"Недостаточно золота для оплаты комиссии ({fee} 💰)."
    remove_from_inventory(player, item_id, quantity)
    player.gold -= fee
    return None


def buy_listing(buyer: Any, listing: Any, seller_gold_callback: Any = None) -> Optional[str]:
    if buyer.telegram_id == listing.seller_id:
        return "Нельзя купить свой лот."
    if buyer.gold < listing.price:
        return "Недостаточно золота."
    buyer.gold -= listing.price
    from game.core.player import add_to_inventory
    add_to_inventory(buyer, listing.item_id, listing.quantity)
    return None


def cancel_listing(player: Any, listing: Any) -> Optional[str]:
    if player.telegram_id != listing.seller_id:
        return "Это не ваш лот."
    from game.core.player import add_to_inventory
    add_to_inventory(player, listing.item_id, listing.quantity)
    return None


def format_listing(listing: Any) -> str:
    item = get_item(listing.item_id)
    item_name = item["name"] if item else listing.item_id
    lines = [
        f"🏷️ <b>{item_name}</b> x{listing.quantity}",
        f"💰 Цена: {listing.price} золота",
        f"👤 Продавец: {listing.seller_id}",
    ]
    return "\n".join(lines)


def format_market(listings: list[Any]) -> str:
    if not listings:
        return "🏪 Аукцион пуст. Будьте первым продавцом!"
    lines = ["🏪 <b>Аукцион:</b>", ""]
    for i, listing in enumerate(listings, 1):
        item = get_item(listing.item_id)
        item_name = item["name"] if item else listing.item_id
        lines.append(f"  {i}. {item_name} x{listing.quantity} — {listing.price} 💰")
    return "\n".join(lines)
