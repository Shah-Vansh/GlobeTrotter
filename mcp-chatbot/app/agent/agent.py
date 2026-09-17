"""
GlobeTrotter agent – multi-step tool loop with conversation memory
and navigation hints for the existing React routes.
"""

from __future__ import annotations

import inspect
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from app.agent.navigation import extract_navigation
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.result_utils import compact_tool_result
from app.agent.state import get_or_create_conversation, save_conversation
from app.agent.tools_schema import TOOL_IMPLEMENTATIONS, get_tool_schemas
from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.auth_context import set_access_token
from app.utils.logger import get_logger, get_ai_logger

logger = get_logger(__name__)
ai_logger = get_ai_logger()

MAX_TOOL_ROUNDS = 10

# Light heuristics to remember personal facts across turns
_NAME_PATTERNS = [
    re.compile(
        r"\b(?:my name is|i am|i'm|this is|call me)\s+([A-Z][a-zA-Z'\\-]{1,30})\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:name['’]?s)\s+([A-Z][a-zA-Z'\\-]{1,30})\b", re.IGNORECASE),
]


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
    message_count: int = 0
    navigation: Optional[dict[str, Any]] = None


def _extract_user_facts(message: str, metadata: dict[str, Any]) -> None:
    """Update metadata with durable facts (e.g. name) from the user message."""
    if not message or not isinstance(metadata, dict):
        return
    for pat in _NAME_PATTERNS:
        m = pat.search(message.strip())
        if m:
            name = m.group(1).strip()
            # Skip common false positives
            if name.lower() in {"the", "a", "an", "looking", "planning", "here", "there"}:
                continue
            metadata["user_name"] = name
            logger.info("MEMORY_FACT user_name=%s", name)
            break


def _build_system_prompt(metadata: dict[str, Any], authenticated: bool) -> str:
    """System prompt + auth status + session memory (name, trip ids)."""
    if authenticated:
        auth_block = (
            "\n\n## Current session\n"
            "- User is AUTHENTICATED (valid JWT is attached to every tool call).\n"
            "- Call list_trips / create_trip / add_stop_to_trip and other trip tools directly.\n"
            "- Do NOT ask the user to log in.\n"
        )
    else:
        auth_block = (
            "\n\n## Current session\n"
            "- User is NOT authenticated (no JWT).\n"
            "- Public tools (search destinations/activities) work.\n"
            "- For trip create/list/update, tell them to log in first; do not invent trips.\n"
        )

    extra_parts: list[str] = []
    if metadata.get("user_name"):
        extra_parts.append(
            f"user_name={metadata['user_name']} (address them by name when natural)"
        )
    if metadata.get("last_trip_id") is not None:
        extra_parts.append(f"last_trip_id={metadata['last_trip_id']}")
    if metadata.get("last_stop_id") is not None:
        extra_parts.append(f"last_stop_id={metadata['last_stop_id']}")
    recent = metadata.get("recent_tools") or []
    if recent:
        extra_parts.append("recent_tools=" + ",".join(recent[-8:]))

    memory_block = ""
    if extra_parts:
        memory_block = (
            "\n\n## Session memory (persists for this conversation until cleared)\n"
            "Remember and use these facts; do not ask for them again if already known:\n"
            "- "
            + "\n- ".join(extra_parts)
            + "\n"
        )

    return SYSTEM_PROMPT + auth_block + memory_block


def _sanitize_tool_args(arguments: Any) -> dict:
    if not isinstance(arguments, dict):
        return {}
    return {k: v for k, v in arguments.items() if v is not None}


