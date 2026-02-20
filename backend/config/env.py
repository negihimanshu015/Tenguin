from typing import List, Optional
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Security
    SECRET_KEY: str = Field(alias='DJANGO_SECRET_KEY')
    DEBUG: bool = Field(default=False, alias='DJANGO_DEBUG')
    ALLOWED_HOSTS: List[str] = Field(default_factory=list, alias='DJANGO_ALLOWED_HOSTS')

    # Database
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_TEST_DB: Optional[str] = None

    # Clerk
    CLERK_ISSUER: Optional[str] = None
    CLERK_AUDIENCE: Optional[str] = None

    # App
    PROJECT_NAME: str = "Tenguin"

env = AppSettings()
