# GlobeTrotter MCP AI Chatbot

Natural-language interface over the existing GlobeTrotter application using **MCP + Groq (`openai/gpt-oss-120b`) + FastAPI**.

> **Core rule**: The chatbot can only do what the existing GlobeTrotter frontend + backend already support. MCP tools are thin wrappers around existing APIs. No invented functionality.

## Architecture Summary

```
User → Chat UI → FastAPI /api/chat → Agent (Groq / gpt-oss-120b)
                                          ↓ tool schemas
                                   Tool implementations
                                          ↓
                              Existing GlobeTrotter APIs
                                          ↓
                                   Existing Backend + DB
```

(Same tool functions also power the standalone MCP server in `app/mcp/server.py`.)

## Development Branch

All work happens exclusively on the **`dev`** branch.

## Project Structure

```
mcp-chatbot/
├── app/
│   ├── api/chat.py              # POST /api/chat (agent) + /api/chat/test
│   ├── agent/
│   │   ├── agent.py             # Agentic tool-calling loop (Phase 4)
│   │   ├── tools_schema.py      # OpenAI/Groq tool definitions
│   │   ├── prompts.py
│   │   └── state.py             # In-memory conversation state
│   ├── mcp/server.py + client.py
│   ├── tools/destinations.py + activities.py
│   ├── services/globetrotter_service.py + llm_service.py
│   └── utils/logger.py
├── scripts/test_llm.py + test_agent.py
├── docs/CAPABILITY_MATRIX.md
└── ...
```

## Implemented tools

| Tool name                 | Backend API                | Status |
|---------------------------|----------------------------|--------|
| `search_destinations`     | `GET /api/cities`          | ✅     |
| `get_destination_details` | `GET /api/cities/{id}`     | ✅     |
| `search_activities`       | `GET /api/activities`      | ✅     |
| `get_activity_details`    | `GET /api/activities/{id}` | ✅     |

## Environment

```bash
cp .env.example .env
# GROQ_API_KEY=...
# GROQ_MODEL=openai/gpt-oss-120b
# GLOBETROTTER_API_URL=http://localhost:5000
```

## Phases

- [x] Phase 0 – Audit
- [x] Phase 1 – Foundation + Logging
- [x] Phase 2 – MCP Server + real tools
- [x] Phase 3 – Groq integration
- [x] **Phase 4 – LLM + tool calling**
- [ ] Phase 5 – Full API → MCP tools (trips, itinerary, auth…)
- [ ] Phase 6 – Richer multi-tool workflows
- [ ] Phase 7 – Durable memory
- [ ] Phase 8 – Observability polish
- [ ] Phase 9 – Frontend Chat UI
- [ ] Phase 10 – Testing & production readiness

## How to run Phase 4

### Prerequisites

1. GlobeTrotter Flask backend on `:5000` (seeded data recommended)
2. `GROQ_API_KEY` in `.env`

### Install & start API

```bash
cd mcp-chatbot
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### CLI agent test

```bash
python -m scripts.test_agent
python -m scripts.test_agent "Find beach destinations related to Goa"
python -m scripts.test_agent "Show highly rated activities"
```

### HTTP agent test

```bash
curl -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search for destinations in India and suggest a few activities"}'
```

Example response fields:

```json
{
  "success": true,
  "request_id": "req_…",
  "conversation_id": "conv_…",
  "reply": "…natural language summary…",
  "model": "openai/gpt-oss-120b",
  "latency_seconds": 2.14,
  "usage": { "input_tokens": …, "output_tokens": …, "total_tokens": … },
  "tool_calls_made": [
    { "tool": "search_destinations", "arguments": {"search": "India"}, "success": true }
  ]
}
```

Pass the same `conversation_id` on follow-up messages to keep context.

### LLM-only test (no tools)

```bash
curl -X POST http://127.0.0.1:8001/api/chat/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Logging

Agent loop emits:

```
AGENT_START / AGENT_ROUND / AGENT_TOOL_CALL / AGENT_TOOL_RESULT / AGENT_SUCCESS
LLM_REQUEST / LLM_RESPONSE / LLM_USAGE
MCP-style tool + API logs from the tool layer
```

All correlated by `request_id` in terminal + `logs/app.log` + `logs/ai.log`.
