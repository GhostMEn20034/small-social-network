from datetime import date, timedelta
from typing import List
import pytest
from httpx import AsyncClient

from src.models.comment import Comment
from src.models.post import Post
from src.schemes.auth.token_data import AuthTokens


class TestGetComment:

    @pytest.mark.asyncio
    async def test_get_all_top_level_comments(self, async_client: AsyncClient, posts_of_main_user: List[Post]):
        """
        Test retrieving all top-level comments for a post.
        """
        response = await async_client.get(f"/api/v1/comments/?post_id={posts_of_main_user[0].id}")

        assert response.status_code == 200
        comments = response.json()

        assert isinstance(comments, list)

        # Ensure all comments are top-level (no parent_id)
        assert all('parent_id' not in comment or comment['parent_id'] is None for comment in comments)

        # Ensure all comments are not blocked
        assert all(comment.get('blocked') is False for comment in comments)

    @pytest.mark.asyncio
    async def test_get_specific_comment(self, async_client: AsyncClient, comments_of_another_user: List[Comment],
                                        comments_of_main_user: List[Comment]):
        """
        Test retrieving a specific comment and its replies.
        """
        response = await async_client.get(f"/api/v1/comments/{comments_of_main_user[0].id}")

        assert response.status_code == 200
        comment = response.json()

        assert "content" in comment['comment']
        assert isinstance(comment.get("replies", []), list)
        assert len(comment["replies"]) > 0

    @pytest.mark.asyncio
    async def test_get_non_existent_comment(self, async_client: AsyncClient):
        """
        Test retrieving a non-existent comment by ID.
        """
        non_existent_id = 999999  # An ID that should not exist
        response = await async_client.get(f"/api/v1/comments/{non_existent_id}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Not able to get comment details for non-existent comment"}


    @pytest.mark.asyncio
    async def test_get_daily_comment_breakdown(
            self,
            async_client: AsyncClient,
            tokens: AuthTokens,
            comments_of_main_user: List[Comment],
            comments_of_another_user: List[Comment],
    ):
        """
        Test the daily breakdown analytics endpoint for published and blocked comments.
        """
        # Define a date range covering the past week
        date_from = (date.today() - timedelta(days=7)).isoformat()
        date_to = date.today().isoformat()
        date_range = {"date_from": date_from, "date_to": date_to}

        # Send request to analytics endpoint
        response = await async_client.get(
            "/api/v1/comments/analytics/daily-breakdown",
            params=date_range,
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        # Validate the response
        assert response.status_code == 200

        daily_analytics = response.json()

        assert isinstance(daily_analytics, list)
        assert all(
            "date" in item and "total_comments" in item and "blocked_comments" in item for item in daily_analytics)

        for item in daily_analytics:
            item_date = date.fromisoformat(item["date"])
            assert date.fromisoformat(date_from) <= item_date <= date.fromisoformat(date_to)
