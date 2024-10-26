from typing import List

import pytest
from httpx import AsyncClient

from src.models.post import Post
from src.schemes.auth.token_data import AuthTokens


class TestDeletePost:
    @pytest.mark.asyncio
    async def test_delete_post_user(self, async_client: AsyncClient, posts_of_main_user: List[Post],
                                    tokens: AuthTokens):
        """Test authorized user deleting their own post."""
        post_to_delete = posts_of_main_user[-1]

        response = await async_client.delete(
            f"/api/v1/posts/{post_to_delete.id}",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_post_not_found(self, async_client: AsyncClient, tokens: AuthTokens):
        """Test trying to delete a post that does not exist."""
        non_existing_post_id = 9999  # Assuming this post ID does not exist

        response = await async_client.delete(
            f"/api/v1/posts/{non_existing_post_id}",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"

    @pytest.mark.asyncio
    async def test_delete_post_by_non_owner(self, async_client: AsyncClient, posts_of_another_user: List[Post],
                                                    tokens: AuthTokens):
        """Test user trying to delete a post they do not own."""
        post_to_delete = posts_of_another_user[0]  # Post created by another user

        response = await async_client.delete(
            f"/api/v1/posts/{post_to_delete.id}",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Only owner can delete the post"
