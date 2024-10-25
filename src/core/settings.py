from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    psql_connection_string: str
    secret_key: str # Secret key for JWT tokens
    sightengine_api_user: str # For Content moderation
    sightengine_api_secret: str # # For Content moderation
    gemini_api_key: str

settings = Settings()