from fastapi import HTTPException, status

from .abstract import AbstractUserService
from src.schemes.user import UserCreate, UserReadSchema, UserUpdateSchema, ChangePasswordSchema
from src.repositories.unit_of_work.abstract import AbstractUnitOfWork
from src.utils.password_utils import hash_password, verify_password
from src.utils.user.user_model import create_user_from_signup_data, apply_updates_to_user
from src.models.user import User


class UserServiceImplementation(AbstractUserService):
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def user_signup(self, user_create_data: UserCreate) -> UserReadSchema:

        async with self._uow:
            user = await self._uow.user_repository.get_by_email(user_create_data.email)

            if user is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The user with this email already exists",
                )

            hashed_password = hash_password(user_create_data.password1)

            user_model = create_user_from_signup_data(user_create_data, hashed_password)

            created_user = await self._uow.user_repository.add(user_model)

            await self._uow.commit()

            return UserReadSchema(**created_user.model_dump())

    async def update_user(self, user: User, user_update_data: UserUpdateSchema) -> UserReadSchema:
        async with self._uow:
            user_with_the_same_email = await self._uow.user_repository.get_by_email(user_update_data.email)
            # If there's a user with the same email, and it's not the user itself
            if user_with_the_same_email is not None and user.email != user_update_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The user with this email already exists",
                )

        async with self._uow:
            apply_updates_to_user(user, user_update_data)

            updated_user = await self._uow.user_repository.update(user)

            await self._uow.commit()

            return UserReadSchema(**updated_user.model_dump())


    async def change_password(self, user: User, change_password_data: ChangePasswordSchema) -> None:
        """
        :param user: User object before update
        :param change_password_data: Object with old password and new password
        """
        old_hashed_password = user.password

        if not verify_password(change_password_data.old_password, old_hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wrong old password"
            )

        new_hashed_password = hash_password(change_password_data.new_password1)

        user.password = new_hashed_password

        async with self._uow:
            await self._uow.user_repository.update(user)
            await self._uow.commit()

