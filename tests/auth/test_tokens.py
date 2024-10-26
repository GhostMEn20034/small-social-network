import pytest
from fastapi import status
from httpx import AsyncClient

from src.schemes.auth.token_data import RefreshTokenRequest
from src.models.user import User


class TestAuthService:

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, the_user: User):

        # Prepare the login payload
        login_data = {
            "username": the_user.email,
            "password": "some_pwd",  # Use the plain password for login
        }

        # Perform the login request
        response = await async_client.post("/api/v1/auth/token", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_incorrect_email(self, async_client: AsyncClient):
        # Prepare the login payload with incorrect email
        login_data = {
            "username": "wrong@example.com",
            "password": "some_pwd",
        }

        # Perform the login request
        response = await async_client.post("/api/v1/auth/token", data=login_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Incorrect email or password"

    @pytest.mark.asyncio
    async def test_login_incorrect_password(self, async_client: AsyncClient, the_user: User):
        # Prepare the login payload with incorrect password
        login_data = {
            "username": the_user.email,
            "password": "wrong_password",
        }

        # Perform the login request
        response = await async_client.post("/api/v1/auth/token", data=login_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Incorrect email or password"

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, async_client: AsyncClient, the_user: User):
        # Simulate login to get tokens
        login_data = {
            "username": the_user.email,
            "password": "some_pwd",
        }
        login_response = await async_client.post("/api/v1/auth/token", data=login_data)
        refresh_token = login_response.json()["refresh_token"]

        # Prepare the refresh token request
        refresh_token_data = RefreshTokenRequest(refresh_token=refresh_token)

        # Perform the refresh token request
        response = await async_client.post("/api/v1/auth/token/refresh", json=refresh_token_data.model_dump())

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), str)  # Ensure the response is a string token

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        # Prepare the refresh token request with invalid token
        refresh_token_data = RefreshTokenRequest(refresh_token="invalid_token")

        # Perform the refresh token request
        response = await async_client.post("/api/v1/auth/token/refresh", json=refresh_token_data.model_dump())

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Could not validate credentials"
