from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.base import async_session_factory
from database.repositories import PlayerRepository, ShipRepository, QuestRepository
from keyboards.combat import combat_menu_kb, skill_tree_kb
from keyboards.inline_menus import boss_select_kb
from game.combat.battle import run_combat, format_combat_result
from game.combat.pve import run_boss_fight, get_available_bosses, format_boss_list
from game.combat.skills import format_skill_tree, format_player_skills, learn_skill
from game.combat.fleet import run_fleet_battle, create_enemy_fleet
from game.world.islands import get_random_encounter
import config

router = Router()


@router.message(F.text == "⚔️ Бой")
async def combat_menu(message: Message) -> None:
    await message.answer("⚔️ <b>Боевое меню:</b>", reply_markup=combat_menu_kb(), parse_mode="HTML")


@router.message(F.text == "🗡️ Охота на монстров")
async def hunt_monsters(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            await message.answer("Используйте /start для начала игры!")
            return
        if player.energy < 10:
            await message.answer("⚡ Недостаточно энергии! (нужно 10)")
            return
        encounter = get_random_encounter(player.current_island)
        if not encounter:
            await message.answer("🏝️ На этом острове нет монстров. Попробуйте другой остров!")
            return
        player.energy -= 10
        result = run_combat(player, encounter)
        text = format_combat_result(result)
        if result.winner == "player":
            player_obj, leveled_up = await repo.add_xp(player, result.xp_gained)
            player_obj.gold += result.gold_gained
            stats: dict = player_obj.stats if player_obj.stats else {}
            stats["monsters_killed"] = stats.get("monsters_killed", 0) + 1
            player_obj.stats = stats
            if result.loot:
                from game.core.player import add_to_inventory
                for item_id in result.loot:
                    add_to_inventory(player_obj, item_id, 1)
            if leveled_up:
                text += f"\n\n🎉 Уровень повышен! Теперь вы {player_obj.level} уровня!"
        elif result.winner == "enemy":
            player.health = max(1, player.health - result.player_damage_taken)
            player.gold = max(0, player.gold + result.gold_gained)
        await repo.save(player)
        quest_repo = QuestRepository(session)
        await quest_repo.log_battle(
            attacker_id=player.telegram_id,
            defender_id=None,
            battle_type="pve",
            result=result.winner,
            rounds=result.rounds,
            loot={"items": result.loot},
            xp_gained=result.xp_gained,
            gold_gained=result.gold_gained,
        )
        await message.answer(text, reply_markup=combat_menu_kb(), parse_mode="HTML")


@router.message(F.text == "🐲 Бой с боссом")
async def boss_menu(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        text = format_boss_list(player.current_island)
        bosses = get_available_bosses(player.current_island)
        kb = boss_select_kb(bosses) if bosses else None
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("boss:"))
async def fight_boss(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    boss_id = callback.data.split(":")[1]  # type: ignore[union-attr]
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(callback.from_user.id)
        if not player:
            await callback.answer("Используйте /start!")
            return
        if player.energy < 20:
            await callback.answer("⚡ Недостаточно энергии! (нужно 20)", show_alert=True)
            return
        player.energy -= 20
        result = run_boss_fight(player, boss_id)
        text = format_combat_result(result)
        if result.winner == "player":
            player_obj, leveled_up = await repo.add_xp(player, result.xp_gained)
            player_obj.gold += result.gold_gained
            stats = player_obj.stats if player_obj.stats else {}
            stats["bosses_killed"] = stats.get("bosses_killed", 0) + 1
            player_obj.stats = stats
            if leveled_up:
                text += f"\n\n🎉 Уровень повышен! Теперь вы {player_obj.level} уровня!"
        await repo.save(player)
        await callback.message.edit_text(text, parse_mode="HTML")  # type: ignore[union-attr]
        await callback.answer()


@router.message(F.text == "⚔️ PVP Арена")
async def pvp_menu(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        if player.level < config.PVP_MIN_LEVEL:
            await message.answer(f"⚔️ PVP доступно с {config.PVP_MIN_LEVEL} уровня. Ваш уровень: {player.level}")
            return
        await message.answer(
            f"⚔️ <b>PVP Арена</b>\n"
            f"📊 Ваш рейтинг: {player.pvp_rating} ⭐\n"
            f"🏆 Побед: {player.pvp_wins}  |  💀 Поражений: {player.pvp_losses}\n\n"
            f"Ожидание противника... (автоматический подбор)",
            parse_mode="HTML",
        )


@router.message(F.text == "⚓ Морской бой")
async def fleet_battle(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        ship_repo = ShipRepository(session)
        ships = await ship_repo.get_player_ships(player.telegram_id)
        if not ships:
            await message.answer("⚓ У вас нет кораблей!")
            return
        if player.energy < 15:
            await message.answer("⚡ Недостаточно энергии! (нужно 15)")
            return
        player.energy -= 15
        enemy_fleet = create_enemy_fleet(player.level, count=min(3, len(ships)))
        active_ships = [s for s in ships if s.hull_hp > 0]
        if not active_ships:
            await message.answer("⚓ Все ваши корабли повреждены! Отремонтируйте их.")
            return
        result = run_fleet_battle(active_ships, enemy_fleet)
        text = "\n".join(result.log)
        if result.winner == "player":
            player_obj, leveled_up = await repo.add_xp(player, result.xp_gained)
            player_obj.gold += result.gold_gained
            if leveled_up:
                text += f"\n\n🎉 Уровень повышен! Теперь вы {player_obj.level} уровня!"
        for damaged in result.ships_damaged:
            ship = damaged["ship"]
            ship.hull_hp = max(0, damaged["remaining_hp"])
            await ship_repo.save(ship)
        await repo.save(player)
        await message.answer(text, reply_markup=combat_menu_kb(), parse_mode="HTML")


@router.message(F.text == "📋 Навыки")
async def skills_menu(message: Message) -> None:
    await message.answer("📋 <b>Деревья навыков:</b>", reply_markup=skill_tree_kb(), parse_mode="HTML")


@router.message(F.text == "⚔️ Боевые")
async def combat_skill_tree(message: Message) -> None:
    await message.answer(format_skill_tree("combat"), parse_mode="HTML")


@router.message(F.text == "🛡 Защитные")
async def defense_skill_tree(message: Message) -> None:
    await message.answer(format_skill_tree("defense"), parse_mode="HTML")


@router.message(F.text == "⛵ Мореходные")
async def sailing_skill_tree(message: Message) -> None:
    await message.answer(format_skill_tree("sailing"), parse_mode="HTML")


@router.message(F.text == "💰 Торговые")
async def trade_skill_tree(message: Message) -> None:
    await message.answer(format_skill_tree("trade"), parse_mode="HTML")


@router.message(F.text == "🏕️ Выживание")
async def survival_skill_tree(message: Message) -> None:
    await message.answer(format_skill_tree("survival"), parse_mode="HTML")


@router.message(F.text == "📋 Мои навыки")
async def my_skills(message: Message) -> None:
    if not message.from_user:
        return
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(message.from_user.id)
        if not player:
            return
        await message.answer(format_player_skills(player), parse_mode="HTML")


@router.callback_query(F.data.startswith("learn_skill:"))
async def learn_skill_cb(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    skill_id = callback.data.split(":")[1]  # type: ignore[union-attr]
    async with async_session_factory() as session:
        repo = PlayerRepository(session)
        player = await repo.get(callback.from_user.id)
        if not player:
            await callback.answer("Используйте /start!")
            return
        error = learn_skill(player, skill_id)
        if error:
            await callback.answer(error, show_alert=True)
            return
        await repo.save(player)
        await callback.answer("✅ Навык изучен!")
        await callback.message.edit_text(format_player_skills(player), parse_mode="HTML")  # type: ignore[union-attr]


@router.message(F.text == "🔙 К бою")
async def back_to_combat(message: Message) -> None:
    await message.answer("⚔️ Боевое меню", reply_markup=combat_menu_kb())
