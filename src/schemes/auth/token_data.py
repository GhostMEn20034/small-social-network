from pydantic import BaseModel

class TokenPayload(BaseModel):
    """
    Decoded JWT token payload
    """
    token_type: str
    exp: int
    id: int


class AuthTokens(BaseModel):
    access_token: str # Token to access some data
    refresh_token: str # Token to refresh the access token


class RefreshTokenRequest(BaseModel):
    refresh_token: str