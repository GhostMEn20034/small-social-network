from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.repositories.base.implementation import GenericRepositoryImplementation
from .abstract import AbstractLikeRepository
from src.models.like import Like


class LikeRepositoryImplementation(GenericRepositoryImplementation[Like], AbstractLikeRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Like)

    async def get_by_comment_id_and_user_id(self, comment_id: int, user_id: int) -> Optional[Like]:
        stmt = (
            select(Like)
            .where(Like.comment_id == comment_id)
            .where(Like.owner_id == user_id)
        )

        like_result = await self._session.exec(stmt)
        return like_result.first()
