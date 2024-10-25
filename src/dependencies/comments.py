from src.core.configs.content_moderator_config import ContentModeratorConfig
from src.core.database import get_session
from src.core.settings import settings
from src.repositories.comment.implementation import CommentRepositoryImplementation
from src.repositories.like.implementation import LikeRepositoryImplementation
from src.repositories.post.implementation import PostRepositoryImplementation
from src.repositories.unit_of_work.implementation import UnitOfWork
from src.repositories.user.implementation import UserRepositoryImplementation
from src.services.comment.implementation import CommentServiceImplementation
from src.utils.content_moderator.implementation import ContentModerator
from src.utils.reply_generator.implementation import ReplyGenerator


async def get_comment_service() -> CommentServiceImplementation:
    async for session in get_session():  # Use async for to retrieve the session
        content_moderator_config = ContentModeratorConfig(
            api_user=settings.sightengine_api_user,
            api_secret=settings.sightengine_api_secret,
        )
        content_moderator = ContentModerator(config=content_moderator_config)

        reply_generator = ReplyGenerator()

        # Instantiate repositories with the session
        user_repository = UserRepositoryImplementation(session=session)
        post_repository = PostRepositoryImplementation(session=session)
        comment_repository = CommentRepositoryImplementation(session=session)
        like_repository = LikeRepositoryImplementation(session=session)

        # Create the Unit of Work
        unit_of_work = UnitOfWork(
            session=session,
            user_repository=user_repository,
            post_repository=post_repository,
            comment_repository=comment_repository,
            like_repository=like_repository,
        )

        # Create and return the comment service
        return CommentServiceImplementation(
            uow=unit_of_work,
            content_moderator=content_moderator,
            reply_generator=reply_generator,
        )