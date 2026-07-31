from pathlib import Path
from typing import ClassVar

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.tickers import Ticker

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


class BaseConfig(BaseSettings):
    """Класс с базовыми настройками для конфигурации."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore"
    )


class WebServerConfig(BaseConfig):
    """Класс с конфигурацей для веб сервера."""

    server_host: str = Field(default=...)
    server_port: int = Field(default=...)


class DatabaseConfig(BaseConfig):
    """Класс с конфигурацией подключения к бд."""

    db_host: str = Field(default=...)
    db_port: int = Field(default=...)
    db_name: str = Field(default=...)
    db_user: str = Field(default=...)
    db_password: SecretStr = Field(default=...)

    @property
    def sqlalchemy_url(self) -> str:
        """Формирует ссылку для подключения к бд через sqlalchemy."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class PollingConfig(BaseConfig):
    """Класс с конфигурацией для сервиса, который будет опрашивать ссылки."""

    api_url: str = Field(default="https://www.deribit.com/api/v2/public/")
    external_api_timeout_seconds: float = Field(default=5.0)

    supported_tickers: set[Ticker] = Field(default={Ticker.BTC_USD, Ticker.ETH_USD})


class RedisConfig(BaseConfig):
    """Класс с конфигурацией для redis."""

    redis_host: str = Field(default=...)
    redis_port: int = Field(default=...)
    redis_password: SecretStr = Field(default=...)

    @property
    def broker_url(self) -> str:
        return f"redis://:{self.redis_password.get_secret_value()}@{self.redis_host}:{self.redis_port}/0"
