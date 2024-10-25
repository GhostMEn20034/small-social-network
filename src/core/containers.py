from dependency_injector import providers, containers

from .configs.content_moderator_config import ContentModeratorConfig
from .database import get_session
from .settings import settings
from .configs.jwt_handler_config import JWTHandlerConfig
from src.utils.auth.jwt_handler import JWTHandler
from src.repositories.unit_of_work.implementation import UnitOfWork
from src.repositories.user.implementation import UserRepositoryImplementation
from src.services.user.implementation import UserServiceImplementation
from src.services.auth.implementation import AuthServiceImplementation
from src.repositories.post.implementation import PostRepositoryImplementation
from src.services.post.implementation import PostServiceImplementation
from src.repositories.comment.implementation import CommentRepositoryImplementation
from src.services.comment.implementation import CommentServiceImplementation
from src.repositories.like.implementation import LikeRepositoryImplementation
from src.utils.content_moderator.implementation import ContentModerator
from src.utils.reply_generator.implementation import ReplyGenerator


class Container(containers.DeclarativeContainer):
    db_session = providers.Resource(get_session)

    jwt_config = providers.Singleton(JWTHandlerConfig, secret_key=settings.secret_key)
    jwt_handler = providers.Singleton(JWTHandler, config=jwt_config)

    reply_generator = providers.Singleton(ReplyGenerator)

    content_moderator_config = providers.Singleton(
        ContentModeratorConfig,
        api_user=settings.sightengine_api_user,
        api_secret=settings.sightengine_api_secret,
    )
    content_moderator = providers.Singleton(ContentModerator, config=content_moderator_config)

    user_repository = providers.Factory(UserRepositoryImplementation, session=db_session)
    post_repository = providers.Factory(PostRepositoryImplementation, session=db_session)
    comment_repository = providers.Factory(CommentRepositoryImplementation, session=db_session)
    like_repository = providers.Factory(LikeRepositoryImplementation, session=db_session)

    unit_of_work = providers.Factory(
        UnitOfWork,
        session=db_session,
        user_repository=user_repository, post_repository=post_repository,
        comment_repository=comment_repository, like_repository=like_repository,
    )

    user_service = providers.Factory(UserServiceImplementation, uow=unit_of_work)
    post_service = providers.Factory(PostServiceImplementation, uow=unit_of_work, content_moderator=content_moderator)
    comment_service = providers.Factory(CommentServiceImplementation,
                                        uow=unit_of_work, content_moderator=content_moderator,
                                        reply_generator=reply_generator,
                                        )

    auth_service = providers.Factory(
        AuthServiceImplementation,
        jwt_handler=jwt_handler, uow=unit_of_work
    )
