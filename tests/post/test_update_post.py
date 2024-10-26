from typing import List

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from src.models.post import Post
from src.schemes.auth.token_data import AuthTokens


class TestUpdatePost:

    @pytest.mark.asyncio
    async def test_update_post_success(self, async_client: AsyncClient, posts_of_main_user: List[Post], tokens: AuthTokens,
                                       mocker: MockerFixture):
        """Test successful post update."""
        # Mocking the content moderator to simulate that content is fine
        mock_moderator = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )

        previous_title = posts_of_main_user[0].title

        updated_data = {
            "title": "Updated Title",
            "content": posts_of_main_user[0].content,
            "draft": posts_of_main_user[0].draft,
            "auto_reply": posts_of_main_user[0].auto_reply,
            "reply_after": posts_of_main_user[0].reply_after,
        }

        response = await async_client.put(
            f"/api/v1/posts/{posts_of_main_user[0].id}",
            json=updated_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["title"] == updated_data["title"]
        assert response.json()["content"] == updated_data["content"]
        assert mock_moderator.called == True

        # Assign old post title for future tests
        previous_data = {
            "title": previous_title,
            "content": posts_of_main_user[0].content,
            "draft": posts_of_main_user[0].draft,
            "auto_reply": posts_of_main_user[0].auto_reply,
            "reply_after": posts_of_main_user[0].reply_after,
        }

        await async_client.put(
            f"/api/v1/posts/{posts_of_main_user[0].id}",
            json=previous_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

    @pytest.mark.asyncio
    async def test_update_post_not_found(self, async_client: AsyncClient, tokens: AuthTokens, mocker: MockerFixture):
        """Test updating a non-existing post."""
        # Mocking the content moderator to simulate that content is fine
        mock_moderator = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )

        updated_data = {
            "title": "New Title",
            "content": "Content for non-existing post.",
            "draft": False,
            "auto_reply": False,
            "reply_after": None
        }

        response = await async_client.put(
            "/api/v1/posts/9999",  # Assuming 9999 does not exist
            json=updated_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"

        assert mock_moderator.called == True

    @pytest.mark.asyncio
    async def test_update_post_not_owner(self, async_client: AsyncClient, posts_of_another_user: List[Post], tokens: AuthTokens):
        """Test Only owner can update its post"""
        updated_data = {
            "title": "Unauthorized Update",
            "content": "Content for unauthorized update.",
            "draft": False,
            "auto_reply": False,
            "reply_after": None
        }

        response = await async_client.put(
            f"/api/v1/posts/{posts_of_another_user[0].id}",
            json=updated_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Only owner can update the post"

    @pytest.mark.asyncio
    async def test_update_post_auto_reply_missing_reply_after(self, async_client: AsyncClient, tokens: AuthTokens):
        """Test updating a post with auto_reply set to True but without reply_after should return HTTP 422."""
        updated_data = {
            "title": "New Title",
            "content": "Content for non-existing post.",
            "draft": False,
            "auto_reply": True,
            "reply_after": None
        }

        response = await async_client.put(
            "/api/v1/posts/1",  # Assuming 9999 does not exist
            json=updated_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.asyncio
    async def test_update_post_inappropriate_content(self, async_client: AsyncClient, posts_of_main_user: List[Post],
                                       tokens: AuthTokens,
                                       mocker: MockerFixture):
        """Test updating a post fails if the content contains inappropriate text."""
        # Mocking the content moderator to simulate that content is inappropriate
        mock_moderator = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=False
        )

        updated_data = {
            "title": "Really Bad Title",
            "content": posts_of_main_user[0].content,
            "draft": posts_of_main_user[0].draft,
            "auto_reply": posts_of_main_user[0].auto_reply,
            "reply_after": posts_of_main_user[0].reply_after,
        }

        response = await async_client.put(
            f"/api/v1/posts/{posts_of_main_user[0].id}",
            json=updated_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 400  # Bad Request
        assert "Text has content such as sexual harassment, offensive content etc." in response.json()["detail"]
        assert mock_moderator.called == True
