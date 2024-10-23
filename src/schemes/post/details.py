from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from .common import Author


class PostDetails(BaseModel):
    id: int
    title: str
    content: str
    draft: bool = False
    auto_reply: bool = False
    author_id: int
    reply_after: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    author: Author
