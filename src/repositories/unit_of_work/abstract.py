from abc import ABC, abstractmethod

from src.repositories.base.abstract import AbstractGenericRepository
from src.repositories.user.abstract import AbstractUserRepository


class AbstractUnitOfWork(ABC):
    user_repository: AbstractUserRepository

    @abstractmethod
    async def commit(self) -> None:
        """Saves all changes to the database."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Closes the session."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        pass