import logging
from typing import Any, Generic, Optional, Sequence, Tuple, Type, TypeVar

from sqlalchemy import Result, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import BaseModel

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[T]:
        return await self.session.get(self.model, id)
    
    async def get_all(self, **filter_by: Any) -> Sequence[T]:
        result = await self.session.scalars(select(self.model).filter_by(**filter_by))
        return result.all()

    async def get_one_or_none(self, **filter_by: Any) -> Optional[T]:        
        query = select(self.model).filter_by(**filter_by)
        result: Result[Tuple[T]] = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, **data: Any) -> T:
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.commit()
        return entity
    
    async def update(self, id: int, **data: Any) -> Optional[T]:
        result = await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(self.model)
        )
        await self.session.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, id: int) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
