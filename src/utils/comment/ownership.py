from src.models.comment import Comment
from src.models.user import User


def is_user_owner_of_comment(user: User, comment: Comment):
    return user.id == comment.owner_id
