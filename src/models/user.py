from datetime import datetime, date, UTC
from typing import List

from pydantic import EmailStr
from sqlmodel import Field, Column, String, Date, TIMESTAMP, Relationship

from .base import BaseModel


class User(BaseModel, table=True):
    __tablename__ = 'users'

    email: EmailStr = Field(sa_column=Column("email", String(256), unique=True, index=True))
    first_name: str = Field(sa_column=Column("first_name", String(128)))
    last_name: str = Field(sa_column=Column("last_name", String(128)))
    password: str = Field(sa_column=Column("password", String(256)))

    date_of_birth: date | None = Field(sa_column=Column("date_of_birth", Date, nullable=True))

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

    # Relationship with Post model
    posts: List["Post"] = Relationship(back_populates="author")
    # Relationship with Comment model
    comments: List["Comment"] = Relationship(back_populates="owner")
    likes: List["Like"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
