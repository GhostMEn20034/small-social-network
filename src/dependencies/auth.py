from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.core.containers import Container
from src.models.user import User
from src.services.auth.abstract import AbstractAuthService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scheme_name="JWT"
)

@inject
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        auth_service: AbstractAuthService = Depends(Provide[Container.auth_service])) -> User:
    return await auth_service.get_user_from_token(token)
