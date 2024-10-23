from abc import ABC, abstractmethod

from fastapi.security import OAuth2PasswordRequestForm

from src.models.user import User
from src.schemes.auth.token_data import AuthTokens


class AbstractAuthService(ABC):

    @abstractmethod
    async def provide_tokens(self, form_data: OAuth2PasswordRequestForm) -> AuthTokens:
        pass

    @abstractmethod
    async def get_user_from_token(self, token: str) -> User:
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> str:
        pass
