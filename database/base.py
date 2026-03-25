from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Table,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship

import config


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


# ---------- Association tables ----------

guild_members = Table(
    "guild_members",
    Base.metadata,
    Column("player_id", BigInteger, ForeignKey("players.telegram_id"), primary_key=True),
    Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
    Column("role", String(20), default="member"),
    Column("joined_at", DateTime, default=datetime.utcnow),
)

alliance_members = Table(
    "alliance_members",
    Base.metadata,
    Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
    Column("alliance_id", Integer, ForeignKey("alliances.id"), primary_key=True),
    Column("joined_at", DateTime, default=datetime.utcnow),
)

player_achievements = Table(
    "player_achievements",
    Base.metadata,
    Column("player_id", BigInteger, ForeignKey("players.telegram_id"), primary_key=True),
    Column("achievement_id", String(50), primary_key=True),
    Column("unlocked_at", DateTime, default=datetime.utcnow),
)


# ---------- Models ----------

class Player(Base):
    __tablename__ = "players"

    telegram_id = Column(BigInteger, primary_key=True)
    username = Column(String(100), nullable=True)
    display_name = Column(String(100), nullable=False, default="Pirate")
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    gold = Column(Integer, default=config.STARTING_GOLD)
    energy = Column(Integer, default=config.ENERGY_MAX)
    max_energy = Column(Integer, default=config.ENERGY_MAX)
    health = Column(Integer, default=100)
    max_health = Column(Integer, default=100)
    attack = Column(Integer, default=10)
    defense = Column(Integer, default=5)
    speed = Column(Integer, default=5)
    luck = Column(Integer, default=5)
    current_island = Column(String(50), default=config.STARTING_ISLAND)
    faction_id = Column(String(50), nullable=True)
    faction_reputation = Column(JSON, default=dict)
    inventory = Column(JSON, default=list)
    equipped_items = Column(JSON, default=dict)
    skill_points = Column(Integer, default=0)
    skills = Column(JSON, default=dict)
    quest_progress = Column(JSON, default=dict)
    daily_quests = Column(JSON, default=list)
    daily_quests_reset = Column(DateTime, nullable=True)
    achievements = Column(JSON, default=list)
    stats = Column(JSON, default=dict)
    story_chapter = Column(Integer, default=0)
    story_choices = Column(JSON, default=dict)
    pvp_rating = Column(Integer, default=1000)
    pvp_wins = Column(Integer, default=0)
    pvp_losses = Column(Integer, default=0)
    is_banned = Column(Boolean, default=False)
    last_energy_regen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    ships = relationship("Ship", back_populates="owner", lazy="selectin")
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)
    guild = relationship("Guild", back_populates="members", foreign_keys=[guild_id], lazy="selectin")
    sent_mail = relationship("Mail", foreign_keys="Mail.sender_id", back_populates="sender", lazy="selectin")
    received_mail = relationship("Mail", foreign_keys="Mail.receiver_id", back_populates="receiver", lazy="selectin")
    market_listings = relationship("MarketListing", back_populates="seller", lazy="selectin")


class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(BigInteger, ForeignKey("players.telegram_id"), nullable=False)
    ship_type = Column(String(50), nullable=False, default="sloop")
    name = Column(String(100), default="Unnamed Ship")
    level = Column(Integer, default=1)
    hull_hp = Column(Integer, default=100)
    max_hull_hp = Column(Integer, default=100)
    sail_speed = Column(Integer, default=10)
    cannon_damage = Column(Integer, default=10)
    cargo_capacity = Column(Integer, default=50)
    crew_count = Column(Integer, default=5)
    max_crew = Column(Integer, default=10)
    upgrades = Column(JSON, default=dict)
    cargo = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    durability = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("Player", back_populates="ships")


class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    tag = Column(String(10), unique=True, nullable=False)
    description = Column(Text, default="")
    leader_id = Column(BigInteger, nullable=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    gold = Column(Integer, default=0)
    territory = Column(JSON, default=list)
    perks = Column(JSON, default=dict)
    max_members = Column(Integer, default=config.MAX_GUILD_MEMBERS)
    diplomacy = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("Player", back_populates="guild", foreign_keys=[Player.guild_id], lazy="selectin")
    alliance_id = Column(Integer, ForeignKey("alliances.id"), nullable=True)
    alliance = relationship("Alliance", back_populates="guilds", lazy="selectin")


class Alliance(Base):
    __tablename__ = "alliances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    leader_guild_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    guilds = relationship("Guild", back_populates="alliance", lazy="selectin")


class MarketListing(Base):
    __tablename__ = "market_listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(BigInteger, ForeignKey("players.telegram_id"), nullable=False)
    item_id = Column(String(50), nullable=False)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Integer, nullable=False)
    listed_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    seller = relationship("Player", back_populates="market_listings")


class Mail(Base):
    __tablename__ = "mail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, ForeignKey("players.telegram_id"), nullable=False)
    receiver_id = Column(BigInteger, ForeignKey("players.telegram_id"), nullable=False)
    subject = Column(String(200), default="")
    body = Column(Text, default="")
    attachments = Column(JSON, default=list)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("Player", foreign_keys=[sender_id], back_populates="sent_mail")
    receiver = relationship("Player", foreign_keys=[receiver_id], back_populates="received_mail")


class WorldEvent(Base):
    __tablename__ = "world_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    data = Column(JSON, default=dict)
    island_id = Column(String(50), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class BattleLog(Base):
    __tablename__ = "battle_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    attacker_id = Column(BigInteger, nullable=False)
    defender_id = Column(BigInteger, nullable=True)
    battle_type = Column(String(20), default="pve")
    result = Column(String(20), default="")
    rounds = Column(JSON, default=list)
    loot = Column(JSON, default=dict)
    xp_gained = Column(Integer, default=0)
    gold_gained = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, nullable=False)
    channel = Column(String(50), default="global")
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)


async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
