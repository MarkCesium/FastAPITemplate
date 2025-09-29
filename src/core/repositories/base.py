import logging
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, Sequence, TypeVar
from uuid import UUID

from sqlalchemy import Result, delete, func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database import (
    DatabaseOperationException,
    EntityNotFoundException,
    ValidationException,
)
from src.core.models import BaseModel

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


@dataclass
class PaginatedResult(Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[T]:
        try:
            return await self.session.get(self.model, id)
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {e}")
            raise DatabaseOperationException("get entity", str(e))

    async def get_by_id_or_404(self, id: UUID) -> T:
        """Получить по ID или выбросить исключение EntityNotFoundException"""
        entity = await self.get_by_id(id)
        if not entity:
            raise EntityNotFoundException(self.model.__name__, id)
        return entity

    async def find(
        self,
        filters: Optional[List[Any]] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        load_options: Optional[List[Any]] = None,
    ) -> Sequence[T]:
        try:
            query = select(self.model)

            if filters:
                query = query.where(*filters)

            if order_by is not None:
                query = query.order_by(order_by)

            if load_options:
                query = query.options(*load_options)

            if offset:
                query = query.offset(offset)

            if limit:
                query = query.limit(limit)

            result = await self.session.scalars(query)
            return result.all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding {self.model.__name__}: {e}")
            raise DatabaseOperationException("find entities", str(e))

    async def get_all(self, **filter_by: Any) -> Sequence[T]:
        try:
            query = select(self.model).filter_by(**filter_by)
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise DatabaseOperationException("get all entities", str(e))

    async def get_one_or_none(self, **filter_by: Any) -> Optional[T]:
        try:
            query = select(self.model).filter_by(**filter_by)
            result: Result[tuple[T]] = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting one {self.model.__name__}: {e}")
            raise DatabaseOperationException("get entity", str(e))

    async def get_one_or_404(self, **filter_by: Any) -> T:
        entity = await self.get_one_or_none(**filter_by)
        if not entity:
            filter_desc = ", ".join(f"{k}={v}" for k, v in filter_by.items())
            raise EntityNotFoundException(
                f"{self.model.__name__} with {filter_desc}", 0
            )
        return entity

    async def create(self, **data: Any) -> T:
        try:
            entity = self.model(**data)
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            await self.session.rollback()
            raise ValidationException("Data integrity constraint violated")
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            await self.session.rollback()
            raise DatabaseOperationException("create entity", str(e))

    async def update(self, id: UUID, **data: Any) -> T:
        try:
            result = await self.session.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**data)
                .returning(self.model)
            )
            updated_entity = result.scalar_one_or_none()
            if not updated_entity:
                raise EntityNotFoundException(self.model.__name__, id)
            await self.session.flush()
            return updated_entity
        except EntityNotFoundException:
            raise
        except IntegrityError as e:
            logger.error(
                f"Integrity error updating {self.model.__name__} with id {id}: {e}"
            )
            await self.session.rollback()
            raise ValidationException("Data integrity constraint violated")
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} with id {id}: {e}")
            await self.session.rollback()
            raise DatabaseOperationException("update entity", str(e))

    async def patch(self, id: UUID, **data: Any) -> T:
        """Частичное обновление - игнорирует None значения"""
        # Убираем None значения для частичного обновления
        filtered_data = {k: v for k, v in data.items() if v is not None}
        return await self.update(id, **filtered_data)

    async def delete(self, id: UUID) -> None:
        try:
            result = await self.session.execute(
                delete(self.model).where(self.model.id == id)
            )
            if result.rowcount == 0:
                raise EntityNotFoundException(self.model.__name__, id)
            await self.session.flush()
        except EntityNotFoundException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            await self.session.rollback()
            raise DatabaseOperationException("delete entity", str(e))

    async def count(self, filters: Optional[List[Any]] = None) -> int:
        """Подсчёт количества сущностей"""
        try:
            query = select(func.count()).select_from(self.model)
            if filters:
                query = query.where(*filters)
            result = await self.session.scalar(query)
            return result or 0
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise DatabaseOperationException("count entities", str(e))

    async def get_paginated(
        self,
        page: int = 1,
        per_page: int = 10,
        filters: Optional[List[Any]] = None,
        order_by: Optional[Any] = None,
    ) -> PaginatedResult[T]:
        if page < 1:
            raise ValidationException("Page number must be >= 1")
        if per_page < 1:
            raise ValidationException("Per page number must be >= 1")

        try:
            offset = (page - 1) * per_page

            # Получаем общее количество
            total = await self.count(filters)

            # Получаем данные с пагинацией
            items = await self.find(
                filters=filters, limit=per_page, offset=offset, order_by=order_by
            )

            return PaginatedResult(
                items=items,
                total=total,
                page=page,
                per_page=per_page,
                has_next=offset + per_page < total,
                has_prev=page > 1,
            )
        except SQLAlchemyError as e:
            logger.error(f"Error paginating {self.model.__name__}: {e}")
            raise DatabaseOperationException("paginate entities", str(e))

    async def commit(self) -> None:
        """Зафиксировать транзакцию"""
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error committing transaction: {e}")
            await self.session.rollback()
            raise DatabaseOperationException("commit transaction", str(e))

    async def rollback(self) -> None:
        """Откатить транзакцию"""
        try:
            await self.session.rollback()
        except SQLAlchemyError as e:
            logger.error(f"Error rolling back transaction: {e}")
            raise DatabaseOperationException("rollback transaction", str(e))

    async def refresh(self, entity: T) -> T:
        """Обновить состояние сущности из БД"""
        try:
            await self.session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            logger.error(f"Error refreshing {self.model.__name__}: {e}")
            raise DatabaseOperationException("refresh entity", str(e))
