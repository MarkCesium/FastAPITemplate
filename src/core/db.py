import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import PostgresConfig, settings


class DataBaseHelper:
    def __init__(self, config: PostgresConfig) -> None:
        self.engine = create_async_engine(
            url=str(config.url),
            echo=config.echo,
            echo_pool=config.echo_pool,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_pre_ping=config.pool_pre_ping,
            pool_timeout=config.pool_timeout,
        )
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

        self.async_scoped_factory = async_scoped_session(
            self.async_session_factory,
            scopefunc=asyncio.current_task,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def async_session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_scoped_factory() as session:
            yield session


db_helper = DataBaseHelper(
    settings.database,
)
