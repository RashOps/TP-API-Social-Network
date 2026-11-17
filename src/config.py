from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError
from pathlib import Path
import os
# from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    Chargement des variables depuis le fichier .env avec validation.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database - MongoDB
    mongo_uri: str = Field(
        default="mongodb://localhost:27017/",
        description="MongoDB connection URI",
        min_length=10
    )
    mongo_db_name: str = Field(
        default="social_network_event",
        description="Main database name",
        min_length=1,
        max_length=64
    )
    jwt_secret_key: str = Field(
        default="development-secret-change-me-123456",
        description="Secret used to sign JWT tokens",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)

    # API Settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )

# Instantiation de la classe
try:
    settings = Settings()
except ValidationError as e:
    print(f"Configuration validation error: {e}")
    raise