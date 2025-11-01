from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.unit_of_work import UnitOfWork
from src.infrastructure.db import database_helper


async def get_uow(
    session: AsyncSession = Depends(database_helper.async_session_dependency),
) -> UnitOfWork:
    return UnitOfWork(session)


UoW = Annotated[UnitOfWork, Depends(get_uow)]

# Example:
# from src.core.services.example import ExampleService
#
# async def get_example_service(uow: UoW) -> ExampleService:
#     return ExampleService(uow)
#
# ExampleService = Annotated[ExampleService, Depends(get_example_service)]
