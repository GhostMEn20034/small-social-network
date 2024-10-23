from src.models.user import User
from src.schemes.user import UserCreate, UserUpdateSchema


def create_user_from_signup_data(user_data: UserCreate, hashed_password: str) -> User:
    """
    :param user_data: User's signup data
    :param hashed_password: The user's hashed password.
    :return: User model
    """
    return User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        date_of_birth=user_data.date_of_birth,
        password=hashed_password,
    )

def apply_updates_to_user(user: User, new_user_data: UserUpdateSchema) -> User:
    """
    :param user: User Object before update
    :param new_user_data: New user's data which will be applied to the user
    :return:
    """
    user.email = new_user_data.email
    user.first_name = new_user_data.first_name
    user.last_name = new_user_data.last_name
    user.date_of_birth = new_user_data.date_of_birth

    return user
