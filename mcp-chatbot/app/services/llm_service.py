"""
Groq LLM service for GlobeTrotter MCP Chatbot (Phase 3+).

Uses the Groq API with model openai/gpt-oss-120b.
Every request records:
  - request_id
  - model / provider
  - latency
  - input / output / total tokens
  - success or error
into both the terminal and the dedicated ai.log file.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from groq import AsyncGroq, APIError, APIConnectionError, RateLimitError

from app.config import get_settings
from app.utils.logger import get_logger, get_ai_logger

logger = get_logger(__name__)
ai_logger = get_ai_logger()


@dataclass
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResponse:
    content: str
    model: str
    request_id: str
    latency_seconds: float
    usage: LLMUsage = field(default_factory=LLMUsage)
    raw: Optional[Any] = None
    finish_reason: Optional[str] = None


class LLMServiceError(Exception):
    """Raised when the LLM provider returns an error."""

    def __init__(self, message: str, *, request_id: str, status_code: Optional[int] = None):
        self.request_id = request_id
        self.status_code = status_code
        super().__init__(message)


class LLMService:
    """Thin async wrapper around the Groq chat completions API."""

    def __init__(self):
        settings = get_settings()
        if not settings.groq_api_key:
            logger.warning(
                "GROQ_API_KEY is empty – LLM calls will fail until it is set in .env"
            )
        self.client = AsyncGroq(api_key=settings.groq_api_key or "missing")
        self.model = settings.groq_model
        self.provider = "groq"

    def _new_request_id(self) -> str:
        return f"req_{uuid.uuid4().hex[:8]}"

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.3,
        max_tokens: Optional[int] = 2048,
        tools: Optional[list[dict]] = None,
        tool_choice: Optional[str | dict] = None,
        request_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Send a chat completion request to Groq.

        messages may include tool / assistant tool_call roles (Phase 4).
        """
        rid = request_id or self._new_request_id()
        start = time.perf_counter()

        final_messages: list[dict[str, Any]] = list(messages)
        if system_prompt:
            final_messages = [{"role": "system", "content": system_prompt}] + final_messages

        logger.info(
            "LLM_REQUEST request_id=%s provider=%s model=%s messages=%d tools=%s",
            rid,
            self.provider,
            self.model,
            len(final_messages),
            bool(tools),
        )
        ai_logger.info(
            "LLM_REQUEST request_id=%s provider=%s model=%s tools=%s",
            rid,
            self.provider,
            self.model,
            bool(tools),
        )

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": final_messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        try:
            completion = await self.client.chat.completions.create(**kwargs)
        except RateLimitError as exc:
            latency = time.perf_counter() - start
            self._log_error(rid, "RateLimitError", str(exc), latency)
            raise LLMServiceError(
                f"Groq rate limit: {exc}", request_id=rid, status_code=429
            ) from exc
        except APIConnectionError as exc:
            latency = time.perf_counter() - start
            self._log_error(rid, "APIConnectionError", str(exc), latency)
            raise LLMServiceError(
                f"Groq connection error: {exc}", request_id=rid, status_code=0
            ) from exc
        except APIError as exc:
            latency = time.perf_counter() - start
            status = getattr(exc, "status_code", None)
            self._log_error(rid, "APIError", str(exc), latency, status_code=status)
            raise LLMServiceError(
                f"Groq API error: {exc}", request_id=rid, status_code=status
            ) from exc
        except Exception as exc:  # noqa: BLE001
            latency = time.perf_counter() - start
            self._log_error(rid, type(exc).__name__, str(exc), latency)
            raise LLMServiceError(
                f"Unexpected LLM error: {exc}", request_id=rid
            ) from exc

        latency = time.perf_counter() - start

        choice = completion.choices[0] if completion.choices else None
        content = (choice.message.content or "") if choice else ""
        finish_reason = choice.finish_reason if choice else None

        usage = LLMUsage()
        if completion.usage:
            usage.input_tokens = completion.usage.prompt_tokens or 0
            usage.output_tokens = completion.usage.completion_tokens or 0
            usage.total_tokens = completion.usage.total_tokens or (
                usage.input_tokens + usage.output_tokens
            )

        has_tools = bool(
            choice
            and getattr(choice.message, "tool_calls", None)
        )

        logger.info(
            "LLM_RESPONSE request_id=%s latency=%.3fs "
            "input_tokens=%d output_tokens=%d total_tokens=%d "
            "finish_reason=%s tool_calls=%s",
            rid,
            latency,
            usage.input_tokens,
            usage.output_tokens,
            usage.total_tokens,
            finish_reason,
            has_tools,
        )
        ai_logger.info(
            "LLM_USAGE request_id=%s provider=%s model=%s "
            "input_tokens=%d output_tokens=%d total_tokens=%d latency=%.3fs tool_calls=%s",
            rid,
            self.provider,
            self.model,
            usage.input_tokens,
            usage.output_tokens,
            usage.total_tokens,
            latency,
            has_tools,
        )

        return LLMResponse(
            content=content,
            model=self.model,
            request_id=rid,
            latency_seconds=latency,
            usage=usage,
            raw=completion,
            finish_reason=finish_reason,
        )

    def _log_error(
        self,
        request_id: str,
        error_type: str,
        message: str,
        latency: float,
        status_code: Optional[int] = None,
    ) -> None:
        logger.error(
            "LLM_ERROR request_id=%s type=%s status=%s latency=%.3fs error=%s",
            request_id,
            error_type,
            status_code,
            latency,
            message,
        )
        ai_logger.error(
            "LLM_ERROR request_id=%s type=%s status=%s latency=%.3fs error=%s",
            request_id,
            error_type,
            status_code,
            latency,
            message,
        )


_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
