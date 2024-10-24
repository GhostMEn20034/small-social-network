from pydantic import BaseModel


class CommentUpdateSchema(BaseModel):
    content: str
