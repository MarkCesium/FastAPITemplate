import logging
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UnitOfWork(AbstractAsyncContextManager["UnitOfWork"]):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session
        # put repositories here, example:
        # self.users = UserRepository(self.session)
        # etc.

    async def __aenter__(self) -> "UnitOfWork":
        logger.debug("Entering UnitOfWork context")
        return self

    async def commit(self) -> None:
        logger.debug("Committing transaction")
        await self.session.commit()

    async def rollback(self) -> None:
        logger.debug("Rolling back transaction")
        await self.session.rollback()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        try:
            if exc_type:
                logger.warning(f"Exception occurred: {exc_type.__name__}")
                await self.rollback()
            else:
                logger.debug("Transaction completed successfully")
                await self.commit()
        finally:
            await self.session.close()
