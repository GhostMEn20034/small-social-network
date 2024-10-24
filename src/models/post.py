from datetime import datetime, UTC
from sqlmodel import Field, Column, Integer, String, TIMESTAMP, Relationship, ForeignKey, BOOLEAN
from typing import Optional, List

from .user import User
from .base import BaseModel

class Post(BaseModel, table=True):
    __tablename__ = 'posts'

    id: int | None = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    title: str = Field(sa_column=Column("title", String(256), nullable=False))
    content: str = Field(sa_column=Column("content", String, nullable=False))
    draft: bool = Field(
        sa_column=Column(
            "draft",
            BOOLEAN, default=False, nullable=False,
            index=True
        ),
    )

    # Relationship to the User model
    author_id: int = Field(sa_column=Column("author_id", Integer, ForeignKey("users.id"), nullable=False))
    author: User = Relationship(back_populates="posts")
    # Auto-Reply feature
    auto_reply: bool = Field(
        sa_column=Column(
            "auto_reply",
            BOOLEAN, default=False, nullable=False
        ),
        description="Indicates if auto-reply is needed."
    )
    reply_after: Optional[int] = Field(
        sa_column=Column(
            "reply_after",
            Integer, nullable=True
        ),
        description="Time duration after which to auto-reply (in minutes)."
    )
    # Timestamps
    created_at: datetime | None = Field(
        sa_column=Column(
            "created_at", TIMESTAMP(timezone=True),
            default=lambda: datetime.now(UTC),
            nullable=False
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

    # Relationship with Comment model
    comments: List["Comment"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
