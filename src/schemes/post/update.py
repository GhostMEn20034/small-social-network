from typing import Optional
from pydantic import BaseModel, conint


class UpdatePostSchema(BaseModel):
    title: str
    content: str
    draft: bool = False
    auto_reply: bool = False
    reply_after: Optional[conint(gt=0)] = None
