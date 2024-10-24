from typing import List

from fastapi import HTTPException, status

from .abstract import AbstractCommentService
from src.repositories.unit_of_work.abstract import AbstractUnitOfWork
from src.models.user import User
from src.schemes.comment.create import CreateCommentSchema
from src.utils.comment.comment_model import create_comment_from_schema
from src.schemes.comment.read import CommentReadSchema, CommentWithRepliesSchema, DailyCommentAnalyticItem
from src.schemes.comment.update import CommentUpdateSchema
from src.utils.comment.ownership import is_user_owner_of_comment
from src.utils.post.ownership import is_user_owner_of_post
from src.models.like import Like
from src.schemes.common import DateRange


class CommentServiceImplementation(AbstractCommentService):
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def create_comment(self, user: User, comment_data: CreateCommentSchema) -> CommentReadSchema:
        async with self._uow:
            post = await self._uow.post_repository.get_by_id(comment_data.post_id)
            if post is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not able to create comment for non-existent post",
                )

            if comment_data.parent_id is not None:

                parent_comment = await self._uow.comment_repository.get_by_id(comment_data.parent_id)
                if parent_comment is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Not able to create comment for non-existent parent comment",
                    )

            comment_object = create_comment_from_schema(user, comment_data)

            created_comment = await self._uow.comment_repository.add(comment_object)
            await self._uow.commit()
            return CommentReadSchema(**created_comment.model_dump())


    async def get_top_level_comments(self, post_id: int):
        """
        Returns comments as a tree with replies, etc.
        """
        async with self._uow:
            comments = await self._uow.comment_repository.get_top_level_comments(post_id)
            return comments

    async def get_comment_details(self, comment_id: int) -> CommentWithRepliesSchema:
        async with self._uow:
            comment = await self._uow.comment_repository.get_comment_details_and_replies(comment_id)

            if comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not able to get comment details for non-existent comment",
                )

            return CommentWithRepliesSchema(
                comment=comment.model_dump(),
                replies=[reply.model_dump() for reply in comment.replies if reply.blocked == False]
            )

    async def update_comment(self, comment_id: int, user: User ,update_data: CommentUpdateSchema) -> CommentReadSchema:
        async with self._uow:
            comment = await self._uow.comment_repository.get_by_id(comment_id)
            if comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not able to apply updates for non-existent comment",
                )

            if not is_user_owner_of_comment(user, comment):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can update the comment",
                )


            comment.content = update_data.content

            updated_comment = await self._uow.comment_repository.update(comment)
            await self._uow.commit()

            return CommentReadSchema(**updated_comment.model_dump())

    async def like_comment(self, comment_id: int, user: User):
        async with self._uow:
            comment = await self._uow.comment_repository.get_by_id(comment_id)
            if comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cannot like non-existent comment",
                )
            # check whether the comment was liked by the user before
            like_record = await self._uow.like_repository.get_by_comment_id_and_user_id(comment_id, user.id)
            # If there's no record, create a new one and increment like counter in the comment by 1
            if like_record is None:
                like_record = Like(
                    comment_id=comment_id,
                    owner_id=user.id,
                )
                await self._uow.like_repository.add(like_record)
                await self._uow.comment_repository.increment_like_counter(comment)
                await self._uow.commit()

                return None

            # If there's a record, delete the record and decrement like counter in the comment by 1
            await self._uow.like_repository.delete(like_record)
            await self._uow.comment_repository.decrement_like_counter(comment)
            await self._uow.commit()

    async def block_comment(self, comment_id: int, user: User) -> CommentReadSchema:
        async with self._uow:
            comment = await self._uow.comment_repository.get_comment_with_post(comment_id)
            if comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cannot block non-existent comment",
                )

            if not is_user_owner_of_post(user, comment.post):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner of the post can block comments under the post",
                )

            comment.block_comment()

            updated_comment = await self._uow.comment_repository.update(comment)
            await self._uow.commit()

            return CommentReadSchema(**updated_comment.model_dump())

    async def delete_comment(self, comment_id: int, user: User) -> None:
        async with self._uow:
            comment = await self._uow.comment_repository.get_by_id(comment_id)
            if comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cannot delete non-existent comment",
                )

            if not is_user_owner_of_comment(user, comment):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner of the comment can delete the comment",
                )

            await self._uow.comment_repository.delete(comment)
            await self._uow.commit()

    async def daily_comment_analytic(self, date_range: DateRange, user: User) -> List[DailyCommentAnalyticItem]:
        async with self._uow:
            daily_analytic = await self._uow.comment_repository.daily_comment_analytic(date_range, user)

            return daily_analytic
