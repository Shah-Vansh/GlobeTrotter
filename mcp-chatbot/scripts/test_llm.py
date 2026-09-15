"""
Phase 3 smoke-test: call Groq (openai/gpt-oss-120b) directly and print usage.

Usage (from mcp-chatbot/ with venv activated and GROQ_API_KEY set):

    python -m scripts.test_llm
    python -m scripts.test_llm "Suggest a 3-day beach destination in India"
"""

from __future__ import annotations

import asyncio
import sys

from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.logger import setup_logging


async def main(prompt: str) -> None:
    setup_logging()
    llm = get_llm_service()

    print(f"Model : {llm.model}")
    print(f"Prompt: {prompt}\n")

    try:
        result = await llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=(
                "You are the GlobeTrotter travel assistant. "
                "Be concise and helpful. Do not invent features."
            ),
        )
    except LLMServiceError as exc:
        print(f"ERROR [{exc.request_id}]: {exc}")
        sys.exit(1)

    print("--- Reply ---")
    print(result.content)
    print()
    print("--- Metrics ---")
    print(f"request_id     : {result.request_id}")
    print(f"latency        : {result.latency_seconds:.3f}s")
    print(f"input_tokens   : {result.usage.input_tokens}")
    print(f"output_tokens  : {result.usage.output_tokens}")
    print(f"total_tokens   : {result.usage.total_tokens}")
    print(f"finish_reason  : {result.finish_reason}")


if __name__ == "__main__":
    user_prompt = (
        " ".join(sys.argv[1:]).strip()
        or "Hello! Briefly introduce yourself as the GlobeTrotter AI assistant."
    )
    asyncio.run(main(user_prompt))
