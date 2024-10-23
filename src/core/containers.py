from dependency_injector import providers, containers

from .database import get_session
from src.repositories.user.implementation import UserRepositoryImplementation
from src.repositories.unit_of_work.implementation import UnitOfWork
from src.services.user.implementation import UserServiceImplementation
from .settings import settings
from .configs.jwt_handler_config import JWTHandlerConfig
from src.utils.auth.jwt_handler import JWTHandler
from src.services.auth.implementation import AuthServiceImplementation


class Container(containers.DeclarativeContainer):
    db_session = providers.Resource(get_session)

    jwt_config = providers.Singleton(JWTHandlerConfig, secret_key=settings.secret_key)

    jwt_handler = providers.Singleton(JWTHandler, config=jwt_config)

    user_repository = providers.Factory(UserRepositoryImplementation, session=db_session)

    unit_of_work = providers.Factory(
        UnitOfWork,
        session=db_session, user_repository=user_repository
    )

    user_service = providers.Factory(UserServiceImplementation, uow=unit_of_work)

    auth_service = providers.Factory(
        AuthServiceImplementation,
        jwt_handler=jwt_handler, uow=unit_of_work
    )
