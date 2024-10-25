from typing import List

from fastapi import HTTPException, status

from .abstract import AbstractCommentService
from src.repositories.unit_of_work.abstract import AbstractUnitOfWork
from src.models.user import User
from src.models.comment import Comment
from src.schemes.comment.create import CreateCommentSchema
from src.utils.comment.comment_model import create_comment_from_schema
from src.schemes.comment.read import CommentReadSchema, CommentWithRepliesSchema, DailyCommentAnalyticItem
from src.schemes.comment.update import CommentUpdateSchema
from src.utils.comment.ownership import is_user_owner_of_comment
from src.utils.post.ownership import is_user_owner_of_post
from src.models.like import Like
from src.schemes.common import DateRange
from src.utils.content_moderator.abstract import AbstractContentModerator
from src.utils.comment.auto_reply import schedule_auto_reply
from src.utils.reply_generator.abstract import AbstractReplyGenerator


class CommentServiceImplementation(AbstractCommentService):
    def __init__(self, uow: AbstractUnitOfWork, content_moderator: AbstractContentModerator,
                 reply_generator: AbstractReplyGenerator):
        self._uow = uow
        self._content_moderator = content_moderator
        self._reply_generator = reply_generator

    def _create_prompt_from_post_and_comment(self, comment: Comment) -> str:
        """
        Returns prompt created from post and comment objects
        :param comment: Comment object, make sure that you have joined a post to the comment
        """
        prompt = (
            f"Post Title: {comment.post.title}\n"
            f"Post Text: {comment.post.content}\n\n"
            f"Comment: {comment.content}\n"
        )


        return prompt


    async def create_comment(self, user: User, comment_data: CreateCommentSchema) -> CommentReadSchema:
        block_comment = False

        text_to_moderate = comment_data.content
        is_text_appropriate = await self._content_moderator.moderate_text(text_to_moderate)

        if not is_text_appropriate:
            block_comment = True

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
            if block_comment:
                comment_object.block_comment()

            created_comment = await self._uow.comment_repository.add(comment_object)
            await self._uow.commit()

            # If comment is not blocked and auto_reply feature for a specific post is enabled
            # Then schedule auto reply
            if not block_comment and post.auto_reply:
                schedule_auto_reply(post, created_comment)

            return CommentReadSchema(**created_comment.model_dump())

    async def auto_reply_comment(self, comment_id: int) -> None:
        """
        Automatically responds to the specified comment under the post.
        :param comment_id: ID of a comment that needs to be answered.
        """
        async with self._uow:
            comment = await self._uow.comment_repository.get_comment_with_post(comment_id)

            prompt = (
                "Given a post title and post text.\n"
                "You need to answer the comment. Answer should be compact.\n"
                "DON'T USE LISTS, TABLES, ETC. \n"
            ) + self._create_prompt_from_post_and_comment(comment)

            response = await self._reply_generator.generate_reply(prompt)

            auto_generated_comment = Comment(
                content=response,
                post_id=comment.post_id,
                owner_id=comment.post.author_id,
                parent_id=comment.id,
            )

            await self._uow.comment_repository.add(auto_generated_comment)
            await self._uow.commit()

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
        block_comment = False

        text_to_moderate = update_data.content
        is_text_appropriate = await self._content_moderator.moderate_text(text_to_moderate)

        if not is_text_appropriate:
            block_comment = True

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

            if block_comment:
                comment.block_comment()

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
