from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from database.base import async_session_factory
from database.repositories import PlayerRepository, MarketRepository
from keyboards.market import market_menu_kb
from game.trading.market import format_market
from game.core.economy import format_trade_goods
from game.trading.economy_manager import format_economy_stats, EconomySnapshot

router = Router()


@router.message(F.text == "🏪 Аукцион")
async def market_menu(message: Message) -> None:
    await message.answer("🏪 <b>Аукцион:</b>", reply_markup=market_menu_kb(), parse_mode="HTML")


@router.message(F.text == "🔍 Просмотр лотов")
async def browse_listings(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        market_repo = MarketRepository(session)
        listings = await market_repo.get_active_listings(limit=20)
        text = format_market(listings)
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📤 Выставить на продажу")
async def create_listing_prompt(message: Message) -> None:
    await message.answer(
        "📤 <b>Выставить предмет на аукцион:</b>\n\n"
        "Отправьте сообщение в формате:\n"
        "<code>/sell [предмет] [количество] [цена]</code>\n\n"
        "Например: <code>/sell iron_ingot 5 100</code>",
        parse_mode="HTML",
    )


@router.message(F.text == "📋 Мои лоты")
async def my_listings(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        market_repo = MarketRepository(session)
        listings = await market_repo.get_player_listings(message.from_user.id)
        text = format_market(listings)
        if not listings:
            text = "📋 У вас нет активных лотов."
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "💰 Торговые товары")
async def trade_goods(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        text = format_trade_goods(player.current_island)
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📊 Экономика")
async def economy_stats(message: Message) -> None:
    snapshot = EconomySnapshot()
    text = format_economy_stats(snapshot)
    await message.answer(text, parse_mode="HTML")


@router.message(F.text.startswith("/sell"))
async def sell_item(message: Message) -> None:
    if not message.from_user or not message.text:
        return
    parts = message.text.split()
    if len(parts) != 4:
        await message.answer("Формат: /sell [предмет] [количество] [цена]")
        return
    item_id = parts[1]
    try:
        quantity = int(parts[2])
        price = int(parts[3])
    except ValueError:
        await message.answer("Количество и цена должны быть числами.")
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        from game.trading.market import create_listing
        from game.core.player import get_item
        error = create_listing(player, item_id, quantity, price)
        if error:
            await message.answer(f"❌ {error}")
            return
        item = get_item(item_id)
        item_name = item["name"] if item else item_id
        market_repo = MarketRepository(session)
        await market_repo.create_listing(
            seller_id=player.telegram_id,
            item_id=item_id,
            item_name=item_name,
            quantity=quantity,
            price=price,
        )
        await repo.save(player)
        await message.answer(
            f"✅ Лот создан!\n"
            f"📦 {item_name} x{quantity}\n"
            f"💰 Цена: {price}",
            parse_mode="HTML",
        )


@router.message(F.text == "🚢 Маршруты")
async def routes_menu(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        from game.trading.routes import format_routes
        text = format_routes(player.level)
        await message.answer(text, parse_mode="HTML")
