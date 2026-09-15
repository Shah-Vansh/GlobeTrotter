"""
Phase 4 smoke-test: full agent (LLM + tools → GlobeTrotter APIs).

Prerequisites:
  - GROQ_API_KEY set in .env
  - GlobeTrotter Flask backend running (default http://localhost:5000)

Usage:
  python -m scripts.test_agent
  python -m scripts.test_agent "Find beach destinations in India"
  python -m scripts.test_agent "Show activities with rating above 4"
"""

from __future__ import annotations

import asyncio
import json
import sys

from app.agent.agent import get_agent
from app.utils.logger import setup_logging


async def main(prompt: str) -> None:
    setup_logging()
    agent = get_agent()

    print(f"Prompt: {prompt}\n")
    result = await agent.run(prompt)

    print("=== Agent Result ===")
    print(f"success          : {result.success}")
    print(f"request_id       : {result.request_id}")
    print(f"conversation_id  : {result.conversation_id}")
    print(f"model            : {result.model}")
    print(f"latency_seconds  : {result.total_latency_seconds}")
    print(f"usage            : {result.usage}")
    print(f"tool_calls_made  : {json.dumps(result.tool_calls_made, indent=2)}")
    if result.error:
        print(f"error            : {result.error}")
    print()
    print("--- Reply ---")
    print(result.reply)


if __name__ == "__main__":
    user_prompt = (
        " ".join(sys.argv[1:]).strip()
        or "Search for destinations related to Goa and list a few activities."
    )
    asyncio.run(main(user_prompt))
