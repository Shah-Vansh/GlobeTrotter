"""
Phase 6 – multi-step agentic workflow smoke tests.

Prerequisites:
  - GROQ_API_KEY in .env
  - GlobeTrotter backend on GLOBETROTTER_API_URL
  - Optional: ACCESS_TOKEN env var (JWT from /api/auth/login) for trip workflows

Usage:
  python -m scripts.test_workflow
  ACCESS_TOKEN=eyJ... python -m scripts.test_workflow
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

from app.agent.agent import get_agent
from app.utils.logger import setup_logging


PUBLIC_PROMPTS = [
    "Search for destinations related to beach or Goa and summarise the top options.",
    "Find highly rated activities and list a few with their categories.",
]

AUTH_PROMPTS = [
    (
        "Using real tools only: search destinations for Goa, then create a trip named "
        "'Goa Escape' from 2026-12-01 to 2026-12-05, then list my trips."
    ),
]


async def run_one(prompt: str, access_token: str | None) -> None:
    print("\n" + "=" * 60)
    print(f"PROMPT: {prompt}")
    print("=" * 60)

    agent = get_agent()
    result = await agent.run(prompt, access_token=access_token)

    print(f"success         : {result.success}")
    print(f"request_id      : {result.request_id}")
    print(f"latency         : {result.total_latency_seconds}s")
    print(f"usage           : {result.usage}")
    print(f"workflow_steps  : {' → '.join(result.workflow_steps) or '(none)'}")
    print(f"tool_calls_made : {json.dumps(result.tool_calls_made, indent=2)}")
    if result.error:
        print(f"error           : {result.error}")
    print("\n--- Reply ---")
    print(result.reply)


async def main() -> None:
    setup_logging()
    token = os.environ.get("ACCESS_TOKEN") or None

    prompts = list(PUBLIC_PROMPTS)
    if token:
        prompts.extend(AUTH_PROMPTS)
        print("ACCESS_TOKEN detected – running authenticated workflow(s).")
    else:
        print("No ACCESS_TOKEN – skipping authenticated trip workflow.")
        print("Set ACCESS_TOKEN from POST /api/auth/login to test full chain.")

    for p in prompts:
        await run_one(p, token)


if __name__ == "__main__":
    # Allow a single custom prompt
    if len(sys.argv) > 1:
        custom = " ".join(sys.argv[1:])

        async def _custom():
            setup_logging()
            await run_one(custom, os.environ.get("ACCESS_TOKEN"))

        asyncio.run(_custom())
    else:
        asyncio.run(main())
