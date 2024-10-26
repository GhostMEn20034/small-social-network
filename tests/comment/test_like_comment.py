from typing import List

import pytest
from httpx import AsyncClient

from src.models.comment import Comment
from src.schemes.auth.token_data import AuthTokens


class TestLikeComment:

    @pytest.mark.asyncio
    async def test_like_comment(self, async_client: AsyncClient, tokens: AuthTokens,
                                comments_of_another_user: List[Comment]):
        """
        Test liking a comment.
        """
        comment_id = comments_of_another_user[0].id  # Assuming the comment exists

        # Send PUT request to like the comment
        response = await async_client.put(
            f"/api/v1/comments/{comment_id}/like",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 204

        # Fetch the updated comment to verify the like count
        updated_comment_response = await async_client.get(f"/api/v1/comments/{comment_id}")
        updated_comment = updated_comment_response.json()["comment"]

        # Check that the likes count has been incremented
        assert updated_comment["likes_count"] == 1

    @pytest.mark.asyncio
    async def test_unlike_comment(self, async_client: AsyncClient, tokens: AuthTokens,
                                comments_of_another_user: List[Comment]):
        """
        Test unlike a comment.
        """
        comment_id = comments_of_another_user[0].id  # Assuming the comment exists

        # Send PUT request to the same route again to unlike the comment
        response = await async_client.put(
            f"/api/v1/comments/{comment_id}/like",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 204

        # Fetch the updated comment to verify the like count
        updated_comment_response = await async_client.get(f"/api/v1/comments/{comment_id}")
        updated_comment = updated_comment_response.json()["comment"]

        # Check that the likes count has been decremented
        assert updated_comment["likes_count"] == 0
