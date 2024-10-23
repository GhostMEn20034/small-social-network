from typing import Sequence, Tuple, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.repositories.base.implementation import GenericRepositoryImplementation
from .abstract import AbstractPostRepository
from src.models.post import Post
from src.models.user import User


class PostRepositoryImplementation(GenericRepositoryImplementation[Post], AbstractPostRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Post)

    async def get_posts_with_authors(self) -> Sequence[tuple[Post, User]]:
        stmt = (
            select(Post, User).
            where(Post.draft == False).
            join(User)
        )

        result = await self._session.exec(stmt)

        # Fetch all posts with authors
        posts_with_authors = result.all()

        return posts_with_authors

    async def get_post_by_id_with_related_objects(self, post_id: int) -> Optional[Tuple[Post, User]]:
        stmt = (
            select(Post, User)
            .join(User)
            .where(Post.id == post_id)
        )

        result = await self._session.exec(stmt)

        # Fetch the single post with the author
        post_with_related_data = result.one_or_none()  # This returns a tuple or None

        if post_with_related_data:
            post, user = post_with_related_data  # Unpack the tuple
            return post, user  # Returning the tuple (Post, User)

        return None  # No post found