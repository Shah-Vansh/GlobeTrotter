"""
Request-scoped JWT access token for authenticated MCP tools.

The chatbot never bypasses GlobeTrotter auth: every protected tool must
forward the same Bearer token the frontend would send.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

_access_token: ContextVar[Optional[str]] = ContextVar("access_token", default=None)


def set_access_token(token: Optional[str]) -> None:
    _access_token.set(token)


def get_access_token() -> Optional[str]:
    return _access_token.get()


def require_access_token() -> str:
    token = get_access_token()
    if not token:
        raise PermissionError(
            "This action requires authentication. "
            "Please log in and provide a valid access token."
        )
    return token
