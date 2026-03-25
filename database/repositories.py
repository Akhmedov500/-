from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Sequence

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import (
    Player,
    Ship,
    Guild,
    Alliance,
    MarketListing,
    Mail,
    WorldEvent,
    BattleLog,
    ChatMessage,
)
import config


class PlayerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, telegram_id: int) -> Optional[Player]:
        result = await self.session.execute(
            select(Player).where(Player.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, username: Optional[str] = None, display_name: str = "Pirate") -> Player:
        player = Player(
            telegram_id=telegram_id,
            username=username,
            display_name=display_name,
            gold=config.STARTING_GOLD,
            energy=config.ENERGY_MAX,
            max_energy=config.ENERGY_MAX,
            faction_reputation={},
            inventory=[],
            equipped_items={},
            skills={},
            quest_progress={},
            daily_quests=[],
            achievements=[],
            stats={"monsters_killed": 0, "quests_completed": 0, "items_crafted": 0, "islands_visited": 1, "gold_earned": 0, "pvp_battles": 0, "trades_completed": 0},
            story_choices={},
        )
        self.session.add(player)
        await self.session.commit()
        await self.session.refresh(player)
        return player

    async def save(self, player: Player) -> None:
        player.last_active = datetime.utcnow()
        await self.session.commit()

    async def update_energy(self, player: Player) -> Player:
        now = datetime.utcnow()
        if player.last_energy_regen is None:
            player.last_energy_regen = now
            await self.session.commit()
            return player
        elapsed = (now - player.last_energy_regen).total_seconds() / 60
        regen_ticks = int(elapsed / config.ENERGY_REGEN_MINUTES)
        if regen_ticks > 0 and player.energy < player.max_energy:
            player.energy = min(player.max_energy, player.energy + regen_ticks)
            player.last_energy_regen = now
            await self.session.commit()
        return player

    async def add_xp(self, player: Player, amount: int) -> tuple[Player, bool]:
        player.xp += amount
        leveled_up = False
        while player.xp >= self._xp_for_level(player.level + 1) and player.level < config.MAX_LEVEL:
            player.xp -= self._xp_for_level(player.level + 1)
            player.level += 1
            player.skill_points += 1
            player.max_health += 10
            player.health = player.max_health
            player.attack += 2
            player.defense += 1
            leveled_up = True
        await self.session.commit()
        return player, leveled_up

    @staticmethod
    def _xp_for_level(level: int) -> int:
        return int(config.XP_PER_LEVEL_BASE * (config.XP_PER_LEVEL_MULTIPLIER ** (level - 1)))

    async def get_top_players(self, order_by: str = "level", limit: int = 10) -> Sequence[Player]:
        col = getattr(Player, order_by, Player.level)
        result = await self.session.execute(
            select(Player).order_by(col.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_pvp_leaderboard(self, limit: int = 10) -> Sequence[Player]:
        result = await self.session.execute(
            select(Player).order_by(Player.pvp_rating.desc()).limit(limit)
        )
        return result.scalars().all()


class ShipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_player_ships(self, owner_id: int) -> Sequence[Ship]:
        result = await self.session.execute(
            select(Ship).where(Ship.owner_id == owner_id)
        )
        return result.scalars().all()

    async def get_active_ship(self, owner_id: int) -> Optional[Ship]:
        result = await self.session.execute(
            select(Ship).where(and_(Ship.owner_id == owner_id, Ship.is_active == True))
        )
        return result.scalar_one_or_none()

    async def create(self, owner_id: int, ship_type: str = "sloop", name: str = "Unnamed Ship") -> Ship:
        from game.core.ship import SHIP_TYPES
        stats = SHIP_TYPES.get(ship_type, SHIP_TYPES["sloop"])
        ship = Ship(
            owner_id=owner_id,
            ship_type=ship_type,
            name=name,
            hull_hp=stats["hull_hp"],
            max_hull_hp=stats["hull_hp"],
            sail_speed=stats["speed"],
            cannon_damage=stats["damage"],
            cargo_capacity=stats["cargo"],
            crew_count=stats["crew"],
            max_crew=stats["max_crew"],
            upgrades={},
            cargo=[],
        )
        self.session.add(ship)
        await self.session.commit()
        await self.session.refresh(ship)
        return ship

    async def save(self, ship: Ship) -> None:
        await self.session.commit()

    async def set_active(self, owner_id: int, ship_id: int) -> None:
        await self.session.execute(
            update(Ship).where(Ship.owner_id == owner_id).values(is_active=False)
        )
        await self.session.execute(
            update(Ship).where(and_(Ship.id == ship_id, Ship.owner_id == owner_id)).values(is_active=True)
        )
        await self.session.commit()


class GuildRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, guild_id: int) -> Optional[Guild]:
        result = await self.session.execute(
            select(Guild).where(Guild.id == guild_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Guild]:
        result = await self.session.execute(
            select(Guild).where(Guild.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, tag: str, leader_id: int) -> Guild:
        guild = Guild(
            name=name,
            tag=tag,
            leader_id=leader_id,
            diplomacy={},
            territory=[],
            perks={},
        )
        self.session.add(guild)
        await self.session.commit()
        await self.session.refresh(guild)
        return guild

    async def save(self, guild: Guild) -> None:
        await self.session.commit()

    async def get_top_guilds(self, limit: int = 10) -> Sequence[Guild]:
        result = await self.session.execute(
            select(Guild).order_by(Guild.level.desc()).limit(limit)
        )
        return result.scalars().all()

    async def delete(self, guild_id: int) -> None:
        await self.session.execute(delete(Guild).where(Guild.id == guild_id))
        await self.session.commit()


class MarketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_listing(
        self,
        seller_id: int,
        item_id: str,
        item_name: str,
        quantity: int,
        price: int,
        duration_hours: int = 24,
    ) -> MarketListing:
        listing = MarketListing(
            seller_id=seller_id,
            item_id=item_id,
            item_name=item_name,
            quantity=quantity,
            price=price,
            expires_at=datetime.utcnow() + timedelta(hours=duration_hours),
        )
        self.session.add(listing)
        await self.session.commit()
        await self.session.refresh(listing)
        return listing

    async def get_active_listings(self, limit: int = 20, offset: int = 0) -> Sequence[MarketListing]:
        result = await self.session.execute(
            select(MarketListing)
            .where(and_(MarketListing.is_active == True, MarketListing.expires_at > datetime.utcnow()))
            .order_by(MarketListing.listed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def search_listings(self, query: str) -> Sequence[MarketListing]:
        result = await self.session.execute(
            select(MarketListing)
            .where(
                and_(
                    MarketListing.is_active == True,
                    MarketListing.item_name.ilike(f"%{query}%"),
                )
            )
            .order_by(MarketListing.price.asc())
        )
        return result.scalars().all()

    async def buy_listing(self, listing_id: int) -> Optional[MarketListing]:
        result = await self.session.execute(
            select(MarketListing).where(
                and_(MarketListing.id == listing_id, MarketListing.is_active == True)
            )
        )
        listing = result.scalar_one_or_none()
        if listing:
            listing.is_active = False
            await self.session.commit()
        return listing

    async def cancel_listing(self, listing_id: int, seller_id: int) -> bool:
        result = await self.session.execute(
            select(MarketListing).where(
                and_(
                    MarketListing.id == listing_id,
                    MarketListing.seller_id == seller_id,
                    MarketListing.is_active == True,
                )
            )
        )
        listing = result.scalar_one_or_none()
        if listing:
            listing.is_active = False
            await self.session.commit()
            return True
        return False

    async def get_player_listings(self, seller_id: int) -> Sequence[MarketListing]:
        result = await self.session.execute(
            select(MarketListing).where(
                and_(MarketListing.seller_id == seller_id, MarketListing.is_active == True)
            )
        )
        return result.scalars().all()


class QuestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_battle(
        self,
        attacker_id: int,
        defender_id: Optional[int],
        battle_type: str,
        result: str,
        rounds: list,
        loot: dict,
        xp_gained: int,
        gold_gained: int,
    ) -> BattleLog:
        log = BattleLog(
            attacker_id=attacker_id,
            defender_id=defender_id,
            battle_type=battle_type,
            result=result,
            rounds=rounds,
            loot=loot,
            xp_gained=xp_gained,
            gold_gained=gold_gained,
        )
        self.session.add(log)
        await self.session.commit()
        return log

    async def get_player_battles(self, player_id: int, limit: int = 10) -> Sequence[BattleLog]:
        result = await self.session.execute(
            select(BattleLog)
            .where((BattleLog.attacker_id == player_id) | (BattleLog.defender_id == player_id))
            .order_by(BattleLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


class MailRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def send(self, sender_id: int, receiver_id: int, subject: str, body: str, attachments: Optional[list] = None) -> Mail:
        mail = Mail(
            sender_id=sender_id,
            receiver_id=receiver_id,
            subject=subject,
            body=body,
            attachments=attachments or [],
        )
        self.session.add(mail)
        await self.session.commit()
        await self.session.refresh(mail)
        return mail

    async def get_inbox(self, player_id: int, limit: int = 20) -> Sequence[Mail]:
        result = await self.session.execute(
            select(Mail)
            .where(Mail.receiver_id == player_id)
            .order_by(Mail.sent_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_read(self, mail_id: int, player_id: int) -> bool:
        result = await self.session.execute(
            select(Mail).where(and_(Mail.id == mail_id, Mail.receiver_id == player_id))
        )
        mail = result.scalar_one_or_none()
        if mail:
            mail.is_read = True
            await self.session.commit()
            return True
        return False

    async def unread_count(self, player_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Mail.id)).where(
                and_(Mail.receiver_id == player_id, Mail.is_read == False)
            )
        )
        return result.scalar_one()


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_event(self, event_type: str, name: str, description: str, data: dict, island_id: Optional[str] = None, duration_hours: int = 24) -> WorldEvent:
        event = WorldEvent(
            event_type=event_type,
            name=name,
            description=description,
            data=data,
            island_id=island_id,
            ends_at=datetime.utcnow() + timedelta(hours=duration_hours),
        )
        self.session.add(event)
        await self.session.commit()
        return event

    async def get_active_events(self) -> Sequence[WorldEvent]:
        result = await self.session.execute(
            select(WorldEvent).where(
                and_(WorldEvent.is_active == True, WorldEvent.ends_at > datetime.utcnow())
            )
        )
        return result.scalars().all()

    async def end_expired_events(self) -> int:
        result = await self.session.execute(
            update(WorldEvent)
            .where(and_(WorldEvent.is_active == True, WorldEvent.ends_at <= datetime.utcnow()))
            .values(is_active=False)
        )
        await self.session.commit()
        return result.rowcount  # type: ignore[return-value]


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def send_message(self, sender_id: int, channel: str, message: str) -> ChatMessage:
        msg = ChatMessage(sender_id=sender_id, channel=channel, message=message)
        self.session.add(msg)
        await self.session.commit()
        return msg

    async def get_recent(self, channel: str, limit: int = 50) -> Sequence[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.channel == channel)
            .order_by(ChatMessage.sent_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
