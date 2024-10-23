from abc import ABC, abstractmethod
from typing import List

from src.models.user import User
from src.schemes.post.create import PostCreateSchema
from src.schemes.post.details import PostDetails
from src.schemes.post.list import PostListItemSchema, PostListItemWithAuthorSchema
from src.schemes.post.update import UpdatePostSchema


class AbstractPostService(ABC):
    @abstractmethod
    async def create_post(self, user: User ,create_post_schema: PostCreateSchema) -> PostListItemSchema:
        pass

    @abstractmethod
    async def get_user_posts(self, user: User) -> List[PostListItemSchema]:
        """
        :returns All posts related to specific user.
        """
        pass

    @abstractmethod
    async def get_all_posts_with_authors(self) -> List[PostListItemWithAuthorSchema]:
        pass

    @abstractmethod
    async def get_post_with_related_data(self, post_id: int) -> PostDetails:
        pass

    @abstractmethod
    async def update_post(self, user: User, post_id: int, update_post_data: UpdatePostSchema) -> PostListItemSchema:
        pass

    @abstractmethod
    async def delete_post(self, user: User, post_id: int) -> None:
        pass
