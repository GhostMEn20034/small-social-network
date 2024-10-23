import bcrypt


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.

    :param password: The plain-text password.
    :return: The hashed password.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plain-text password matches the hashed password.

    :param plain_password: The plain-text password.
    :param hashed_password: The hashed password.
    :return: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))