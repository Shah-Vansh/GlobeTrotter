"""
Simple MCP client helper used for Phase 2 verification.

This client connects to the local GlobeTrotter MCP server (stdio)
and can list tools + call them. No LLM is involved.

Usage (from mcp-chatbot/ directory, with venv activated):

    python -m app.mcp.client

Or import and use programmatically.
"""

from __future__ import annotations

import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class GlobeTrotterMCPClient:
    """Minimal async MCP client that talks to our server over stdio."""

    def __init__(self):
        self._stack: Optional[AsyncExitStack] = None
        self.session: Optional[ClientSession] = None

    async def __aenter__(self) -> "GlobeTrotterMCPClient":
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()

        # Launch the MCP server as a subprocess via stdio
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "app.mcp.server"],
            env=None,  # inherits current environment (including .env via config)
        )

        stdio_transport = await self._stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport

        self.session = await self._stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self.session.initialize()
        logger.info("MCP client connected and initialized")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._stack:
            await self._stack.__aexit__(exc_type, exc, tb)
        self.session = None

    async def list_tools(self) -> list[Any]:
        assert self.session is not None
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name: str, arguments: dict | None = None) -> Any:
        assert self.session is not None
        logger.info("Calling MCP tool name=%s arguments=%s", name, arguments)
        result = await self.session.call_tool(name, arguments or {})
        return result


async def _demo() -> None:
    """Quick smoke-test of the MCP server without any LLM."""
    print("=== GlobeTrotter MCP Client Demo (Phase 2) ===\n")

    async with GlobeTrotterMCPClient() as client:
        tools = await client.list_tools()
        print(f"Available tools ({len(tools)}):")
        for t in tools:
            print(f"  - {t.name}: {t.description[:80] if t.description else ''}...")

        print("\n--- Calling search_destinations_tool (search='Goa') ---")
        result = await client.call_tool(
            "search_destinations_tool",
            {"search": "Goa"},
        )
        # result.content is a list of content blocks
        for block in result.content:
            if hasattr(block, "text"):
                try:
                    parsed = json.loads(block.text)
                    print(json.dumps(parsed, indent=2)[:1500])
                except Exception:
                    print(block.text[:1500])

        print("\n--- Calling search_activities_tool (limit via backend defaults) ---")
        result2 = await client.call_tool(
            "search_activities_tool",
            {"min_rating": 4.0},
        )
        for block in result2.content:
            if hasattr(block, "text"):
                try:
                    parsed = json.loads(block.text)
                    print(json.dumps(parsed, indent=2)[:1500])
                except Exception:
                    print(block.text[:1500])

    print("\n=== Demo finished ===")


if __name__ == "__main__":
    asyncio.run(_demo())
