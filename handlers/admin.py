from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from database.base import async_session_factory
from database.repositories import PlayerRepository
import config

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return
    text = (
        "🔧 <b>Админ-панель:</b>\n\n"
        "/admin_stats — Статистика сервера\n"
        "/admin_give [user_id] [gold/xp] [amount] — Выдать ресурсы\n"
        "/admin_ban [user_id] — Забанить игрока\n"
        "/admin_unban [user_id] — Разбанить игрока\n"
        "/admin_event [event_id] — Запустить событие\n"
        "/admin_broadcast [message] — Рассылка"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("admin_stats"))
async def admin_stats(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return
    async with async_session_factory() as session:
        from sqlalchemy import select, func
        from database.base import Player, Guild
        player_count = (await session.execute(select(func.count(Player.telegram_id)))).scalar_one()
        guild_count = (await session.execute(select(func.count(Guild.id)))).scalar_one()
        total_gold = (await session.execute(select(func.sum(Player.gold)))).scalar_one() or 0
        avg_level = (await session.execute(select(func.avg(Player.level)))).scalar_one() or 0

        text = (
            f"📊 <b>Статистика сервера:</b>\n\n"
            f"👥 Игроков: {player_count}\n"
            f"🏰 Гильдий: {guild_count}\n"
            f"💰 Золота в обращении: {total_gold}\n"
            f"📊 Средний уровень: {avg_level:.1f}"
        )
        await message.answer(text, parse_mode="HTML")


@router.message(F.text.startswith("/admin_give"))
async def admin_give(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id) or not message.text:
        return
    parts = message.text.split()
    if len(parts) != 4:
        await message.answer("Формат: /admin_give [user_id] [gold/xp] [amount]")
        return
    try:
        target_id = int(parts[1])
        resource = parts[2]
        amount = int(parts[3])
    except ValueError:
        await message.answer("Неверный формат.")
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(target_id)
        if not player:
            await message.answer("Игрок не найден.")
            return
        if resource == "gold":
            player.gold += amount
        elif resource == "xp":
            await repo.add_xp(player, amount)
        else:
            await message.answer("Ресурс: gold или xp")
            return
        await repo.save(player)
        await message.answer(f"✅ Выдано {amount} {resource} игроку {player.display_name}")


@router.message(F.text.startswith("/admin_ban"))
async def admin_ban(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id) or not message.text:
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Формат: /admin_ban [user_id]")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("Неверный ID.")
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(target_id)
        if not player:
            await message.answer("Игрок не найден.")
            return
        player.is_banned = True
        await repo.save(player)
        await message.answer(f"🔨 Игрок {player.display_name} забанен.")


@router.message(F.text.startswith("/admin_unban"))
async def admin_unban(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id) or not message.text:
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Формат: /admin_unban [user_id]")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("Неверный ID.")
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(target_id)
        if not player:
            await message.answer("Игрок не найден.")
            return
        player.is_banned = False
        await repo.save(player)
        await message.answer(f"✅ Игрок {player.display_name} разбанен.")
