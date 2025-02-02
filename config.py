from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SRS App"
    jwt_secret_key: str
    model_config = SettingsConfigDict(env_file=".env")
