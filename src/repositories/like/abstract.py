from abc import ABC, abstractmethod
from typing import Optional

from src.models.like import Like
from src.repositories.base.abstract import AbstractGenericRepository


class AbstractLikeRepository(AbstractGenericRepository[Like], ABC):

    @abstractmethod
    async def get_by_comment_id_and_user_id(self, comment_id: int, user_id: int) -> Optional[Like]:
        pass
