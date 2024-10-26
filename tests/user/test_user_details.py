import pytest
from httpx import AsyncClient

from src.models.user import User
from src.schemes.auth.token_data import AuthTokens


class TestUpdateUser:

    @pytest.mark.asyncio
    async def test_get_user_details(self, async_client: AsyncClient, the_user: User, tokens: AuthTokens):

        response = await async_client.get("/api/v1/users/details",
                                          headers={"Authorization": f"Bearer {tokens.access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == the_user.email
        assert data["first_name"] == the_user.first_name
