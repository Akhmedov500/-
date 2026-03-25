from __future__ import annotations

import random
import string
from datetime import datetime, timedelta
from typing import Any, Optional


def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, value))


def random_id(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def chance(probability: float) -> bool:
    return random.random() < probability


def weighted_choice(options: list[Any], weights: list[float]) -> Any:
    return random.choices(options, weights=weights, k=1)[0]


def time_until(target: datetime) -> timedelta:
    now = datetime.utcnow()
    diff = target - now
    if diff.total_seconds() < 0:
        return timedelta(0)
    return diff


def parse_duration(text: str) -> Optional[timedelta]:
    text = text.strip().lower()
    try:
        if text.endswith("m"):
            return timedelta(minutes=int(text[:-1]))
        elif text.endswith("h"):
            return timedelta(hours=int(text[:-1]))
        elif text.endswith("d"):
            return timedelta(days=int(text[:-1]))
        elif text.endswith("s"):
            return timedelta(seconds=int(text[:-1]))
    except ValueError:
        pass
    return None


def truncate(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def paginate(items: list[Any], page: int = 1, per_page: int = 10) -> tuple[list[Any], int]:
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = clamp(page, 1, total_pages)
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total_pages
