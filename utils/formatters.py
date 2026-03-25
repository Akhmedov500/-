from __future__ import annotations



def gold_fmt(amount: int) -> str:
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}M 💰"
    if amount >= 1_000:
        return f"{amount / 1_000:.1f}K 💰"
    return f"{amount} 💰"


def xp_bar(current: int, target: int, length: int = 10) -> str:
    if target <= 0:
        return "▓" * length
    filled = int((current / target) * length)
    filled = min(filled, length)
    empty = length - filled
    return "▓" * filled + "░" * empty


def health_bar(current: int, maximum: int, length: int = 10) -> str:
    if maximum <= 0:
        return "▓" * length
    filled = int((current / maximum) * length)
    filled = min(filled, length)
    empty = length - filled
    return "❤️" + "█" * filled + "░" * empty


def energy_bar(current: int, maximum: int) -> str:
    return f"⚡ {current}/{maximum}"


def stat_line(name: str, value: int, emoji: str = "📊") -> str:
    return f"{emoji} {name}: {value}"


def progress_bar(current: int, total: int, length: int = 10, label: str = "") -> str:
    if total <= 0:
        pct = 100
    else:
        pct = int((current / total) * 100)
    filled = int((current / max(1, total)) * length)
    filled = min(filled, length)
    empty = length - filled
    bar = "▓" * filled + "░" * empty
    text = f"{bar} {pct}%"
    if label:
        text = f"{label}: {text}"
    return text


def number_emoji(num: int) -> str:
    emojis = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 0: "0️⃣"}
    return emojis.get(num, str(num))


def format_list(items: list[str], numbered: bool = False) -> str:
    if not items:
        return "Пусто"
    lines = []
    for i, item in enumerate(items, 1):
        if numbered:
            lines.append(f"  {i}. {item}")
        else:
            lines.append(f"  • {item}")
    return "\n".join(lines)


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["  ".join(headers)]
    lines.append("─" * len(lines[0]))
    for row in rows:
        lines.append("  ".join(str(c) for c in row))
    return "\n".join(lines)
