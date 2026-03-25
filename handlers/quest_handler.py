from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

from database.base import async_session_factory
from database.repositories import PlayerRepository
from keyboards.inline_menus import quest_choice_kb
from game.quests.main_story import (
    get_current_chapter, make_story_choice, format_chapter,
)
from game.quests.faction_quests import (
    get_available_faction_quests, format_faction_quest,
)
from game.quests.daily_quests import get_daily_quests, format_daily_quests
from game.quests.achievements import (
    check_all_achievements, format_achievements, format_new_achievement,
)

router = Router()


def quest_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Сюжет"), KeyboardButton(text="📜 Фракционные")],
            [KeyboardButton(text="📋 Ежедневные"), KeyboardButton(text="🏆 Достижения")],
            [KeyboardButton(text="🌍 События"), KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
    )


@router.message(F.text == "📜 Квесты")
async def quests_menu(message: Message) -> None:
    await message.answer("📜 <b>Квесты:</b>", reply_markup=quest_menu_kb(), parse_mode="HTML")


@router.message(F.text == "📖 Сюжет")
async def show_story(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        chapter = get_current_chapter(player)
        if not chapter:
            await message.answer("📖 Сюжетная кампания завершена! Поздравляем!")
            return
        text = format_chapter(chapter)
        kb = quest_choice_kb(chapter["choices"]) if "choices" in chapter else None
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("story_choice:"))
async def story_choice(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    choice_idx = int(callback.data.split(":")[1])  # type: ignore[union-attr]
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(callback.from_user.id)
        if not player:
            await callback.answer("Используйте /start!")
            return
        choice = make_story_choice(player, choice_idx)
        if not choice:
            await callback.answer("Неверный выбор!")
            return
        await repo.save(player)
        next_chapter = get_current_chapter(player)
        if next_chapter:
            text = f"✅ Вы выбрали: {choice.get('text', '')}\n\n"
            text += format_chapter(next_chapter)
            kb = quest_choice_kb(next_chapter["choices"]) if "choices" in next_chapter else None
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")  # type: ignore[union-attr]
        else:
            await callback.message.edit_text("📖 Глава завершена!", parse_mode="HTML")  # type: ignore[union-attr]
        await callback.answer()


@router.message(F.text == "📜 Фракционные")
async def faction_quests(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        if not player.faction_id:
            await message.answer("🏴 Вы не состоите во фракции. Присоединитесь к фракции!")
            return
        quests = get_available_faction_quests(player, player.faction_id)
        if not quests:
            await message.answer("📜 Нет доступных фракционных квестов.")
            return
        text = f"📜 <b>Квесты фракции {player.faction_id}:</b>\n\n"
        for q in quests[:5]:
            text += format_faction_quest(q) + "\n\n"
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📋 Ежедневные")
async def daily_quests_menu(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        quests = get_daily_quests(player.level)
        text = format_daily_quests(quests)
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🏆 Достижения")
async def achievements_menu(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        new_achievements = check_all_achievements(player)
        if new_achievements:
            await repo.save(player)
            for ach in new_achievements:
                await message.answer(format_new_achievement(ach), parse_mode="HTML")
        text = format_achievements(player)
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🌍 События")
async def world_events(message: Message) -> None:
    from game.quests.events import format_event_list
    text = format_event_list()
    await message.answer(text, parse_mode="HTML")
