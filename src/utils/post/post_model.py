from src.models.post import Post
from src.models.user import User
from src.schemes.post.create import PostCreateSchema
from src.schemes.post.update import UpdatePostSchema


def create_post_from_schema(user: User, create_post_data: PostCreateSchema) -> Post:
    return Post(
            title=create_post_data.title,
            content=create_post_data.content,
            draft=create_post_data.draft,
            author=user,
            auto_reply=create_post_data.auto_reply,
            reply_after=create_post_data.reply_after,
        )

def update_post_from_schema(update_post_data: UpdatePostSchema, post: Post) -> None:
    post.title = update_post_data.title
    post.content = update_post_data.content
    post.draft = update_post_data.draft
    post.auto_reply = update_post_data.auto_reply
    post.reply_after = update_post_data.reply_after
