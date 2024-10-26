from typing import List
import pytest
from httpx import AsyncClient

from src.models.comment import Comment
from src.schemes.auth.token_data import AuthTokens


class TestDeleteComment:
    @pytest.mark.asyncio
    async def test_delete_comment_success(self, async_client: AsyncClient, tokens: AuthTokens,
                                          comments_of_main_user: List[Comment]):
        """
        Test successfully deleting a comment.
        """
        comment_id = comments_of_main_user[-1].id  # Assuming the comment exists and belongs to the user

        # Send DELETE request to delete the comment
        response = await async_client.delete(
            f"/api/v1/comments/{comment_id}",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 204  # Expecting 204 No Content

    @pytest.mark.asyncio
    async def test_delete_non_existent_comment(self, async_client: AsyncClient, tokens: AuthTokens):
        """
        Test deleting a non-existent comment.
        """
        non_existent_comment_id = 99999  # Assuming this ID does not exist

        # Send DELETE request to delete the non-existent comment
        response = await async_client.delete(
            f"/api/v1/comments/{non_existent_comment_id}",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 404
        assert response.json() == {"detail": "Cannot delete non-existent comment"}

    @pytest.mark.asyncio
    async def test_delete_comment_without_permission(self, async_client: AsyncClient, tokens: AuthTokens,
                                                     comments_of_another_user: List[Comment]):
        """
        Test deleting a comment when the user is not the owner.
        """
        comment_id = comments_of_another_user[0].id  # Assuming this comment belongs to another user

        # Send DELETE request to delete the comment
        response = await async_client.delete(
            f"/api/v1/comments/{comment_id}",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 403
        assert response.json() == {"detail": "Only owner of the comment can delete the comment"}