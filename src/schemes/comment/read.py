from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, conint


class CommentReadSchema(BaseModel):
    id: int
    content: str
    likes_count: conint(ge=0)
    post_id: int
    owner_id: int
    parent_id: Optional[int]
    blocked: bool
    blocked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class CommentWithRepliesSchema(BaseModel):
    comment: CommentReadSchema
    replies: Optional[List[CommentReadSchema]] = []


class DailyCommentAnalyticItem(BaseModel):
    date: date
    total_comments: int
    blocked_comments: int

