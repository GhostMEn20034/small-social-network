from typing import List

import pytest
from httpx import AsyncClient

from src.models.post import Post
from src.models.user import User
from src.schemes.auth.token_data import AuthTokens


class TestGetPost:

    @pytest.mark.asyncio
    async def test_get_post_by_id(self, async_client: AsyncClient, posts_of_main_user: List[Post],
                                  tokens: AuthTokens):
        """Test retrieving a post by its ID."""
        post_to_get = posts_of_main_user[0]  # Get the first post

        response = await async_client.get(
            f"/api/v1/posts/{post_to_get.id}",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["id"] == post_to_get.id
        assert response.json()["title"] == post_to_get.title
        assert response.json()["content"] == post_to_get.content

    @pytest.mark.asyncio
    async def test_get_post_not_found(self, async_client: AsyncClient, tokens: AuthTokens):
        """Test retrieving a post that does not exist."""
        non_existing_post_id = 9999  # Assuming this post ID does not exist

        response = await async_client.get(
            f"/api/v1/posts/{non_existing_post_id}",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"


    @pytest.mark.asyncio
    async def test_get_posts_of_user(self, async_client: AsyncClient, tokens: AuthTokens,
                                     the_user: User, posts_of_main_user: List[Post]):
        """
        Test retrieving all posts of a user.
        All posts should have author_id equal to the_user.id
        """
        response = await async_client.get(
            f"/api/v1/posts/me",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 200
        posts = response.json()

        assert isinstance(posts, list)
        assert all(post["author_id"] == the_user.id for post in posts)  # Ensure all author_ids match

    @pytest.mark.asyncio
    async def test_get_posts_of_user_unauthenticated(self, async_client: AsyncClient):
        """
        Test retrieving all posts of a user without authentication.
        The response status must be 401.
        """
        response = await async_client.get("/api/v1/posts/me")  # No authorization header

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_get_all_posts(self, async_client: AsyncClient, tokens: AuthTokens):
        """
        Test retrieving all posts.
        The response status must be 200.
        """
        response = await async_client.get(
            "/api/v1/posts/",
            headers={"Authorization": f"Bearer {tokens.access_token}"}
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_all_posts_unauthenticated(self, async_client: AsyncClient):
        """
        Test retrieving all posts without authentication.
        The response status must be 200 OK.
        """
        response = await async_client.get("/api/v1/posts/")

        assert response.status_code == 200
        posts = response.json()

        assert isinstance(posts, list)  # Ensure the response is a list
