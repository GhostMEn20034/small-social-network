import asyncio

from asgiref.sync import async_to_sync

from src.celery_worker import celery
from src.dependencies.comments import get_comment_service
from src.services.comment.abstract import AbstractCommentService


@celery.task(name="auto-reply")
def reply_automatically(comment_id: int):
    """
    Automatically replies to a comment using Gemini AI.

    This function utilizes the Gemini AI model to generate
    and post a response to a comment. It retrieves the relevant
    comment details, processes them through Gemini AI, and posts
    the generated reply.

    :param comment_id: Commentary identifier.
    """
    comment_service: AbstractCommentService = async_to_sync(get_comment_service)()

    async_to_sync(comment_service.auto_reply_comment)(comment_id)

