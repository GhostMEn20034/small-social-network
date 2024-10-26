from typing import List

import pytest
from httpx import AsyncClient

from src.models.comment import Comment
from src.models.post import Post
from src.schemes.auth.token_data import AuthTokens


class TestBlockComment:
    @pytest.mark.asyncio
    async def test_block_comment_success(self, async_client: AsyncClient, tokens: AuthTokens,
                                         comments_of_another_user: List[Comment], posts_of_main_user: List[Post]):
        """
        Test blocking a comment successfully.
        """
        comment_id = comments_of_another_user[-1].id  # Assuming the comment exists and belongs to a post of the user

        # Send PUT request to block the comment
        response = await async_client.put(
            f"/api/v1/comments/{comment_id}/block",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 200  # Expecting 200 OK
        blocked_comment = response.json()

        # Check that the comment is blocked
        assert blocked_comment["blocked"] is True
        assert blocked_comment["id"] == comment_id

    @pytest.mark.asyncio
    async def test_block_non_existent_comment(self, async_client: AsyncClient, tokens: AuthTokens):
        """
        Test blocking a non-existent comment.
        """
        non_existent_comment_id = 99999  # Assuming this ID does not exist

        # Send PUT request to block the non-existent comment
        response = await async_client.put(
            f"/api/v1/comments/{non_existent_comment_id}/block",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 404
        assert response.json() == {"detail": "Cannot block non-existent comment"}

    @pytest.mark.asyncio
    async def test_block_comment_without_permission(self, async_client: AsyncClient, tokens: AuthTokens, comments_of_another_user: List[Comment]):
        """
        Test blocking a comment when the user is not the owner of the post.
        """
        comment_id = comments_of_another_user[1].id  # Assuming this comment belongs to another user

        # Send PUT request to block the comment
        response = await async_client.put(
            f"/api/v1/comments/{comment_id}/block",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 403
        assert response.json() == {"detail": "Only owner of the post can block comments under the post"}
