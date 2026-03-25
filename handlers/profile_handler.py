from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from database.base import async_session_factory
from database.repositories import PlayerRepository
from utils.formatters import xp_bar, gold_fmt

router = Router()


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            await message.answer("Используйте /start для начала игры!")
            return
        await repo.update_energy(player)

        xp_needed = repo._xp_for_level(player.level + 1)
        bar = xp_bar(player.xp, xp_needed)

        text = (
            f"👤 <b>Профиль: {player.display_name}</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📊 Уровень: {player.level}\n"
            f"📈 XP: {player.xp}/{xp_needed} [{bar}]\n"
            f"❤️ HP: {player.health}/{player.max_health}\n"
            f"⚡ Энергия: {player.energy}/{player.max_energy}\n"
            f"💰 Золото: {gold_fmt(player.gold)}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"⚔️ Атака: {player.attack}\n"
            f"🛡 Защита: {player.defense}\n"
            f"💨 Скорость: {player.speed}\n"
            f"🍀 Удача: {player.luck}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🏝️ Остров: {player.current_island}\n"
            f"🏴 Фракция: {player.faction_id or 'Нет'}\n"
            f"🏰 Гильдия: {'Есть' if player.guild_id else 'Нет'}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"⚔️ PVP: {player.pvp_rating} ⭐ ({player.pvp_wins}W/{player.pvp_losses}L)\n"
            f"💎 Очков навыков: {player.skill_points}"
        )
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        stats: dict = player.stats if player.stats else {}
        text = (
            f"📊 <b>Статистика {player.display_name}:</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👹 Монстров убито: {stats.get('monsters_killed', 0)}\n"
            f"🐲 Боссов побеждено: {stats.get('bosses_killed', 0)}\n"
            f"📜 Квестов выполнено: {stats.get('quests_completed', 0)}\n"
            f"🔧 Предметов создано: {stats.get('items_crafted', 0)}\n"
            f"🏝️ Островов посещено: {stats.get('islands_visited', 0)}\n"
            f"💰 Золота заработано: {stats.get('gold_earned', 0)}\n"
            f"⚔️ PVP боёв: {stats.get('pvp_battles', 0)}\n"
            f"🤝 Сделок: {stats.get('trades_completed', 0)}\n"
            f"🏴‍☠️ Контрабанды: {stats.get('smuggling_runs', 0)}"
        )
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "⚙️ Настройки")
async def settings(message: Message) -> None:
    from keyboards.main import settings_kb
    await message.answer("⚙️ <b>Настройки:</b>", reply_markup=settings_kb(), parse_mode="HTML")
