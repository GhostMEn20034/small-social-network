import pytest
from httpx import AsyncClient

from src.models.user import User
from src.schemes.auth.token_data import AuthTokens
from src.utils.password_utils import hash_password


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_update_user(self, async_client: AsyncClient, the_user: User, tokens: AuthTokens):
        old_email = the_user.email

        response = await async_client.put(
            "/api/v1/users/update",
            json={
                "email": "uwu@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "uwu@example.com"
        assert data["first_name"] == "John"

        await async_client.put(
            "/api/v1/users/update",
            json={
                "email": old_email,
                "first_name": "John",
                "last_name": "Doe",
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

    @pytest.mark.asyncio
    async def test_update_user_with_existing_email(self, async_client: AsyncClient, the_user: User, another_user: User,
                                                   tokens: AuthTokens):
        # Try updating `the_user` to use `another_user`'s email
        response = await async_client.put(
            "/api/v1/users/update",
            json={
                "email": another_user.email,  # Attempting to use the existing user's email
                "first_name": "UpdatedFirstName",
                "last_name": "UpdatedLastName",
                "date_of_birth": "1992-10-10"
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "The user with this email already exists"
