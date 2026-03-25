from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.base import async_session_factory
from database.repositories import PlayerRepository
from keyboards.crafting import crafting_menu_kb, inventory_kb
from keyboards.inline_menus import recipe_select_kb, potion_select_kb
from game.crafting.recipes import (
    RECIPES, get_recipe, craft_item, format_recipe_list,
)
from game.crafting.materials import format_materials_list
from game.crafting.alchemy import (
    POTIONS, brew_potion, format_potions_list,
)
from game.core.player import format_inventory

router = Router()


@router.message(F.text == "🔧 Крафт")
async def crafting_menu(message: Message) -> None:
    await message.answer("🔧 <b>Крафт:</b>", reply_markup=crafting_menu_kb(), parse_mode="HTML")


@router.message(F.text == "⚔️ Оружие")
async def weapon_recipes(message: Message) -> None:
    text = format_recipe_list("weapon")
    recipes = [{"id": rid, **r} for rid, r in RECIPES.items() if r["category"] == "weapon"]
    kb = recipe_select_kb(recipes) if recipes else None
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(F.text == "🛡 Броня")
async def armor_recipes(message: Message) -> None:
    text = format_recipe_list("armor")
    recipes = [{"id": rid, **r} for rid, r in RECIPES.items() if r["category"] == "armor"]
    kb = recipe_select_kb(recipes) if recipes else None
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(F.text == "🧪 Алхимия")
async def alchemy_menu(message: Message) -> None:
    text = format_potions_list()
    potions = [{"id": pid, **p} for pid, p in POTIONS.items()]
    kb = potion_select_kb(potions) if potions else None
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(F.text == "📦 Материалы")
async def materials_menu(message: Message) -> None:
    text = format_materials_list()
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🍖 Еда")
async def food_recipes(message: Message) -> None:
    text = format_recipe_list("food")
    recipes = [{"id": rid, **r} for rid, r in RECIPES.items() if r["category"] == "food"]
    kb = recipe_select_kb(recipes) if recipes else None
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("craft:"))
async def do_craft(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    recipe_id = callback.data.split(":")[1]  # type: ignore[union-attr]
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(callback.from_user.id)
        if not player:
            await callback.answer("Используйте /start!")
            return
        error = craft_item(player, recipe_id)
        if error:
            await callback.answer(error, show_alert=True)
            return
        recipe = get_recipe(recipe_id)
        name = recipe["name"] if recipe else recipe_id
        xp = recipe.get("xp", 0) if recipe else 0
        if xp:
            await repo.add_xp(player, xp)
        stats = player.stats if player.stats else {}
        stats["items_crafted"] = stats.get("items_crafted", 0) + 1
        player.stats = stats
        await repo.save(player)
        await callback.answer(f"✅ Создано: {name}!")
        await callback.message.edit_text(f"🔧 Создано: <b>{name}</b>!", parse_mode="HTML")  # type: ignore[union-attr]


@router.callback_query(F.data.startswith("brew:"))
async def do_brew(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    potion_id = callback.data.split(":")[1]  # type: ignore[union-attr]
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(callback.from_user.id)
        if not player:
            await callback.answer("Используйте /start!")
            return
        error = brew_potion(player, potion_id)
        if error:
            await callback.answer(error, show_alert=True)
            return
        from game.crafting.alchemy import get_potion
        potion = get_potion(potion_id)
        name = potion["name"] if potion else potion_id
        await repo.save(player)
        await callback.answer(f"✅ Сварено: {name}!")
        await callback.message.edit_text(f"🧪 Сварено: <b>{name}</b>!", parse_mode="HTML")  # type: ignore[union-attr]


@router.message(F.text == "🎒 Инвентарь")
async def show_inventory(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        text = format_inventory(player)
        await message.answer(text, reply_markup=inventory_kb(), parse_mode="HTML")


@router.message(F.text == "📦 Все предметы")
async def all_items(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        text = format_inventory(player)
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "⚔️ Экипировка")
async def equipment(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        equipped = player.equipped_items if player.equipped_items else {}
        weapon = equipped.get("weapon", "Нет")
        armor = equipped.get("armor", "Нет")
        text = (
            "⚔️ <b>Экипировка:</b>\n\n"
            f"  🗡️ Оружие: {weapon}\n"
            f"  🛡 Броня: {armor}"
        )
        await message.answer(text, parse_mode="HTML")
