"""
GlobeTrotter agent – Phase 4.

Orchestrates:
  User message
    → Groq (gpt-oss-120b) with tool schemas
    → optional tool calls (search_destinations, …)
    → tool results fed back to the model
    → final natural-language answer

Tools are the same implementations used by the MCP server; they call
the existing GlobeTrotter HTTP APIs only.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.state import get_or_create_conversation
from app.agent.tools_schema import TOOL_IMPLEMENTATIONS, get_tool_schemas
from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.logger import get_logger, get_ai_logger

logger = get_logger(__name__)
ai_logger = get_ai_logger()

MAX_TOOL_ROUNDS = 5


@dataclass
class AgentResult:
    success: bool
    request_id: str
    conversation_id: str
    reply: str
    model: str
    total_latency_seconds: float
    tool_calls_made: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None


class GlobeTrotterAgent:
    """Agentic loop: LLM ↔ tools ↔ existing GlobeTrotter APIs."""

    def __init__(self):
        self.llm = get_llm_service()
        self.tool_schemas = get_tool_schemas()

    async def run(
        self,
        user_message: str,
        *,
        conversation_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> AgentResult:
        rid = request_id or f"req_{uuid.uuid4().hex[:8]}"
        cid = conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        started = time.perf_counter()

        logger.info(
            "AGENT_START request_id=%s conversation_id=%s message=%s",
            rid,
            cid,
            user_message[:120],
        )
        ai_logger.info(
            "AGENT_START request_id=%s conversation_id=%s",
            rid,
            cid,
        )

        state = get_or_create_conversation(cid)
        state.add_user(user_message)

        total_input_tokens = 0
        total_output_tokens = 0
        tool_calls_log: list[dict[str, Any]] = []

        try:
            for round_idx in range(MAX_TOOL_ROUNDS):
                logger.info(
                    "AGENT_ROUND request_id=%s round=%d messages=%d",
                    rid,
                    round_idx + 1,
                    len(state.messages),
                )

                llm_result = await self.llm.chat(
                    messages=state.messages,
                    system_prompt=SYSTEM_PROMPT,
                    tools=self.tool_schemas,
                    tool_choice="auto",
                    request_id=f"{rid}_r{round_idx + 1}",
                )

                total_input_tokens += llm_result.usage.input_tokens
                total_output_tokens += llm_result.usage.output_tokens

                # Inspect raw completion for tool_calls
                tool_calls = self._extract_tool_calls(llm_result.raw)

                if not tool_calls:
                    # Final text answer
                    reply = llm_result.content or ""
                    state.add_assistant(reply)
                    total_latency = time.perf_counter() - started

                    logger.info(
                        "AGENT_SUCCESS request_id=%s rounds=%d tools=%d latency=%.3fs",
                        rid,
                        round_idx + 1,
                        len(tool_calls_log),
                        total_latency,
                    )
                    ai_logger.info(
                        "AGENT_SUCCESS request_id=%s total_tokens=%d latency=%.3fs",
                        rid,
                        total_input_tokens + total_output_tokens,
                        total_latency,
                    )

                    return AgentResult(
                        success=True,
                        request_id=rid,
                        conversation_id=cid,
                        reply=reply,
                        model=llm_result.model,
                        total_latency_seconds=round(total_latency, 3),
                        tool_calls_made=tool_calls_log,
                        usage={
                            "input_tokens": total_input_tokens,
                            "output_tokens": total_output_tokens,
                            "total_tokens": total_input_tokens + total_output_tokens,
                        },
                    )

                # Model requested tool calls – execute them
                state.add_assistant(
                    llm_result.content or "",
                    tool_calls=[
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc["arguments_raw"],
                            },
                        }
                        for tc in tool_calls
                    ],
                )

                for tc in tool_calls:
                    tool_name = tc["name"]
                    arguments = tc["arguments"]
                    tool_call_id = tc["id"]

                    logger.info(
                        "AGENT_TOOL_CALL request_id=%s tool=%s args=%s",
                        rid,
                        tool_name,
                        arguments,
                    )
                    ai_logger.info(
                        "AGENT_TOOL_CALL request_id=%s tool=%s",
                        rid,
                        tool_name,
                    )

                    tool_result = await self._execute_tool(tool_name, arguments)
                    result_text = json.dumps(tool_result, default=str)

                    tool_calls_log.append(
                        {
                            "tool": tool_name,
                            "arguments": arguments,
                            "success": tool_result.get("success", False),
                        }
                    )

                    state.add_tool_result(tool_call_id, tool_name, result_text)

                    logger.info(
                        "AGENT_TOOL_RESULT request_id=%s tool=%s success=%s",
                        rid,
                        tool_name,
                        tool_result.get("success"),
                    )

            # Exceeded max rounds – return whatever we have
            total_latency = time.perf_counter() - started
            fallback = (
                "I reached the maximum number of tool steps while processing your request. "
                "Please try a more specific question."
            )
            logger.warning(
                "AGENT_MAX_ROUNDS request_id=%s latency=%.3fs",
                rid,
                total_latency,
            )
            return AgentResult(
                success=True,
                request_id=rid,
                conversation_id=cid,
                reply=fallback,
                model=self.llm.model,
                total_latency_seconds=round(total_latency, 3),
                tool_calls_made=tool_calls_log,
                usage={
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "total_tokens": total_input_tokens + total_output_tokens,
                },
            )

        except LLMServiceError as exc:
            total_latency = time.perf_counter() - started
            logger.error(
                "AGENT_FAILED request_id=%s error=%s latency=%.3fs",
                rid,
                str(exc),
                total_latency,
            )
            return AgentResult(
                success=False,
                request_id=rid,
                conversation_id=cid,
                reply="",
                model=self.llm.model,
                total_latency_seconds=round(total_latency, 3),
                tool_calls_made=tool_calls_log,
                error=str(exc),
            )
        except Exception as exc:  # noqa: BLE001
            total_latency = time.perf_counter() - started
            logger.exception(
                "AGENT_FAILED request_id=%s unexpected=%s",
                rid,
                str(exc),
            )
            return AgentResult(
                success=False,
                request_id=rid,
                conversation_id=cid,
                reply="",
                model=self.llm.model,
                total_latency_seconds=round(total_latency, 3),
                tool_calls_made=tool_calls_log,
                error=f"Unexpected agent error: {exc}",
            )

    def _extract_tool_calls(self, completion: Any) -> list[dict[str, Any]]:
        """Parse tool_calls from a Groq/OpenAI-style completion object."""
        if completion is None:
            return []
        try:
            choice = completion.choices[0]
            message = choice.message
            raw_calls = getattr(message, "tool_calls", None) or []
        except (IndexError, AttributeError):
            return []

        parsed: list[dict[str, Any]] = []
        for tc in raw_calls:
            try:
                name = tc.function.name
                args_raw = tc.function.arguments or "{}"
                try:
                    args = json.loads(args_raw)
                except json.JSONDecodeError:
                    args = {}
                parsed.append(
                    {
                        "id": tc.id,
                        "name": name,
                        "arguments": args,
                        "arguments_raw": args_raw,
                    }
                )
            except AttributeError:
                continue
        return parsed

    async def _execute_tool(self, name: str, arguments: dict) -> dict:
        impl = TOOL_IMPLEMENTATIONS.get(name)
        if impl is None:
            return {"success": False, "error": f"Unknown tool: {name}"}
        try:
            return await impl(**arguments)
        except TypeError as exc:
            # Bad / unexpected arguments from the model
            return {"success": False, "error": f"Invalid arguments for {name}: {exc}"}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": f"Tool {name} failed: {exc}"}


_agent: Optional[GlobeTrotterAgent] = None


def get_agent() -> GlobeTrotterAgent:
    global _agent
    if _agent is None:
        _agent = GlobeTrotterAgent()
    return _agent
