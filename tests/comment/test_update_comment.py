from typing import List

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture
from src.models.comment import Comment
from src.models.user import User
from src.schemes.auth.token_data import AuthTokens
from src.schemes.comment.update import CommentUpdateSchema

class TestUpdateComment:

    @pytest.mark.asyncio
    async def test_update_comment_success(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens,
            comments_of_main_user: List[Comment],
            the_user: User
    ):
        """
        Test successful update of a comment.
        """
        # Mock text moderation to allow the content
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )

        # Prepare data for updating the comment
        update_data = CommentUpdateSchema(content="Updated content")

        previous_content = comments_of_main_user[2].content

        # Send PUT request to update the comment
        response = await async_client.put(
            f"/api/v1/comments/{comments_of_main_user[2].id}",
            json=update_data.model_dump(),
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 200
        updated_comment = response.json()
        assert updated_comment["content"] == update_data.content

        # Ensure that moderation function was called
        mock_moderate_text.assert_called_once_with(update_data.content)

        update_data = CommentUpdateSchema(content=previous_content)

        await async_client.put(
            f"/api/v1/comments/{comments_of_main_user[2].id}",
            json=update_data.model_dump(),
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

    @pytest.mark.asyncio
    async def test_update_non_existent_comment(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens
    ):
        """
        Test updating a non-existent comment.
        """
        # Mock text moderation
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )

        # Prepare data for updating a comment
        update_data = CommentUpdateSchema(content="New content")

        # Send PUT request to update a non-existent comment
        response = await async_client.put(
            "/api/v1/comments/99999",  # Non-existent comment ID
            json=update_data.model_dump(),
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 404
        assert response.json() == {"detail": "Not able to apply updates for non-existent comment"}

        # Ensure that moderation function was called
        mock_moderate_text.assert_called_once_with(update_data.content)

    @pytest.mark.asyncio
    async def test_update_comment_not_owner(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens,
            comments_of_another_user: List[Comment],
            the_user: User
    ):
        """
        Test updating a comment that the user does not own.
        """
        # Mock text moderation
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )

        # Prepare data for updating the comment
        update_data = CommentUpdateSchema(content="Trying to update another user's comment")

        # Send PUT request to update the comment
        response = await async_client.put(
            f"/api/v1/comments/{comments_of_another_user[0].id}",
            json=update_data.model_dump(),
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 403
        assert response.json() == {"detail": "Only owner can update the comment"}

        # Ensure that moderation function was called
        mock_moderate_text.assert_called_once_with(update_data.content)

    @pytest.mark.asyncio
    async def test_update_comment_blocked_due_to_inappropriate_content(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens,
            comments_of_main_user: List[Comment],
            the_user: User
    ):
        """
        Test updating a comment with inappropriate content that gets blocked.
        """
        # Mock text moderation to block the content
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=False
        )

        # Prepare data for updating the comment
        update_data = CommentUpdateSchema(content="Really bad content")

        # Send PUT request to update the comment
        response = await async_client.put(
            f"/api/v1/comments/{comments_of_main_user[0].id}",
            json=update_data.model_dump(),
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 200
        updated_comment = response.json()
        assert updated_comment["blocked"] is True  # The comment should be blocked

        # Ensure that moderation function was called
        mock_moderate_text.assert_called_once_with(update_data.content)
