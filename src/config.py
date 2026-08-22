"""Configuration management using pydantic-settings."""
from pathlib import Path

from pydantic import Field, field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJ_ROOT = Path(__file__).resolve().parents[1]


class AppSettings(BaseSettings):
    """Base config — values shared across all environments.

    pydantic-settings automatically reads from:
      1. Environment variables (highest priority)
      2. The .env file specified in model_config
      3. Field defaults (lowest priority)

    Field names map to env vars by uppercasing: `irc_host` -> IRC_HOST
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    project_root: Path = PROJ_ROOT

    llm_api_key: SecretStr = Field(description="API key for LLM auth.")
    llm_model: str = "gemini-3.5-flash-lite"
