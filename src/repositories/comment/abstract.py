from abc import ABC, abstractmethod
from typing import Sequence, Optional, List

from src.models.comment import Comment
from src.models.user import User
from src.repositories.base.abstract import AbstractGenericRepository
from src.schemes.comment.read import DailyCommentAnalyticItem
from src.schemes.common import DateRange


class AbstractCommentRepository(AbstractGenericRepository[Comment], ABC):
    @abstractmethod
    async def get_top_level_comments(self, post_id: int) -> Sequence[Comment]:
        """
        Returns only comments without parent_id (Comment that is not reply to another comment)
        """
        pass

    @abstractmethod
    async def get_comment_details_and_replies(self, comment_id: int) -> Optional[Comment]:
        """
        Returns the comment and its replies
        """
        pass

    @abstractmethod
    async def increment_like_counter(self, record: Comment) -> Comment:
        pass

    @abstractmethod
    async def decrement_like_counter(self, record: Comment) -> Comment:
        pass

    @abstractmethod
    async def get_comment_with_post(self, comment_id: int) -> Optional[Comment]:
        pass

    @abstractmethod
    async def daily_comment_analytic(self, date_range: DateRange, user: User) -> List[DailyCommentAnalyticItem]:
        pass
