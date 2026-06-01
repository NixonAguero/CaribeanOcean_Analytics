from fastapi import FastAPI
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    APP_ENV: str = "development"
    APP_DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()



def create_app():
    app = FastAPI(title="Hotel Analytics API")
    app.version = "1.0.0"
    return app