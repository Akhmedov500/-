from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database.base import async_session_factory
from database.repositories import PlayerRepository, GuildRepository
from game.core.guild import format_guild, format_guild_members
import config

router = Router()


def guild_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏰 Моя гильдия"), KeyboardButton(text="🏰 Создать гильдию")],
            [KeyboardButton(text="👥 Участники"), KeyboardButton(text="📊 Топ гильдий")],
            [KeyboardButton(text="🚪 Покинуть гильдию"), KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )


@router.message(F.text == "🏰 Гильдия")
async def guild_menu(message: Message) -> None:
    await message.answer("🏰 <b>Гильдия:</b>", reply_markup=guild_menu_kb(), parse_mode="HTML")


@router.message(F.text == "🏰 Моя гильдия")
async def my_guild(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        if not player.guild_id:
            await message.answer("🏰 Вы не состоите в гильдии. Создайте свою или присоединитесь!")
            return
        guild_repo = GuildRepository(session)
        guild = await guild_repo.get(player.guild_id)
        if not guild:
            await message.answer("🏰 Гильдия не найдена.")
            return
        text = format_guild(guild)
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🏰 Создать гильдию")
async def create_guild_prompt(message: Message) -> None:
    await message.answer(
        "🏰 <b>Создание гильдии:</b>\n\n"
        f"💰 Стоимость: {config.GUILD_CREATE_COST} золота\n\n"
        "Отправьте команду:\n"
        "<code>/create_guild [название] [тег]</code>\n\n"
        "Например: <code>/create_guild Чёрные Паруса BP</code>",
        parse_mode="HTML",
    )


@router.message(F.text.startswith("/create_guild"))
async def create_guild(message: Message) -> None:
    if not message.from_user or not message.text:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Формат: /create_guild [название] [тег]")
        return
    # Split the remaining text - last word is tag
    remaining = parts[1:]
    if len(remaining) < 2:
        await message.answer("Укажите название и тег.")
        return
    tag = remaining[-1]
    name = " ".join(remaining[:-1])

    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        if player.guild_id:
            await message.answer("❌ Вы уже состоите в гильдии.")
            return
        if player.gold < config.GUILD_CREATE_COST:
            await message.answer(f"❌ Недостаточно золота. Нужно: {config.GUILD_CREATE_COST}")
            return
        guild_repo = GuildRepository(session)
        existing = await guild_repo.get_by_name(name)
        if existing:
            await message.answer("❌ Гильдия с таким названием уже существует.")
            return
        player.gold -= config.GUILD_CREATE_COST
        guild = await guild_repo.create(name=name, tag=tag, leader_id=player.telegram_id)
        player.guild_id = guild.id
        await repo.save(player)
        await message.answer(
            f"🏰 Гильдия <b>{name}</b> [{tag}] создана!\n"
            f"💰 Списано: {config.GUILD_CREATE_COST} золота",
            parse_mode="HTML",
        )


@router.message(F.text == "👥 Участники")
async def guild_members(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player or not player.guild_id:
            await message.answer("🏰 Вы не состоите в гильдии.")
            return
        guild_repo = GuildRepository(session)
        guild = await guild_repo.get(player.guild_id)
        if not guild:
            return
        text = format_guild_members(guild)
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📊 Топ гильдий")
async def top_guilds(message: Message) -> None:
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


@router.message(F.text == "🚪 Покинуть гильдию")
async def leave_guild(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player or not player.guild_id:
            await message.answer("🏰 Вы не состоите в гильдии.")
            return
        guild_repo = GuildRepository(session)
        guild = await guild_repo.get(player.guild_id)
        if guild and guild.leader_id == player.telegram_id:
            await message.answer("❌ Лидер не может покинуть гильдию. Передайте лидерство.")
            return
        player.guild_id = None
        await repo.save(player)
        await message.answer("🚪 Вы покинули гильдию.", reply_markup=guild_menu_kb())
