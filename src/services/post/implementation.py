from typing import List
from fastapi import HTTPException, status

from src.models.user import User
from src.repositories.unit_of_work.abstract import AbstractUnitOfWork
from src.schemes.post.create import PostCreateSchema
from src.schemes.post.details import PostDetails
from src.schemes.post.list import PostListItemSchema, PostListItemWithAuthorSchema
from src.schemes.post.common import Author
from src.schemes.post.update import UpdatePostSchema
from src.services.post.abstraction import AbstractPostService
from src.utils.content_moderator.abstract import AbstractContentModerator
from src.utils.post.ownership import is_user_owner_of_post
from src.utils.post.post_model import create_post_from_schema, update_post_from_schema


class PostServiceImplementation(AbstractPostService):
    def __init__(self, uow: AbstractUnitOfWork, content_moderator: AbstractContentModerator):
        self._uow = uow
        self._content_moderator = content_moderator

    async def create_post(self, user: User ,create_post_schema: PostCreateSchema) -> PostListItemSchema:
        text_to_moderate = (
            f"{create_post_schema.title}\n"
            f"{create_post_schema.content}"
        )

        is_text_appropriate = await self._content_moderator.moderate_text(text_to_moderate)
        if not is_text_appropriate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Text has content such as sexual harassment, offensive content etc."
            )

        post = create_post_from_schema(user, create_post_schema)
        async with self._uow:
            created_post = await self._uow.post_repository.add(post)

            await self._uow.commit()

            return PostListItemSchema(**created_post.model_dump())

    async def get_user_posts(self, user: User) -> List[PostListItemSchema]:
        posts = []

        async with self._uow:
            post_list = await self._uow.post_repository.list(author_id=user.id)

            await self._uow.commit()

            # Convert each post into PostListItemSchema
            for post in post_list:
                post_schema = PostListItemSchema(
                    id=post.id,  # Assuming `post` has an `id` attribute
                    title=post.title,
                    content=post.content,
                    draft=post.draft,
                    author_id=post.author_id,
                    auto_reply=post.auto_reply,
                    reply_after=post.reply_after,
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                )
                posts.append(post_schema)

            await self._uow.commit()

        return posts

    async def get_all_posts_with_authors(self) -> List[PostListItemWithAuthorSchema]:
        posts_with_authors = []
        async with self._uow:
            post_list = await self._uow.post_repository.get_posts_with_authors()

            for post, author in post_list:
                # Create Author object
                author = Author(
                    first_name=author.first_name,
                    last_name=author.last_name,
                )
                # Create PostListItemWithAuthorSchema object
                post_schema = PostListItemWithAuthorSchema(
                    id=post.id,
                    title=post.title,
                    content=post.content,
                    draft=post.draft,
                    auto_reply=post.auto_reply,
                    author_id=post.author_id,
                    reply_after=post.reply_after,
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    author=author  # Include author information
                )
                posts_with_authors.append(post_schema)

        return posts_with_authors

    async def get_post_with_related_data(self, post_id: int) -> PostDetails:
        async with self._uow:
            post_with_related_data = await self._uow.post_repository.get_post_by_id_with_related_objects(post_id)

            if post_with_related_data is None:
                raise HTTPException(
                    status_code=404,
                    detail="Post not found"
                )

            post, user = post_with_related_data
            post_details = PostDetails(
                **post.model_dump(),
                author=Author(**user.model_dump())
            )

            return post_details

    async def update_post(self, user: User, post_id: int, update_post_data: UpdatePostSchema) -> PostListItemSchema:
        text_to_moderate = (
            f"{update_post_data.title}\n"
            f"{update_post_data.content}"
        )

        is_text_appropriate = await self._content_moderator.moderate_text(text_to_moderate)
        if not is_text_appropriate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Text has content such as sexual harassment, offensive content etc."
            )

        async with self._uow:
            post = await self._uow.post_repository.get_by_id(post_id)
            if post is None:
                raise HTTPException(
                    status_code=404,
                    detail="Post not found"
                )

            is_owner_of_post = is_user_owner_of_post(user, post)
            if not is_owner_of_post:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can update the post"
                )

            update_post_from_schema(update_post_data, post)

            updated_post = await self._uow.post_repository.update(post)

            await self._uow.commit()

            return PostListItemSchema(**updated_post.model_dump())

    async def delete_post(self, user: User, post_id: int) -> None:
        async with self._uow:
            post = await self._uow.post_repository.get_by_id(post_id)
            if post is None:
                raise HTTPException(
                    status_code=404,
                    detail="Post not found"
                )

            is_owner_of_post = is_user_owner_of_post(user, post)
            if not is_owner_of_post:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can delete the post"
                )

            await self._uow.post_repository.delete(post)

            await self._uow.commit()
