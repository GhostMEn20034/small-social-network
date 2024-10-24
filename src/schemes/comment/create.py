from typing import Optional

from pydantic import BaseModel


class CreateCommentSchema(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None


