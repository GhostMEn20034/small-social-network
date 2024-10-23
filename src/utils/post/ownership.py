from src.models.post import Post
from src.models.user import User


def is_user_owner_of_post(user: User, post: Post):
    return user.id == post.author_id