from src.models.comment import Comment
from src.models.user import User
from src.schemes.comment.create import CreateCommentSchema


def create_comment_from_schema(user: User, create_comment_schema: CreateCommentSchema) -> Comment:
    return Comment(
        owner=user,
        content=create_comment_schema.content,
        post_id=create_comment_schema.post_id,
        parent_id=create_comment_schema.parent_id,
    )