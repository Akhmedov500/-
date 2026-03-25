"""
Simple migration helper.
For production use Alembic; this module provides a quick init_db() fallback.
"""
from database.base import async_engine, Base


async def run_migrations() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
