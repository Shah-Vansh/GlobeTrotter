"""
GlobeTrotter agent – Phases 4–6.

Multi-step agentic loop:
  User message
    → Groq + tool schemas
    → sequential tool calls (search → create_trip → add_stop → …)
    → compact tool results fed back
    → final natural-language answer
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.result_utils import compact_tool_result
from app.agent.state import get_or_create_conversation
from app.agent.tools_schema import TOOL_IMPLEMENTATIONS, get_tool_schemas
from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.auth_context import set_access_token
from app.utils.logger import get_logger, get_ai_logger

logger = get_logger(__name__)
ai_logger = get_ai_logger()

# Enough room for: search cities → details → activities → create trip → stops → itinerary
MAX_TOOL_ROUNDS = 10


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
    workflow_steps: list[str] = field(default_factory=list)


class GlobeTrotterAgent:
    def __init__(self):
        self.llm = get_llm_service()
        self.tool_schemas = get_tool_schemas()

    async def run(
        self,
        user_message: str,
        *,
        conversation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> AgentResult:
        rid = request_id or f"req_{uuid.uuid4().hex[:8]}"
        cid = conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        started = time.perf_counter()

        set_access_token(access_token)

        logger.info(
            "AGENT_START request_id=%s conversation_id=%s authenticated=%s message=%s",
            rid,
            cid,
            bool(access_token),
            user_message[:120],
        )
        ai_logger.info(
            "AGENT_START request_id=%s conversation_id=%s authenticated=%s",
            rid,
            cid,
            bool(access_token),
        )

        state = get_or_create_conversation(cid)
        state.add_user(user_message)

        total_input_tokens = 0
        total_output_tokens = 0
        tool_calls_log: list[dict[str, Any]] = []
        workflow_steps: list[str] = []

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

                tool_calls = self._extract_tool_calls(llm_result.raw)

                if not tool_calls:
                    reply = llm_result.content or ""
                    state.add_assistant(reply)
                    total_latency = time.perf_counter() - started

                    logger.info(
                        "AGENT_SUCCESS request_id=%s rounds=%d tools=%d steps=%s latency=%.3fs",
                        rid,
                        round_idx + 1,
                        len(tool_calls_log),
                        " → ".join(workflow_steps) if workflow_steps else "(none)",
                        total_latency,
                    )
                    ai_logger.info(
                        "AGENT_WORKFLOW request_id=%s path=%s",
                        rid,
                        " → ".join(workflow_steps) if workflow_steps else "(text-only)",
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
                        workflow_steps=workflow_steps,
                    )

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
                    # Compact payload so multi-step chains stay within context limits
                    result_text = compact_tool_result(tool_result)

                    success = bool(tool_result.get("success"))
                    tool_calls_log.append(
                        {
                            "tool": tool_name,
                            "arguments": arguments,
                            "success": success,
                        }
                    )
                    step_label = f"{tool_name}{'✓' if success else '✗'}"
                    workflow_steps.append(step_label)

                    state.add_tool_result(tool_call_id, tool_name, result_text)

                    logger.info(
                        "AGENT_TOOL_RESULT request_id=%s tool=%s success=%s",
                        rid,
                        tool_name,
                        success,
                    )

            total_latency = time.perf_counter() - started
            fallback = (
                "I made progress with several tool steps but hit the step limit. "
                "Here is what completed: "
                + (
                    " → ".join(workflow_steps)
                    if workflow_steps
                    else "(no tools succeeded)"
                )
                + ". Please ask a more focused follow-up so I can finish."
            )
            logger.warning(
                "AGENT_MAX_ROUNDS request_id=%s steps=%s latency=%.3fs",
                rid,
                workflow_steps,
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
                workflow_steps=workflow_steps,
            )

        except LLMServiceError as exc:
            total_latency = time.perf_counter() - started
            logger.error("AGENT_FAILED request_id=%s error=%s", rid, str(exc))
            return AgentResult(
                success=False,
                request_id=rid,
                conversation_id=cid,
                reply="",
                model=self.llm.model,
                total_latency_seconds=round(total_latency, 3),
                tool_calls_made=tool_calls_log,
                error=str(exc),
                workflow_steps=workflow_steps,
            )
        except Exception as exc:  # noqa: BLE001
            total_latency = time.perf_counter() - started
            logger.exception("AGENT_FAILED request_id=%s unexpected=%s", rid, str(exc))
            return AgentResult(
                success=False,
                request_id=rid,
                conversation_id=cid,
                reply="",
                model=self.llm.model,
                total_latency_seconds=round(total_latency, 3),
                tool_calls_made=tool_calls_log,
                error=f"Unexpected agent error: {exc}",
                workflow_steps=workflow_steps,
            )
        finally:
            set_access_token(None)

    def _extract_tool_calls(self, completion: Any) -> list[dict[str, Any]]:
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
            return {"success": False, "error": f"Invalid arguments for {name}: {exc}"}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": f"Tool {name} failed: {exc}"}


_agent: Optional[GlobeTrotterAgent] = None


def get_agent() -> GlobeTrotterAgent:
    global _agent
    if _agent is None:
        _agent = GlobeTrotterAgent()
    return _agent
