from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.core.economy import (
    get_trade_price, calculate_auction_fee, get_smuggling_goods, attempt_smuggling,
)
from game.core.player import add_to_inventory, remove_from_inventory, has_item
from game.trading.economy_manager import calculate_inflation, adjust_prices, calculate_tax


class MockPlayer:
    def __init__(self) -> None:
        self.inventory: list = []
        self.gold = 500
        self.luck = 5
        self.skills: dict = {}


def test_trade_price_positive() -> None:
    price = get_trade_price("rum", "tortuga", is_buy=True)
    assert price >= 1, "Trade price should be positive"


def test_trade_price_origin_cheaper() -> None:
    origin_prices = [get_trade_price("rum", "tortuga", is_buy=True) for _ in range(50)]
    non_origin_prices = [get_trade_price("rum", "havana", is_buy=True) for _ in range(50)]
    avg_origin = sum(origin_prices) / len(origin_prices)
    avg_non = sum(non_origin_prices) / len(non_origin_prices)
    assert avg_origin < avg_non, "Origin prices should be cheaper on average"


def test_auction_fee() -> None:
    fee = calculate_auction_fee(100)
    assert fee == 5, f"5% of 100 should be 5, got {fee}"
    fee_zero = calculate_auction_fee(0)
    assert fee_zero == 0


def test_smuggling_goods() -> None:
    goods = get_smuggling_goods()
    assert len(goods) == 5
    for g in goods:
        assert "id" in g
        assert "name" in g
        assert "risk" in g
        assert "reward" in g


def test_attempt_smuggling() -> None:
    player = MockPlayer()
    goods = get_smuggling_goods()
    results = [attempt_smuggling(player, goods[0]) for _ in range(100)]
    successes = sum(1 for s, _, _ in results if s)
    assert successes > 0, "Should have some successful smuggling"
    assert successes < 100, "Should have some failed smuggling"


def test_inventory_operations() -> None:
    player = MockPlayer()
    assert not has_item(player, "wood")
    add_to_inventory(player, "wood", 5)
    assert has_item(player, "wood", 5)
    assert not has_item(player, "wood", 6)
    remove_from_inventory(player, "wood", 3)
    assert has_item(player, "wood", 2)
    assert not has_item(player, "wood", 3)
    remove_from_inventory(player, "wood", 2)
    assert not has_item(player, "wood")


def test_calculate_inflation() -> None:
    inflation = calculate_inflation(50000, 10)
    assert inflation >= 0.5
    assert inflation <= 2.0
    inflation_zero = calculate_inflation(0, 0)
    assert inflation_zero == 1.0


def test_adjust_prices() -> None:
    price = adjust_prices(100, 1.5)
    assert price == 150
    price_min = adjust_prices(1, 0.1)
    assert price_min >= 1


def test_calculate_tax() -> None:
    tax = calculate_tax(100, "trade")
    assert tax == 3  # 3% trade tax
    tax_auction = calculate_tax(100, "auction")
    assert tax_auction == 5  # 5% auction fee


if __name__ == "__main__":
    test_trade_price_positive()
    test_trade_price_origin_cheaper()
    test_auction_fee()
    test_smuggling_goods()
    test_attempt_smuggling()
    test_inventory_operations()
    test_calculate_inflation()
    test_adjust_prices()
    test_calculate_tax()
    print("All economy tests passed!")
