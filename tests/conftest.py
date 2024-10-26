import asyncio
from datetime import datetime, timedelta, UTC
from typing import AsyncGenerator, List
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.pool import NullPool
from dependency_injector import providers

from src.core.app_factory import create_app
from src.core.settings import settings
from src.models.comment import Comment
from src.models.post import Post
from src.models.user import User
from src.schemes.auth.token_data import AuthTokens
from src.utils.password_utils import hash_password

engine = create_async_engine(settings.psql_connection_string, echo=True, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@pytest.fixture(scope="session")
async def async_db_engine():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture(scope="session")
async def db_session(async_db_engine):
    """Fixture to create a database session."""
    async_session = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        yield session


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    app.container.db_session.override(providers.Resource(override_get_async_session))

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# let test session to know it is running inside event loop
@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def the_user(db_session) -> User:
    user = User(email='hello@email.com', password=hash_password('some_pwd'), first_name='John', last_name='Doe')
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    print("User", user)
    return user

@pytest.fixture(scope="session")
async def another_user(db_session) -> User:
    user = User(email='anotheruser@email.com', password=hash_password('some_pwd'), first_name='John', last_name='Doe')
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    print("Another user", user)
    return user

@pytest.fixture(scope="session")
async def tokens(async_client: AsyncClient, the_user: User):
    """Retrieves tokens for the main user"""
    # Simulate login to get tokens
    login_data = {
        "username": the_user.email,
        "password": "some_pwd",
    }
    login_response = await async_client.post("/api/v1/auth/token", data=login_data)
    return AuthTokens(**login_response.json())

@pytest.fixture(scope="session")
async def posts_of_main_user(the_user: User, db_session: AsyncSession):
    # Define the data for the posts
    post_data = [
        {
            "title": "First Post",
            "content": "Content of the first post",
            "draft": False,
            "auto_reply": True,
            "reply_after": 10,
        },
        {
            "title": "Second Post",
            "content": "Content of the second post",
            "draft": True,
            "auto_reply": False,
        },
        {
            "title": "Third Post",
            "content": "Content of the third post",
            "draft": False,
            "auto_reply": True,
            "reply_after": 5,
        },
        {
            "title": "Fourth Post",
            "content": "Content of the Fourth post",
            "draft": False,
            "auto_reply": False,
        },
    ]

    posts = []
    for data in post_data:
        post = Post(
            title=data["title"],
            content=data["content"],
            draft=data["draft"],
            auto_reply=data["auto_reply"],
            reply_after=data.get("reply_after"),
            created_at=datetime.now(UTC) - timedelta(days=1),  # For example, setting creation to a day ago
            author_id=the_user.id  # Link to the main user
        )

        db_session.add(post)
        posts.append(post)

    # Commit the changes to save the posts in the database
    await db_session.commit()
    return posts


@pytest.fixture(scope="session")
async def posts_of_another_user(another_user: User, db_session: AsyncSession):
    # Define the data for the posts of another user
    post_data = [
        {
            "title": "Another User's First Post",
            "content": "Content of the first post by another user",
            "draft": False,
            "auto_reply": False,
        },
        {
            "title": "Another User's Second Post",
            "content": "Content of the second post by another user",
            "draft": True,
            "auto_reply": True,
            "reply_after": 15,
        },
        {
            "title": "Another User's Third Post",
            "content": "Content of the third post by another user",
            "draft": False,
            "auto_reply": True,
            "reply_after": 20,
        },
    ]

    posts = []
    for data in post_data:
        post = Post(
            title=data["title"],
            content=data["content"],
            draft=data["draft"],
            auto_reply=data["auto_reply"],
            reply_after=data.get("reply_after"),
            created_at=datetime.now(UTC) - timedelta(days=2),
            author_id=another_user.id  # Link to another user
        )
        db_session.add(post)
        posts.append(post)

    # Commit the changes to save the posts in the database
    await db_session.commit()
    return posts

@pytest.fixture(scope="session")
async def comments_of_main_user(the_user: User, posts_of_main_user: List[Post], db_session: AsyncSession):
    # Define comments for main user's posts
    comment_data = [
        {
            "content": "First comment on First Post",
            "post_id": posts_of_main_user[0].id,
        },
        {
            "content": "Second comment on First Post",
            "post_id": posts_of_main_user[0].id,
        },
        {
            "content": "First comment on Third Post",
            "post_id": posts_of_main_user[2].id,
            "blocked": True,
        },
        {
            "content": "Comment to delete",
            "post_id": posts_of_main_user[0].id,
        }
    ]

    comments = []
    for data in comment_data:
        comment = Comment(
            content=data["content"],
            post_id=data["post_id"],
            created_at=datetime.now() - timedelta(days=2),  # Setting creation time
            owner_id=the_user.id,  # Main user's comment
            blocked=data.get("blocked", False)
        )
        db_session.add(comment)
        comments.append(comment)

    # Commit to save the comments in the database
    await db_session.commit()
    return comments


@pytest.fixture(scope="session")
async def comments_of_another_user(another_user: User, posts_of_another_user: List[Post],
                                   comments_of_main_user: List[Comment], db_session: AsyncSession):
    # Define comments for another user's posts with some replies to main user's comments
    comment_data = [
        {
            "content": "Reply to main user's comment on First Post",
            "post_id": comments_of_main_user[0].post_id,
            "parent_id": comments_of_main_user[0].id,
        },
        {
            "content": "Another user's comment on their own First Post",
            "post_id": posts_of_another_user[0].id,
        },
        {
            "content": "Reply to main user's second comment on First Post",
            "post_id": comments_of_main_user[1].post_id,
            "parent_id": comments_of_main_user[1].id,
        },
        {
            "content": "Another user's comment on their own Second Post",
            "post_id": posts_of_another_user[1].id,
        },
        {
            "content": "Comment need to be blocked",
            "post_id": comments_of_main_user[0].post_id,
        }
    ]

    comments = []
    for data in comment_data:
        comment = Comment(
            content=data["content"],
            post_id=data["post_id"],
            parent_id=data.get("parent_id"),
            created_at=datetime.now() - timedelta(hours=1),  # More recent timestamp for replies
            owner_id=another_user.id  # Another user's comment
        )
        db_session.add(comment)
        comments.append(comment)

    # Commit to save the comments in the database
    await db_session.commit()
    return comments

