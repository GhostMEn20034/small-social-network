from datetime import datetime, UTC
from typing import Optional
from sqlmodel import Field, Column, Integer, ForeignKey, Relationship, TIMESTAMP

from .base import BaseModel
from .comment import Comment
from .user import User


class Like(BaseModel, table=True):
    """
    Each 'like' is associated with both a user (the one who liked the comment) and a comment.
    This model captures which user liked which comment, along with the timestamp of when the like occurred.
    """
    __tablename__ = 'likes'

    id: int | None = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))

    # Relationship to the Comment model
    comment_id: int = Field(sa_column=Column("comment_id", Integer, ForeignKey("comments.id"), nullable=False))
    comment: Optional[Comment] = Relationship(back_populates="likes")

    # Owner of the like (User)
    owner_id: int = Field(sa_column=Column("owner_id", Integer, ForeignKey("users.id"), nullable=False))
    owner: Optional[User] = Relationship(back_populates="likes")

    # Timestamps
    created_at: datetime | None = Field(
        sa_column=Column(
            "created_at", TIMESTAMP(timezone=True),
            default=lambda: datetime.now(UTC),
            nullable=False
        )
    )