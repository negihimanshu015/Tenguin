from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def _parse_list(cls, value):
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    @property
    def validated_allowed_hosts(self) -> List[str]:
        return self._parse_list(self.ALLOWED_HOSTS)

    @property
    def validated_cors_origins(self) -> List[str]:
        return self._parse_list(self.CORS_ALLOWED_ORIGINS)

    # Security
    SECRET_KEY: str = Field(alias="DJANGO_SECRET_KEY")
    DEBUG: bool = Field(default=False, alias="DJANGO_DEBUG")
    ALLOWED_HOSTS: str = Field(default="", alias="DJANGO_ALLOWED_HOSTS")

    # CORS
    CORS_ALLOWED_ORIGINS: str = Field(default="", alias="CORS_ALLOWED_ORIGINS")
    CORS_ALLOW_ALL_ORIGINS: bool = Field(default=False, alias="CORS_ALLOW_ALL_ORIGINS")

    # Database (optional when using DATABASE_URL)
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_TEST_DB: Optional[str] = None

    DATABASE_URL: Optional[str] = Field(default=None, alias="DATABASE_URL")

    # Clerk
    CLERK_ISSUER: Optional[str] = None
    CLERK_AUDIENCE: Optional[str] = None

    # App
    PROJECT_NAME: str = "Tenguin"


env = AppSettings()