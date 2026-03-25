from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.base import async_session_factory
from database.repositories import PlayerRepository, ShipRepository
from keyboards.navigation import navigation_kb, island_kb
from keyboards.inline_menus import island_travel_kb, trade_route_kb, smuggling_kb
from game.world.map import (
    get_island, get_connected_islands, format_island_info,
    format_navigation, get_travel_cost, can_travel,
)
from game.world.islands import get_island_monsters, gather_resources, get_random_encounter
from game.world.weather import get_random_weather, format_weather
from game.trading.routes import get_available_routes, format_routes, run_trade_route
from game.trading.smuggling import get_available_smuggling, do_smuggling, format_smuggling_menu
from game.combat.battle import run_combat, format_combat_result

router = Router()


@router.message(F.text == "🗺️ Карта")
async def show_map(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            await message.answer("Используйте /start для начала игры!")
            return
        await message.answer(
            format_navigation(player.current_island),
            reply_markup=navigation_kb(),
            parse_mode="HTML",
        )


@router.message(F.text == "🏝️ Текущий остров")
async def show_island(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        text = format_island_info(player.current_island)
        weather = get_random_weather()
        text += f"\n\n{format_weather(weather)}"
        await message.answer(text, reply_markup=island_kb(), parse_mode="HTML")


@router.message(F.text == "⛵ Плыть")
async def travel_menu(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        ship_repo = ShipRepository(session)
        ship = await ship_repo.get_active_ship(player.telegram_id)
        connected = get_connected_islands(player.current_island)
        if not connected:
            await message.answer("🏝️ Нет доступных островов для путешествия.")
            return
        islands_data = []
        for isl_id in connected:
            isl = get_island(isl_id)
            if isl:
                cost = get_travel_cost(player.current_island, isl_id, ship.sail_speed if ship else 10)
                islands_data.append({"id": isl_id, "name": isl["name"], "cost": cost, "emoji": isl.get("emoji", "🏝️")})
        await message.answer(
            "⛵ Куда плывём?",
            reply_markup=island_travel_kb(islands_data),
            parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("travel:"))
async def travel_to_island(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    island_id = callback.data.split(":")[1]  # type: ignore[union-attr]
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(callback.from_user.id)
        if not player:
            await callback.answer("Используйте /start!")
            return
        ship_repo = ShipRepository(session)
        ship = await ship_repo.get_active_ship(player.telegram_id)
        speed = ship.sail_speed if ship else 10
        error = can_travel(player, island_id, speed)
        if error:
            await callback.answer(error, show_alert=True)
            return
        cost = get_travel_cost(player.current_island, island_id, speed)
        player.energy -= cost
        player.current_island = island_id
        # Track visited islands
        visited = player.stats.get("visited_islands", []) if player.stats else []
        if island_id not in visited:
            visited.append(island_id)
            stats = player.stats if player.stats else {}
            stats["visited_islands"] = visited
            stats["islands_visited"] = len(visited)
            player.stats = stats
        await repo.save(player)
        island = get_island(island_id)
        name = island["name"] if island else island_id

        # Random encounter chance
        encounter = get_random_encounter(island_id)
        text = f"⛵ Вы прибыли на остров <b>{name}</b>!\n⚡ Энергия: {player.energy}"
        if encounter:
            text += f"\n\n⚠️ Вас встретил {encounter['name']}!"
            result = run_combat(player, encounter)
            text += "\n\n" + format_combat_result(result)
            if result.winner == "player":
                player.xp += result.xp_gained
                player.gold += result.gold_gained
                await repo.save(player)

        await callback.message.edit_text(text, parse_mode="HTML")  # type: ignore[union-attr]
        await callback.answer()


@router.message(F.text == "👀 Осмотреться")
async def look_around(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        island = get_island(player.current_island)
        if not island:
            await message.answer("🏝️ Неизвестный остров.")
            return
        monsters = get_island_monsters(player.current_island)
        text = format_island_info(player.current_island)
        if monsters:
            text += "\n\n👹 <b>Монстры:</b>"
            for m in monsters[:5]:
                text += f"\n  • {m['name']} (ур. {m['level']})"
        await message.answer(text, reply_markup=island_kb(), parse_mode="HTML")


@router.message(F.text == "⛏️ Собрать ресурсы")
async def gather(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        if player.energy < 5:
            await message.answer("⚡ Недостаточно энергии! (нужно 5)")
            return
        player.energy -= 5
        gathered = gather_resources(player.current_island, player.luck)
        if not gathered:
            await message.answer("😔 Вы ничего не нашли. Попробуйте на другом острове.")
            await repo.save(player)
            return
        from game.core.player import add_to_inventory
        text_parts = []
        for item_id, qty in gathered.items():
            add_to_inventory(player, item_id, qty)
            text_parts.append(f"  • {item_id} x{qty}")
        await repo.save(player)
        text = "⛏️ <b>Собранные ресурсы:</b>\n" + "\n".join(text_parts)
        text += f"\n\n⚡ Энергия: {player.energy}"
        await message.answer(text, reply_markup=island_kb(), parse_mode="HTML")


@router.message(F.text == "🚢 Торговые маршруты")
async def show_trade_routes(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        routes = get_available_routes(player.level)
        text = format_routes(player.level)
        kb = trade_route_kb(routes) if routes else None
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("trade_route:"))
async def do_trade_route(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    route_id = callback.data.split(":")[1]  # type: ignore[union-attr]
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(callback.from_user.id)
        if not player:
            await callback.answer("Используйте /start!")
            return
        success, profit, msg = run_trade_route(player, route_id)
        await repo.save(player)
        await callback.message.edit_text(msg, parse_mode="HTML")  # type: ignore[union-attr]
        await callback.answer()


@router.message(F.text == "🏴‍☠️ Контрабанда")
async def show_smuggling(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        text = format_smuggling_menu(player)
        goods = get_available_smuggling(player)
        kb = smuggling_kb(goods) if goods else None
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("smuggle:"))
async def do_smuggle(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    idx = int(callback.data.split(":")[1])  # type: ignore[union-attr]
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(callback.from_user.id)
        if not player:
            await callback.answer("Используйте /start!")
            return
        success, amount, msg = do_smuggling(player, idx)
        await repo.save(player)
        await callback.message.edit_text(msg, parse_mode="HTML")  # type: ignore[union-attr]
        await callback.answer()


@router.message(F.text == "🗺️ К навигации")
async def back_to_nav(message: Message) -> None:
    if not message.from_user:
        return
    await message.answer("🗺️ Навигация", reply_markup=navigation_kb())
