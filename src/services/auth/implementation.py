import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .abstract import AbstractAuthService
from src.core.exceptions.tokens import InvalidTokenType
from src.repositories.unit_of_work.abstract import AbstractUnitOfWork
from src.utils.auth.jwt_handler import JWTHandler
from src.utils.password_utils import verify_password
from src.schemes.auth.token_data import AuthTokens, TokenPayload
from src.models.user import User


class AuthServiceImplementation(AbstractAuthService):
    def __init__(self, jwt_handler: JWTHandler, uow: AbstractUnitOfWork):
        self._jwt_handler = jwt_handler
        self._uow = uow

    async def provide_tokens(self, form_data: OAuth2PasswordRequestForm) -> AuthTokens:
        async with self._uow:
            user = await self._uow.user_repository.get_by_email(form_data.username)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect email or password"
                )

            hashed_password = user.password

            if not verify_password(form_data.password, hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect email or password"
                )

            token_payload = {
                "id": user.id,
            }

            access_token = self._jwt_handler.create_access_token(token_payload.copy())
            refresh_token = self._jwt_handler.create_refresh_token(token_payload.copy())

            return AuthTokens(
                access_token=access_token,
                refresh_token=refresh_token
            )

    def _decode_token(self, token: str, token_type: str) -> TokenPayload:
        """
        Decodes a JWT token
        :param token: your token.
        :param token_type: token type ("access" or "refresh").
        :return: Decoded token's payload
        """
        try:

            if token_type == 'access':
                payload = self._jwt_handler.decode_access_token(token)
            else:
                payload = self._jwt_handler.decode_refresh_token(token)

        except (jwt.PyJWTError, InvalidTokenType):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenPayload(**payload)

    async def get_user_from_token(self, token: str) -> User:
        token_data = self._decode_token(token, token_type='access')
        async with self._uow:
            user = await self._uow.user_repository.get_by_id(token_data.id)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Could not find user",
                )

            return user


    async def refresh_access_token(self, refresh_token: str) -> str:
        token_data = self._decode_token(refresh_token, token_type='refresh')

        async with self._uow:
            user = await self._uow.user_repository.get_by_id(token_data.id)

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Could not find user",
                )

            payload = {"id": user.id}

            return self._jwt_handler.create_access_token(payload)
