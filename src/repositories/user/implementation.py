from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.repositories.base.implementation import GenericRepositoryImplementation
from .abstract import AbstractUserRepository


class UserRepositoryImplementation(GenericRepositoryImplementation[User], AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self._session.exec(stmt)
        return result.first()
