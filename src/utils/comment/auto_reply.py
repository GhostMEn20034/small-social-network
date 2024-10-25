from src.models.comment import Comment
from src.models.post import Post

def schedule_auto_reply(post: Post, comment: Comment):
    from src.tasks.comments import reply_automatically

    countdown = post.reply_after * 60
    return reply_automatically.apply_async((comment.id, ), countdown=countdown)
