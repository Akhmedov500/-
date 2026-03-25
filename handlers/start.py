from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from database.base import async_session_factory
from database.repositories import PlayerRepository, ShipRepository
from keyboards.main import main_menu_kb

router = Router()

WELCOME_TEXT = """
🏴‍☠️ <b>SEA OF SHADOWS</b> 🏴‍☠️
━━━━━━━━━━━━━━━━━
Добро пожаловать в мир пиратских приключений!

Вас ждут:
🗺️ 500+ островов для исследования
⚔️ Эпические морские сражения
🏰 Гильдии и альянсы
💰 Торговля и аукционы
📜 Квесты и сюжетная кампания
🏆 PVP-арены и рейтинги

Готовы покорить моря? ⛵
"""

TUTORIAL_TEXT = """
📖 <b>Краткое руководство:</b>

1. 🗺️ <b>Карта</b> — путешествуйте между островами
2. ⚔️ <b>Бой</b> — сражайтесь с монстрами и боссами
3. 🎒 <b>Инвентарь</b> — управляйте экипировкой
4. 🔧 <b>Крафт</b> — создавайте предметы и зелья
5. 🏪 <b>Аукцион</b> — торгуйте с другими игроками
6. 📜 <b>Квесты</b> — выполняйте задания
7. 🏰 <b>Гильдия</b> — объединяйтесь с другими
8. 👤 <b>Профиль</b> — ваша статистика

💡 Используйте кнопки меню для навигации!
"""


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if player:
            await message.answer(
                f"🏴‍☠️ С возвращением, <b>{player.display_name}</b>!\n"
                f"📊 Уровень: {player.level}  |  💰 {player.gold}\n"
                f"🏝️ Вы на острове: {player.current_island}",
                reply_markup=main_menu_kb(),
                parse_mode="HTML",
            )
            return

        display_name = message.from_user.first_name or "Pirate"
        player = await repo.create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            display_name=display_name,
        )
        ship_repo = ShipRepository(session)
        await ship_repo.create(owner_id=player.telegram_id, ship_type="sloop", name="Первый корабль")

        await message.answer(WELCOME_TEXT, parse_mode="HTML")
        await message.answer(
            f"⛵ Ваш персонаж <b>{display_name}</b> создан!\n"
            f"💰 Стартовое золото: {player.gold}\n"
            f"🏝️ Вы находитесь в: Порт-Ройал\n"
            f"⛵ Ваш первый корабль: Шлюп",
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(TUTORIAL_TEXT, parse_mode="HTML")


@router.message(F.text == "🔙 Главное меню")
async def back_to_menu(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            await message.answer("Используйте /start для начала игры!")
            return
        await repo.update_energy(player)
        await message.answer(
            f"🏴‍☠️ <b>{player.display_name}</b>\n"
            f"📊 Ур. {player.level}  |  ❤️ {player.health}/{player.max_health}"
            f"  |  ⚡ {player.energy}/{player.max_energy}\n"
            f"💰 {player.gold}  |  🏝️ {player.current_island}",
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )
