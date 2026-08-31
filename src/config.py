"""Configuration management using pydantic-settings."""
from pathlib import Path

from pydantic import Field, SecretStr, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.vending import Item


PROJ_ROOT = Path(__file__).resolve().parents[1]


class LLMConfig(BaseModel):
    """Config for LLM."""
    api_key: SecretStr = Field(description="API key for LLM auth.")
    model: str = "ministral-14b-latest"
    temperature: float = 0.7
    sys_msg: str = """
        You are a business owner who operates a vending machine.
    """


class SimulationConfig(BaseModel):
    """"""
    tick_interval: int = Field(
        default=5,
        description="Time interval (in seconds) between simulation ticks.",
    )


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
    webhook_url: SecretStr = Field(description="Webhook URL for Discord.") 
    llm: LLMConfig = Field(default_factory=LLMConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
