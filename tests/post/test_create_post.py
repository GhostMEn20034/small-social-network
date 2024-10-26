import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from src.schemes.auth.token_data import AuthTokens


class TestCreatePost:

    @pytest.mark.asyncio
    async def test_create_post_success(self, async_client: AsyncClient, tokens: AuthTokens, mocker: MockerFixture):
        """Test creating a post successfully with valid data."""
        # Mocking the content moderator to simulate that content is fine
        mock_moderator = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )

        response = await async_client.post(
            "/api/v1/posts/",
            json={
                "title": "A Valid Post Title",
                "content": "This is valid content for the post.",
                "draft": True,
                "auto_reply": False,
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == "A Valid Post Title"
        assert response.json()["content"] == "This is valid content for the post."

        assert mock_moderator.called == True

    @pytest.mark.asyncio
    async def test_create_post_missing_title(self, async_client: AsyncClient, tokens: AuthTokens):
        """Test creating a post fails if title is missing."""
        response = await async_client.post(
            "/api/v1/posts/",
            json={
                "content": "This is content for a post without a title.",
                "draft": True,
                "auto_reply": False,
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 422  # Unprocessable Entity
        assert "title" in response.json()["detail"][0]["loc"]

    @pytest.mark.asyncio
    async def test_create_post_inappropriate_content(self, async_client: AsyncClient, tokens: AuthTokens,
                                                     mocker: MockerFixture):
        """Test creating a post fails if the content contains inappropriate text."""
        # Mocking the content moderator to simulate inappropriate content
        mock_moderator = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=False
        )

        response = await async_client.post(
            "/api/v1/posts/",
            json={
                "title": "Inappropriate Content",
                "content": "This content is flagged as inappropriate.",
                "draft": True,
                "auto_reply": False,
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 400  # Bad Request
        assert "Text has content such as sexual harassment, offensive content etc." in response.json()["detail"]
        assert mock_moderator.called == True

    @pytest.mark.asyncio
    async def test_create_post_unauthorized(self, async_client: AsyncClient):
        """Test creating a post without authorization should fail."""
        response = await async_client.post(
            "/api/v1/posts/",
            json={
                "title": "Unauthorized Post",
                "content": "This should not be created because of missing auth."
            }
        )
        assert response.status_code == 401  # Unauthorized
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_post_with_auto_reply(self, async_client: AsyncClient, tokens: AuthTokens,
                                               mocker: MockerFixture):
        """Test creating a post with the auto-reply feature enabled."""
        mock_moderator = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )

        response = await async_client.post(
            "/api/v1/posts/",
            json={
                "title": "Auto-Reply Enabled Post",
                "content": "This post has auto-reply enabled.",
                "auto_reply": True,
                "reply_after": 10
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 201
        assert response.json()["auto_reply"] is True
        assert response.json()["reply_after"] == 10
        assert mock_moderator.called == True

    @pytest.mark.asyncio
    async def test_create_post_auto_reply_missing_reply_after(self, async_client: AsyncClient, tokens: AuthTokens):
        """Test creating a post with auto_reply set to True but without reply_after should return HTTP 422."""
        response = await async_client.post(
            "/api/v1/posts/",
            json={
                "title": "Auto-Reply Without Duration",
                "content": "Attempting to set auto-reply without specifying reply_after.",
                "auto_reply": True,
                "reply_after": None  # Intentionally set to None to trigger validation error
            },
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )
        assert response.status_code == 422  # Unprocessable Entity
