"""
Centralized logging for the MCP chatbot.

- Logs to terminal (console)
- Logs to rotating files: app.log, error.log, ai.log
- Supports request_id correlation
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.config import get_settings

# Module-level flag so setup is idempotent
_configured = False


def setup_logging() -> None:
    """Configure root logger + specialized handlers. Call once at startup."""
    global _configured
    if _configured:
        return

    settings = get_settings()
    log_dir = settings.log_path
    log_dir.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Shared format with request_id placeholder
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(level)

    # Clear existing handlers (useful in reload scenarios)
    root.handlers.clear()

    # Console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(fmt)
    root.addHandler(console)

    # app.log – general events
    app_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setLevel(level)
    app_handler.setFormatter(fmt)
    root.addHandler(app_handler)

    # error.log – ERROR and above only
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)
    root.addHandler(error_handler)

    # ai.log – dedicated logger for LLM / MCP / token usage
    ai_logger = logging.getLogger("ai")
    ai_logger.setLevel(level)
    ai_logger.propagate = False  # keep it separate from root
    ai_handler = RotatingFileHandler(
        log_dir / "ai.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    ai_handler.setLevel(level)
    ai_handler.setFormatter(fmt)
    ai_logger.addHandler(ai_handler)
    # also echo AI logs to console for visibility during development
    ai_console = logging.StreamHandler(sys.stdout)
    ai_console.setLevel(level)
    ai_console.setFormatter(fmt)
    ai_logger.addHandler(ai_console)

    _configured = True
    logging.getLogger(__name__).info("Logging configured (level=%s, dir=%s)", settings.log_level, log_dir)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a named logger (after setup_logging has been called)."""
    return logging.getLogger(name or __name__)


def get_ai_logger() -> logging.Logger:
    """Dedicated logger for AI / MCP / token events."""
    return logging.getLogger("ai")
