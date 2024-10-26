from typing import List
import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from src.models.comment import Comment
from src.models.post import Post
from src.models.user import User
from src.schemes.auth.token_data import AuthTokens


class TestCreateComment:

    @pytest.mark.asyncio
    async def test_create_comment(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens,
            posts_of_main_user: List[Post],
    ):
        """
        Test the creation of a new comment with a normal content (No obscene language, etc.).
        """
        # Mock text moderation and schedule_auto_reply
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )
        mock_schedule_auto_reply = mocker.patch(
            "src.services.comment.implementation.schedule_auto_reply",
            return_value=None
        )

        # Prepare data for creating a new comment
        comment_data = {
            "content": "This is a test comment",
            "post_id": posts_of_main_user[0].id, # Post With auto-reply enabled
            "parent_id": None
        }

        # Send POST request to create the comment
        response = await async_client.post(
            "/api/v1/comments/",
            json=comment_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 201
        comment = response.json()

        # Validate comment structure
        assert comment["content"] == comment_data["content"]
        assert comment["post_id"] == comment_data["post_id"]
        assert comment["owner_id"] == posts_of_main_user[0].author_id
        assert comment["blocked"] is False  # Because mock_moderate_text returned True

        # Verify that moderation function was called correctly
        mock_moderate_text.assert_called_once_with(comment_data["content"])
        # Verify that schedule auto reply wasn't called
        assert mock_schedule_auto_reply.called == True

    @pytest.mark.asyncio
    async def test_create_comment_with_inappropriate_content(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens,
            posts_of_main_user: List[Post],
    ):
        """
        Content with inappropriate content must be blocked.
        """
        # Mock text moderation and schedule_auto_reply
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=False
        )
        mock_schedule_auto_reply = mocker.patch(
            "src.services.comment.implementation.schedule_auto_reply",
            return_value=None
        )

        # Prepare data for creating a new comment
        comment_data = {
            "content": "Some bad content",
            "post_id": posts_of_main_user[0].id, # Post with auto reply
            "parent_id": None
        }

        response = await async_client.post(
            "/api/v1/comments/",
            json=comment_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response for blocked comment
        assert response.status_code == 201
        comment = response.json()
        assert comment["blocked"] is True  # This time the comment is blocked
        assert comment["blocked_at"] is not None  # Blocked comments should have a timestamp

        mock_moderate_text.assert_called()

        # Verify schedule_auto_reply was not called due to the comment being blocked
        mock_schedule_auto_reply.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_comment_with_reply(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens,
            comments_of_another_user: List[Comment],
            the_user: User,
    ):
        """
        Test the creation of reply.
        """
        # Mock text moderation and schedule_auto_reply
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )
        mock_schedule_auto_reply = mocker.patch(
            "src.services.comment.implementation.schedule_auto_reply",
            return_value=None
        )

        # Prepare data for creating a new comment
        comment_data = {
            "content": "This is a test reply",
            "post_id": comments_of_another_user[0].post_id, # Post with auto_reply enabled
            "parent_id": comments_of_another_user[0].id
        }

        # Send POST request to create the comment
        response = await async_client.post(
            "/api/v1/comments/",
            json=comment_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 201
        comment = response.json()

        # Validate comment structure
        assert comment["content"] == comment_data["content"]
        assert comment["post_id"] == comment_data["post_id"]
        assert comment["owner_id"] == the_user.id
        assert comment["blocked"] is False  # Because mock_moderate_text returned True
        assert comment["parent_id"] == comments_of_another_user[0].id

        # Verify that moderation function was called correctly
        mock_moderate_text.assert_called_once_with(comment_data["content"])
        # Verify that schedule auto reply was called
        assert mock_schedule_auto_reply.called == True

    @pytest.mark.asyncio
    async def test_create_comment_with_non_existent_parent(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens,
    ):
        """
        Test the creation of a reply with a non-existent parent comment.
        """
        # Mock text moderation and schedule_auto_reply
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )
        mock_schedule_auto_reply = mocker.patch(
            "src.services.comment.implementation.schedule_auto_reply",
            return_value=None
        )
        # Prepare data for creating a new comment with a non-existent parent_id
        comment_data = {
            "content": "This is a test reply",
            "post_id": 1,  # Assuming a valid post ID
            "parent_id": 99999  # Non-existent parent ID
        }

        # Send POST request to create the comment
        response = await async_client.post(
            "/api/v1/comments/",
            json=comment_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 404
        assert response.json() == {"detail": "Not able to create comment for non-existent parent comment"}

        # Ensure that moderation function was called
        mock_moderate_text.assert_called_once_with(comment_data["content"])
        # Verify that schedule auto reply wasn't called
        mock_schedule_auto_reply.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_comment_with_non_existent_post(
            self,
            mocker: MockerFixture,
            async_client: AsyncClient,
            tokens: AuthTokens,
    ):
        """
        Test the creation of a comment with a non-existent post ID.
        """
        # Mock text moderation and schedule_auto_reply
        mock_moderate_text = mocker.patch(
            'src.utils.content_moderator.implementation.ContentModerator.moderate_text',
            return_value=True
        )
        mock_schedule_auto_reply = mocker.patch(
            "src.services.comment.implementation.schedule_auto_reply",
            return_value=None
        )

        # Prepare data for creating a new comment with a non-existent post_id
        comment_data = {
            "content": "This is a test comment",
            "post_id": 99999,  # Non-existent post ID
            "parent_id": None  # No parent comment
        }

        # Send POST request to create the comment
        response = await async_client.post(
            "/api/v1/comments/",
            json=comment_data,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Verify response
        assert response.status_code == 404
        assert response.json() == {"detail": "Not able to create comment for non-existent post"}

        # Ensure that moderation function was called
        mock_moderate_text.assert_called_once_with(comment_data["content"])
        # Verify that schedule auto reply wasn't called
        mock_schedule_auto_reply.assert_not_called()
