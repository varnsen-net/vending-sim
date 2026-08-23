"""Configuration management using pydantic-settings."""
from pathlib import Path

from pydantic import Field, SecretStr, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJ_ROOT = Path(__file__).resolve().parents[1]


class LLMConfig(BaseModel):
    """Config for LLM."""
    api_key: SecretStr = Field(description="API key for LLM auth.")
    model: str = "ministral-14b-latest"
    temperature: float = 0.7
    sys_msg: str = """
    You are a sitcom writer. Given a script in progress, your task is to write the next line of dialogue.
    These are lines of dialogue for a sitcom, so they should generally be short and quippy.

    Don't simply parrot what other characters have said. Move the conversation forward.

    Do not prepend anything to your responses.
    Do not put your responses in quotes.
    Just respond with a line of dialogue.
    """


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
    llm: LLMConfig = Field(default_factory=LLMConfig)
    webhook_url: SecretStr = Field(description="Webhook URL for Discord.") 

