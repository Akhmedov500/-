from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database.base import async_session_factory
from database.repositories import PlayerRepository, GuildRepository

router = Router()


def leaderboard_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏆 По уровню"), KeyboardButton(text="⚔️ По PVP")],
            [KeyboardButton(text="💰 По золоту"), KeyboardButton(text="🏰 Гильдии")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )


@router.message(F.text == "🏆 Рейтинг")
async def leaderboard_menu(message: Message) -> None:
    await message.answer("🏆 <b>Таблицы лидеров:</b>", reply_markup=leaderboard_kb(), parse_mode="HTML")


@router.message(F.text == "🏆 По уровню")
async def level_leaderboard(message: Message) -> None:
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        players = await repo.get_top_players(order_by="level", limit=20)
        if not players:
            await message.answer("🏆 Пока нет игроков.")
            return
        lines = ["🏆 <b>Топ по уровню:</b>", ""]
        medals = ["🥇", "🥈", "🥉"]
        for i, p in enumerate(players):
            medal = medals[i] if i < 3 else f"{i + 1}."
            lines.append(f"  {medal} {p.display_name} — ур. {p.level} (⚔️{p.attack} 🛡{p.defense})")
        await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(F.text == "⚔️ По PVP")
async def pvp_leaderboard(message: Message) -> None:
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        players = await repo.get_pvp_leaderboard(limit=20)
        if not players:
            await message.answer("🏆 Пока нет PVP данных.")
            return
        lines = ["⚔️ <b>PVP Рейтинг:</b>", ""]
        medals = ["🥇", "🥈", "🥉"]
        for i, p in enumerate(players):
            medal = medals[i] if i < 3 else f"{i + 1}."
            lines.append(f"  {medal} {p.display_name} — {p.pvp_rating} ⭐ ({p.pvp_wins}W/{p.pvp_losses}L)")
        await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(F.text == "💰 По золоту")
async def gold_leaderboard(message: Message) -> None:
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        players = await repo.get_top_players(order_by="gold", limit=20)
        if not players:
            await message.answer("🏆 Пока нет игроков.")
            return
        lines = ["💰 <b>Топ по золоту:</b>", ""]
        medals = ["🥇", "🥈", "🥉"]
        for i, p in enumerate(players):
            medal = medals[i] if i < 3 else f"{i + 1}."
            lines.append(f"  {medal} {p.display_name} — {p.gold} 💰 (ур. {p.level})")
        await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(F.text == "🏰 Гильдии")
async def guild_leaderboard(message: Message) -> None:
    async with async_session_factory() as session:
        guild_repo = GuildRepository(session)
        guilds = await guild_repo.get_top_guilds(limit=10)
        if not guilds:
            await message.answer("🏰 Пока нет гильдий.")
            return
        lines = ["🏰 <b>Топ гильдий:</b>", ""]
        medals = ["🥇", "🥈", "🥉"]
        for i, g in enumerate(guilds):
            medal = medals[i] if i < 3 else f"{i + 1}."
            members_count = len(g.members) if g.members else 0
            lines.append(f"  {medal} {g.name} [{g.tag}] — ур. {g.level} ({members_count} чел.)")
        await message.answer("\n".join(lines), parse_mode="HTML")
