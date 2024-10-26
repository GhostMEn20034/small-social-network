from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker
from src.core.settings import settings


engine = create_async_engine(settings.psql_connection_string, echo=True, future=True)

# Asynchronous function to create tables
async def create_database() -> None:
    async with engine.begin() as conn:
        # Create all tables based on SQLModel metadata
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
