from sqlmodel import SQLModel

import app.models  # noqa: F401

from .session import engine, get_session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


__all__ = ("init_db", "drop_db", "reset_db", "get_session")
