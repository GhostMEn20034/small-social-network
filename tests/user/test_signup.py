import pytest
from httpx import AsyncClient

from src.models.user import User


class TestSignUp:
    @pytest.mark.asyncio
    async def test_signup(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users/signup",
            json={
                "email": "newuser@test.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
                "password1": "password123",
                "password2": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Doe"

    @pytest.mark.asyncio
    async def test_signup_existing_email(self, async_client: AsyncClient, the_user: User):
        # Attempt to sign up with the same email as `the_user`
        response = await async_client.post(
            "/api/v1/users/signup",
            json={
                "email": the_user.email,  # Using the existing user's email
                "first_name": "Another",
                "last_name": "User",
                "date_of_birth": "1995-05-15",
                "password1": "newpassword123",
                "password2": "newpassword123"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "The user with this email already exists"
