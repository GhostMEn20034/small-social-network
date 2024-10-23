from abc import ABC, abstractmethod
from typing import Sequence, Optional, Tuple

from src.models.post import Post
from src.models.user import User
from src.repositories.base.abstract import AbstractGenericRepository


class AbstractPostRepository(AbstractGenericRepository[Post], ABC):

    @abstractmethod
    async def get_posts_with_authors(self) -> Sequence[tuple[Post, User]]:
        pass

    @abstractmethod
    async def get_post_by_id_with_related_objects(self, post_id: int) -> Optional[Tuple[Post, User]]:
        pass