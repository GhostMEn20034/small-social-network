from abc import ABC
from typing import TypeVar, Type, Optional, List

from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.base import BaseModel
from .abstract import AbstractGenericRepository

T = TypeVar("T", bound=BaseModel)

class GenericRepositoryImplementation(AbstractGenericRepository[T], ABC):
    """
    Implementation of Abstract Generic Repository.
    """

    def __init__(self, session: AsyncSession, model_cls: Type[T]) -> None:
        """
        :param session: SQLModel session.
        :param model_cls: SQLModel class type.
        """
        self._session = session
        self._model_cls = model_cls

    def _construct_get_stmt(self, id: int):
        """Creates a SELECT query for retrieving a single record.

        Args:
            id (int):  Record id.

        Returns:
            SelectOfScalar: SELECT statement.
        """
        stmt = select(self._model_cls).where(self._model_cls.id == id)
        return stmt

    async def get_by_id(self, id: int) -> Optional[T]:
        stmt = self._construct_get_stmt(id)
        result = await self._session.exec(stmt)
        return result.first()

    def _construct_list_stmt(self, **filters):
        """Creates a SELECT query for retrieving a multiple records.

        Raises:
            ValueError: Invalid column name.

        Returns:
            SelectOfScalar: SELECT statment.
        """
        stmt = select(self._model_cls)
        where_clauses = []
        for c, v in filters.items():
            if not hasattr(self._model_cls, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(self._model_cls, c) == v)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))
        return stmt

    async def list(self, **filters) -> List[T]:
        stmt = self._construct_list_stmt(**filters)
        result = await self._session.exec(stmt)
        return result.all()

    async def add(self, record: T) -> T:
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def update(self, record: T) -> T:
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def delete(self, record: T) -> None:
        if record is not None:
            await self._session.delete(record)
            await self._session.flush()