class GlobeTrotterAgent:
    def __init__(self):
        self.llm = get_llm_service()

    @property
    def tool_schemas(self) -> list[dict[str, Any]]:
        return get_tool_schemas()

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
        authenticated = bool(access_token and str(access_token).strip())

        set_access_token(access_token if authenticated else None)

        logger.info(
            "AGENT_START request_id=%s conversation_id=%s authenticated=%s message=%s",
            rid,
            cid,
            authenticated,
            user_message[:120],
        )
        ai_logger.info(
            "AGENT_START request_id=%s conversation_id=%s authenticated=%s",
            rid,
            cid,
            authenticated,
        )

        state = get_or_create_conversation(cid)
        prior_count = len(state.messages)
        state.add_user(user_message)
        _extract_user_facts(user_message, state.metadata)

        logger.info(
            "MEMORY request_id=%s conversation_id=%s prior_messages=%d metadata=%s",
            rid,
            cid,
            prior_count,
            state.metadata,
        )

        total_input_tokens = 0
        total_output_tokens = 0
        tool_calls_log: list[dict[str, Any]] = []
        workflow_steps: list[str] = []
        navigation: Optional[dict[str, Any]] = None
        system_prompt = _build_system_prompt(state.metadata, authenticated)

        try:
            for round_idx in range(MAX_TOOL_ROUNDS):
                set_access_token(access_token if authenticated else None)

                logger.info(
                    "AGENT_ROUND request_id=%s round=%d messages=%d auth=%s",
                    rid,
                    round_idx + 1,
                    len(state.messages),
                    authenticated,
                )

                llm_result = await self.llm.chat(
                    messages=state.messages,
                    system_prompt=system_prompt,
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
                    save_conversation(cid)
                    total_latency = time.perf_counter() - started

                    logger.info(
                        "AGENT_SUCCESS request_id=%s rounds=%d tools=%d steps=%s nav=%s latency=%.3fs",
                        rid,
                        round_idx + 1,
                        len(tool_calls_log),
                        " → ".join(workflow_steps) if workflow_steps else "(none)",
                        navigation.get("path") if navigation else None,
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
                        workflow_steps=workflow_steps,
                        message_count=len(state.messages),
                        navigation=navigation,
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
                    arguments = _sanitize_tool_args(tc["arguments"])
                    tool_call_id = tc["id"]

                    set_access_token(access_token if authenticated else None)

                    logger.info(
                        "AGENT_TOOL_CALL request_id=%s tool=%s args=%s auth=%s",
                        rid,
                        tool_name,
                        arguments,
                        authenticated,
                    )

                    tool_result = await self._execute_tool(tool_name, arguments)
                    result_text = compact_tool_result(tool_result)

                    success = bool(tool_result.get("success"))
                    tool_calls_log.append(
                        {
                            "tool": tool_name,
                            "arguments": arguments,
                            "success": success,
                        }
                    )
                    workflow_steps.append(f"{tool_name}{'✓' if success else '✗'}")
                    state.add_tool_result(tool_call_id, tool_name, result_text)

                    nav = extract_navigation(tool_name, arguments, tool_result)
                    if nav:
                        navigation = nav
                        logger.info(
                            "NAVIGATION request_id=%s path=%s tool=%s",
                            rid,
                            nav.get("path"),
                            tool_name,
                        )

                    logger.info(
                        "AGENT_TOOL_RESULT request_id=%s tool=%s success=%s",
                        rid,
                        tool_name,
                        success,
                    )

                system_prompt = _build_system_prompt(state.metadata, authenticated)

            save_conversation(cid)
            total_latency = time.perf_counter() - started
            fallback = (
                "I made progress with several tool steps but hit the step limit. "
                "Here is what completed: "
                + (" → ".join(workflow_steps) if workflow_steps else "(no tools succeeded)")
                + ". Please ask a more focused follow-up so I can finish."
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
                message_count=len(state.messages),
                navigation=navigation,
            )

        except LLMServiceError as exc:
            save_conversation(cid)
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
                message_count=len(state.messages),
                navigation=navigation,
            )
        except Exception as exc:  # noqa: BLE001
            save_conversation(cid)
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
                message_count=len(state.messages),
                navigation=navigation,
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
                if not isinstance(args, dict):
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
            sig = inspect.signature(impl)
            allowed = {
                k: v
                for k, v in arguments.items()
                if k in sig.parameters and v is not None
            }
            return await impl(**allowed)
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
