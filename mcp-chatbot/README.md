# GlobeTrotter MCP AI Chatbot

Natural-language interface over the existing GlobeTrotter application using **MCP + Groq (`openai/gpt-oss-120b`) + FastAPI**.

> **Core rule**: The chatbot can only do what the existing GlobeTrotter frontend + backend already support. MCP tools are thin wrappers around existing APIs. No invented functionality.

## Architecture Summary

```
User → Chat UI → FastAPI Chat API → AI Agent (Groq / gpt-oss-120b)
                                          ↓
                                    MCP Client
                                          ↓
                                    MCP Server + Tools
                                          ↓
                              Existing GlobeTrotter APIs
                                          ↓
                                   Existing Backend + DB
```

## Development Branch

All work for this feature happens exclusively on the **`dev`** branch.

## Project Structure

```
mcp-chatbot/
├── app/
│   ├── api/
│   │   └── chat.py           # /api/chat/test (Phase 3)
│   ├── agent/                # (Phase 4+)
│   ├── mcp/
│   │   ├── server.py         # FastMCP server (Phase 2)
│   │   └── client.py         # MCP client for testing
│   ├── tools/
│   │   ├── destinations.py
│   │   └── activities.py
│   ├── services/
│   │   ├── globetrotter_service.py
│   │   └── llm_service.py    # Groq client (Phase 3)
│   └── utils/
│       └── logger.py
├── scripts/
│   └── test_llm.py           # CLI smoke-test for Groq
├── docs/
│   └── CAPABILITY_MATRIX.md
├── logs/
├── .env.example
├── requirements.txt
└── README.md
```

## Capability Matrix

See `docs/CAPABILITY_MATRIX.md`.

**Implemented MCP tools (Phase 2):**

| MCP Tool                        | Backend API                | Status |
|---------------------------------|----------------------------|--------|
| `search_destinations_tool`      | `GET /api/cities`          | ✅     |
| `get_destination_details_tool`  | `GET /api/cities/{id}`     | ✅     |
| `search_activities_tool`        | `GET /api/activities`      | ✅     |
| `get_activity_details_tool`     | `GET /api/activities/{id}` | ✅     |

## Environment Variables

```bash
cp .env.example .env
```

Required for Phase 3:

```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
GLOBETROTTER_API_URL=http://localhost:5000
```

## Development Phases (Current Status)

- [x] **Phase 0** – Audit existing APIs & create capability matrix
- [x] **Phase 1** – Foundation + Logging
- [x] **Phase 2** – MCP Server foundation (real tools → existing APIs)
- [x] **Phase 3** – Groq + gpt-oss-120b integration (request / response / tokens / latency / errors)
- [ ] **Phase 4** – LLM + MCP tool calling
- [ ] **Phase 5** – Full API → MCP tool mapping (trips, itinerary, …)
- [ ] **Phase 6** – Agentic multi-tool workflows
- [ ] **Phase 7** – Conversation memory / state
- [ ] **Phase 8** – Full observability
- [ ] **Phase 9** – Frontend Chat UI integration
- [ ] **Phase 10** – Testing, security, production readiness

## Running

### 1. Install

```bash
cd mcp-chatbot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set GROQ_API_KEY and GLOBETROTTER_API_URL
```

### 2. Health check

```bash
uvicorn app.main:app --reload --port 8001
# → http://127.0.0.1:8001/health
```

### 3. Test Groq LLM (Phase 3) – CLI

```bash
python -m scripts.test_llm
python -m scripts.test_llm "Suggest a 3-day beach destination in India"
```

You will see the model reply plus:

```
request_id, latency, input_tokens, output_tokens, total_tokens
```

Logs also appear in the terminal and under `logs/ai.log`.

### 4. Test Groq LLM (Phase 3) – HTTP

```bash
curl -X POST http://127.0.0.1:8001/api/chat/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you help me with?"}'
```

### 5. Test MCP tools only (Phase 2, no LLM)

```bash
# Ensure GlobeTrotter Flask backend is running on :5000
python -m app.mcp.client
```

## Logging (Phase 3)

Every LLM call logs:

```
LLM_REQUEST  request_id=… provider=groq model=openai/gpt-oss-120b
LLM_RESPONSE request_id=… latency=…s input_tokens=… output_tokens=… total_tokens=…
LLM_USAGE    (same data written to ai.log)
LLM_ERROR    (on failure, with type + status)
```

All logs go to terminal + rotating files in `logs/`.
