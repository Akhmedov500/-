from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

import config


def calculate_energy_regen(last_update: datetime) -> int:
    now = datetime.utcnow()
    elapsed = (now - last_update).total_seconds()
    regen_interval = config.ENERGY_REGEN_MINUTES * 60
    points = int(elapsed // regen_interval)
    return points


def apply_energy_regen(player: Any) -> int:
    if not player.last_energy_update:
        player.last_energy_update = datetime.utcnow()
        return 0
    regen = calculate_energy_regen(player.last_energy_update)
    if regen > 0:
        old_energy = player.energy
        player.energy = min(config.MAX_ENERGY, player.energy + regen)
        gained = player.energy - old_energy
        player.last_energy_update = datetime.utcnow()
        return gained
    return 0


def get_time_until_energy(player: Any) -> Optional[timedelta]:
    if player.energy >= config.MAX_ENERGY:
        return None
    if not player.last_energy_update:
        return None
    regen_interval = timedelta(minutes=config.ENERGY_REGEN_MINUTES)
    elapsed = datetime.utcnow() - player.last_energy_update
    remaining = regen_interval - (elapsed % regen_interval)
    return remaining


def format_time_remaining(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    if total_seconds <= 0:
        return "скоро"
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    parts = []
    if hours > 0:
        parts.append(f"{hours}ч")
    if minutes > 0:
        parts.append(f"{minutes}м")
    if seconds > 0 and hours == 0:
        parts.append(f"{seconds}с")
    return " ".join(parts) if parts else "скоро"


def is_cooldown_active(last_action: Optional[datetime], cooldown_seconds: int) -> bool:
    if not last_action:
        return False
    elapsed = (datetime.utcnow() - last_action).total_seconds()
    return elapsed < cooldown_seconds


def get_cooldown_remaining(last_action: Optional[datetime], cooldown_seconds: int) -> Optional[timedelta]:
    if not last_action:
        return None
    elapsed = (datetime.utcnow() - last_action).total_seconds()
    remaining = cooldown_seconds - elapsed
    if remaining <= 0:
        return None
    return timedelta(seconds=remaining)
