"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Groq
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    # Existing GlobeTrotter backend
    globetrotter_api_url: str = "http://localhost:5000"

    # MCP
    mcp_server_name: str = "globetrotter-mcp"

    # Chatbot server
    chatbot_host: str = "127.0.0.1"
    chatbot_port: int = 8001

    # Logging
    log_level: str = "INFO"
    log_dir: str = "logs"

    @property
    def log_path(self) -> Path:
        return Path(self.log_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
