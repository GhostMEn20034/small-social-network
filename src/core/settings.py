from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    psql_connection_string: str
    secret_key: str

settings = Settings()