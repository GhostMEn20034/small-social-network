from datetime import datetime, UTC
from typing import Optional, List
from pydantic import conint
from sqlmodel import Field, Column, Integer, String, Relationship, ForeignKey, BOOLEAN, TIMESTAMP

from .base import BaseModel
from .post import Post
from .user import User


class Comment(BaseModel, table=True):
    __tablename__ = 'comments'

    id: int | None = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    content: str = Field(sa_column=Column("content", String, nullable=False))

    likes_count: conint(ge=0) = Field(sa_column=Column("likes", Integer, default=0, nullable=False))
    likes: List["Like"] = Relationship(back_populates="comment", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    # Relationship to the Post model
    post_id: int = Field(sa_column=Column("post_id", Integer, ForeignKey("posts.id"), nullable=False))
    post: Optional[Post] = Relationship(back_populates="comments")

    # Owner of the comment (User)
    owner_id: int = Field(sa_column=Column("owner_id", Integer, ForeignKey("users.id"), nullable=False))
    owner: User = Relationship(back_populates="comments")  # Back-populates 'comments' in User model

    # Reply functionality
    parent_id: Optional[int] = Field(sa_column=Column("parent_id", Integer, ForeignKey("comments.id"), nullable=True))
    replies: List["Comment"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    parent: Optional["Comment"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={"remote_side": "Comment.id"}
    )

    # Block functionality
    blocked: bool = Field(sa_column=Column("blocked", BOOLEAN, default=False, nullable=False))
    blocked_at: Optional[datetime] = Field(
        sa_column=Column("blocked_at", TIMESTAMP(timezone=True), nullable=True),
        description="Timestamp when the comment was blocked."
    )

    # Timestamps
    created_at: datetime | None = Field(
        sa_column=Column(
            "created_at", TIMESTAMP(timezone=True),
            default=lambda: datetime.now(UTC),
            nullable=False,
            index=True,
        )
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            "updated_at", TIMESTAMP(timezone=True),
            default=lambda: datetime.now(UTC),
            onupdate=lambda: datetime.now(UTC),
            nullable=False
        )
    )

    def block_comment(self):
        self.blocked = True
        self.blocked_at = datetime.now(UTC)