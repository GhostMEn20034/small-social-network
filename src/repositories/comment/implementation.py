from typing import Sequence, Optional, List
from sqlalchemy.orm import joinedload
from sqlmodel import select, case, func, cast, Date
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.comment import Comment
from src.repositories.base.implementation import GenericRepositoryImplementation
from .abstract import AbstractCommentRepository
from src.models.post import Post
from src.models.user import User
from src.schemes.common import DateRange
from src.schemes.comment.read import DailyCommentAnalyticItem


class CommentRepositoryImplementation(GenericRepositoryImplementation[Comment], AbstractCommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Comment)

    async def get_top_level_comments(self, post_id: int) -> Sequence[Comment]:
        # Fetch top-level comments for the specified post
        stmt = (
            select(Comment)
            .where(Comment.post_id == post_id)
            .where(Comment.parent_id.is_(None))  # Only top-level comments
            .where(Comment.blocked == False)  # Filter out blocked comments
        )

        # Execute the statement
        top_comments = await self._session.exec(stmt)
        comments_list = top_comments.all()

        return comments_list

    async def get_comment_details_and_replies(self, comment_id: int) -> Optional[Comment]:
        stmt = (
            select(Comment)
            .options(joinedload(Comment.replies))
            .where(Comment.id == comment_id)
            .where(Comment.blocked == False)
        )

        comment_result = await self._session.exec(stmt)

        comment = comment_result.first()

        return comment

    async def increment_like_counter(self, record: Comment) -> Comment:
        record.likes_count = Comment.likes_count + 1
        return record

    async def decrement_like_counter(self, record: Comment) -> Comment:
        record.likes_count = Comment.likes_count - 1
        return record

    async def get_comment_with_post(self, comment_id: int) -> Optional[Comment]:
        # Define the query to get the comment along with its related post
        stmt = (
            select(Comment, Post) # Selecting both Comment and Post
            .where(Comment.id == comment_id)
            .join(Post)  # Join condition
        )

        result = await self._session.exec(stmt)

        first_object = result.first()

        if first_object is None:
            return None

        comment, post = first_object  # Unpacking the results

        # Attach the post to the comment for easier access
        comment.post = post

        return comment

    async def daily_comment_analytic(self, date_range: DateRange, user: User) -> List[DailyCommentAnalyticItem]:
        # Query to get the count of comments and blocked comments per day
        query = (
            select(
                cast(Comment.created_at, Date).label("comment_date"),  # Extracting date part
                func.count(Comment.id).label("total_comments"),
                func.sum(case((Comment.blocked == True, 1), else_=0)).label("blocked_comments")
            )
            .join(Post)
            .where(
                cast(Comment.created_at, Date) >= date_range.date_from,
                cast(Comment.created_at, Date) <= date_range.date_to,
                Post.author_id == user.id,
            )
            .group_by(cast(Comment.created_at, Date))
            .order_by(cast(Comment.created_at, Date))
        )

        # Execute the query and get results
        results = await self._session.exec(query)
        daily_breakdown = results.all()

        # Convert results into a list of dictionaries
        response_data = [
            DailyCommentAnalyticItem(
                date=str(row.comment_date),
                total_comments=row.total_comments,
                blocked_comments=row.blocked_comments,
            )
            for row in daily_breakdown
        ]

        return response_data
