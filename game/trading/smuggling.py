from __future__ import annotations

from typing import Any

from game.core.economy import get_smuggling_goods, attempt_smuggling
from game.core.faction import change_reputation


def get_available_smuggling(player: Any) -> list[dict[str, Any]]:
    goods = get_smuggling_goods()
    return [g for g in goods if player.level >= 5]


def do_smuggling(player: Any, good_index: int) -> tuple[bool, int, str]:
    goods = get_available_smuggling(player)
    if good_index < 0 or good_index >= len(goods):
        return False, 0, "Неверный выбор контрабанды."
    good = goods[good_index]
    if player.energy < 15:
        return False, 0, "Недостаточно энергии (нужно 15)."

    player.energy -= 15
    success, amount, message = attempt_smuggling(player, good)

    if success:
        player.gold += amount
        change_reputation(player, "shadow_syndicate", 10)
        change_reputation(player, "royal_navy", -5)
        stats: dict = player.stats if player.stats else {}
        stats["smuggling_runs"] = stats.get("smuggling_runs", 0) + 1
        stats["smuggling_profit"] = stats.get("smuggling_profit", 0) + amount
        player.stats = stats
    else:
        player.gold = max(0, player.gold + amount)
        change_reputation(player, "royal_navy", 5)
        change_reputation(player, "shadow_syndicate", -5)

    return success, amount, message


def format_smuggling_menu(player: Any) -> str:
    goods = get_available_smuggling(player)
    if not goods:
        return "🏴‍☠️ Контрабанда недоступна (мин. уровень 5)."
    lines = [
        "🏴‍☠️ <b>Контрабанда</b>",
        "⚠️ Высокий риск — высокая награда!",
        f"⚡ Стоимость: 15 энергии | У вас: {player.energy}",
        "",
    ]
    for i, good in enumerate(goods, 1):
        risk_pct = int(good["risk"] * 100)
        lines.append(f"  {i}. {good['emoji']} {good['name']}")
        lines.append(f"     💰 Награда: {good['reward']}  |  ⚠️ Риск: {risk_pct}%")
        lines.append("")
    return "\n".join(lines)
