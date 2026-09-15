"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
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

    # Production / resilience (Phase 10)
    # Max chat requests per client IP per window
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60
    # Backend HTTP timeout for GlobeTrotter API calls
    api_timeout_seconds: float = 30.0
    # LLM call timeout (seconds)
    llm_timeout_seconds: float = 60.0
    # Comma-separated origins for CORS (empty = use defaults)
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    )
    # If true, refuse to start without GROQ_API_KEY
    require_groq_key: bool = False

    @property
    def log_path(self) -> Path:
        return Path(self.log_dir)

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
