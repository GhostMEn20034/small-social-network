class JWTHandlerConfig:
    """
    Configuration for the JWTHandler.

    This class holds configuration settings such as the secret key, 
    algorithm, expiration times for access and refresh tokens.
    """
    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 access_token_expire_minutes: int = 30, 
                 refresh_token_expire_minutes: int = 1440):  # Default: 1 day
        """
        Initializes the JWTHandlerConfig with the specified settings.

        :param secret_key: The secret key used to encode and decode the tokens.
        :param algorithm: The algorithm used for encoding the tokens (default is "HS256").
        :param access_token_expire_minutes: The default expiration time for access tokens in minutes (default is 30).
        :param refresh_token_expire_minutes: The default expiration time for refresh tokens in minutes (default is 1440).
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
