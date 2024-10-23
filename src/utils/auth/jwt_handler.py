import jwt
from datetime import datetime, timedelta, UTC
from typing import Any, Dict

from src.core.configs.jwt_handler_config import JWTHandlerConfig
from src.core.exceptions.tokens import InvalidTokenType


class JWTHandler:
    """
    A handler for creating and decoding JSON Web Tokens (JWT).
    """
    def __init__(self, config: JWTHandlerConfig):
        self.config = config

    def create_access_token(self, data: Dict[str, Any], expires_delta: timedelta = None) -> str:
        """
        Creates a JWT access token with the provided data and expiration time.

        :param data: The data to be encoded in the token (e.g., user ID, roles).
        :param expires_delta: The custom expiration time for the token.
                If not provided, the default expiration time is used.
        """
        if expires_delta:
            expiration = datetime.now(UTC) + expires_delta
        else:
            expiration = datetime.now(UTC) + timedelta(minutes=self.config.access_token_expire_minutes)

        # Add the token type to the payload
        data.update({"exp": expiration, "token_type": "access"})
        token = jwt.encode(data, self.config.secret_key, algorithm=self.config.algorithm)
        return token

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Creates a JWT refresh token with the provided data and a default expiration time.

        :param data: The data to be encoded in the refresh token.
        """
        expiration = datetime.now(UTC) + timedelta(minutes=self.config.refresh_token_expire_minutes)

        # Add the token type to the payload
        data.update({"exp": expiration, "token_type": "refresh"})
        token = jwt.encode(data, self.config.secret_key, algorithm=self.config.algorithm)
        return token

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        """
        Decodes a JWT access token and retrieves the original data.

        :param token: The JWT access token to decode.
        """
        payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])

        # Ensure that the token is access token
        if payload.get("token_type") != "access":
            raise InvalidTokenType(expected_type="access", actual_type=payload.get("token_type"))

        return payload

    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Decodes a JWT refresh token and retrieves the original data.

        :param token: The JWT refresh token to decode.
        """
        payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])

        # Ensure that the token is refresh token
        if payload.get("token_type") != "refresh":
            raise InvalidTokenType(expected_type="refresh", actual_type=payload.get("token_type"))

        return payload
