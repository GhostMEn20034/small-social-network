from abc import ABC, abstractmethod
from typing import List

from src.models.user import User
from src.schemes.comment.create import CreateCommentSchema
from src.schemes.comment.read import CommentReadSchema, CommentWithRepliesSchema, DailyCommentAnalyticItem
from src.schemes.comment.update import CommentUpdateSchema
from src.schemes.common import DateRange


class AbstractCommentService(ABC):

    @abstractmethod
    async def create_comment(self, user: User, comment_data: CreateCommentSchema) -> CommentReadSchema:
        pass

    async def auto_reply_comment(self, comment_id: int) -> None:
        pass

    @abstractmethod
    async def get_top_level_comments(self, post_id: int):
        pass

    @abstractmethod
    async def get_comment_details(self, comment_id: int) -> CommentWithRepliesSchema:
        pass

    @abstractmethod
    async def update_comment(self, comment_id: int, user: User, update_data: CommentUpdateSchema) -> CommentReadSchema:
        pass

    @abstractmethod
    async def like_comment(self, comment_id: int, user: User):
        pass

    @abstractmethod
    async def block_comment(self, comment_id: int, user: User) -> CommentReadSchema:
        pass

    @abstractmethod
    async def delete_comment(self, comment_id: int, user: User) -> None:
        pass

    @abstractmethod
    async def daily_comment_analytic(self, date_range: DateRange, user: User) -> List[DailyCommentAnalyticItem]:
        pass