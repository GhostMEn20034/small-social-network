import pytest
from httpx import AsyncClient
from src.models.user import User
from src.schemes.auth.token_data import AuthTokens

class TestChangePassword:

    @pytest.mark.asyncio
    async def test_change_password(self, async_client: AsyncClient, the_user: User, tokens: AuthTokens):
        # Valid password change
        response = await async_client.put(
            "/api/v1/users/change-password",
            json={
                "old_password": "some_pwd",
                "new_password1": "new_password123",
                "new_password2": "new_password123"
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 204

        # Reset password for future tests
        await async_client.put(
            "/api/v1/users/change-password",
            json={
                "old_password": "new_password123",
                "new_password1": "some_pwd",
                "new_password2": "some_pwd"
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

    @pytest.mark.asyncio
    async def test_change_password_too_short(self, async_client: AsyncClient, tokens: AuthTokens):
        # Password length less than 8 characters
        response = await async_client.put(
            "/api/v1/users/change-password",
            json={
                "old_password": "some_pwd",
                "new_password1": "short",
                "new_password2": "short"
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 422  # FastAPI returns 422 for validation errors
        data = response.json()
        assert any("Password must be at least 8 characters long" in error["msg"] for error in data["detail"])

    @pytest.mark.asyncio
    async def test_change_password_mismatch(self, async_client: AsyncClient, tokens: AuthTokens):
        # Passwords do not match
        response = await async_client.put(
            "/api/v1/users/change-password",
            json={
                "old_password": "some_pwd",
                "new_password1": "new_password123",
                "new_password2": "different_password123"
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 422  # FastAPI returns 422 for validation errors
        data = response.json()
        assert any("Passwords do not match" in error["msg"] for error in data["detail"])
