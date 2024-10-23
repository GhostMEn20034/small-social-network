from abc import ABC, abstractmethod

from src.models.user import User
from src.schemes.user import UserCreate, UserReadSchema, UserUpdateSchema, ChangePasswordSchema


class AbstractUserService(ABC):

    @abstractmethod
    async def user_signup(self, user_create_data: UserCreate) -> UserReadSchema:
        pass

    @abstractmethod
    async def update_user(self, user: User, user_update_data: UserUpdateSchema) -> UserReadSchema:
        pass

    @abstractmethod
    async def change_password(self, user: User, change_password_data: ChangePasswordSchema) -> None:
        pass
