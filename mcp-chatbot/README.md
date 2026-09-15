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
│   ├── api/              # FastAPI routes (chat, health)
│   ├── agent/            # LLM orchestration, prompts, state
│   ├── mcp/
│   │   ├── server.py     # FastMCP server (Phase 2)
│   │   └── client.py     # Simple MCP client for testing
│   ├── tools/
│   │   ├── destinations.py
│   │   └── activities.py
│   ├── services/
│   │   └── globetrotter_service.py   # HTTP client → existing APIs
│   └── utils/
│       └── logger.py
├── docs/
│   └── CAPABILITY_MATRIX.md
├── logs/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Capability Matrix (Phase 0 Audit)

See `docs/CAPABILITY_MATRIX.md` for the full table.

**Currently implemented MCP tools (Phase 2):**

| MCP Tool                        | Backend API                | Status |
|---------------------------------|----------------------------|--------|
| `search_destinations_tool`      | `GET /api/cities`          | ✅     |
| `get_destination_details_tool`  | `GET /api/cities/{id}`     | ✅     |
| `search_activities_tool`        | `GET /api/activities`      | ✅     |
| `get_activity_details_tool`     | `GET /api/activities/{id}` | ✅     |

## Environment Variables

See `.env.example`.

```bash
cp .env.example .env
# At minimum set:
# GLOBETROTTER_API_URL=http://localhost:5000
```

## Development Phases (Current Status)

- [x] **Phase 0** – Audit existing APIs & create capability matrix
- [x] **Phase 1** – Foundation + Logging
- [x] **Phase 2** – MCP Server foundation (real tools → existing APIs)
- [ ] **Phase 3** – Groq + gpt-oss-120b integration
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
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # edit GLOBETROTTER_API_URL if needed
```

Make sure the existing GlobeTrotter Flask backend is running on the URL configured in `.env` (default `http://localhost:5000`).

### 2. Health check (FastAPI)

```bash
uvicorn app.main:app --reload --port 8001
# → http://127.0.0.1:8001/health
```

### 3. Run the MCP Server (stdio)

```bash
python -m app.mcp.server
```

### 4. Test MCP Client → Server → Tool → Existing API (no LLM)

```bash
python -m app.mcp.client
```

This will:
1. Start the MCP server as a subprocess
2. List available tools
3. Call `search_destinations_tool` and `search_activities_tool`
4. Print the JSON returned from the real GlobeTrotter backend

You should see structured logs in the terminal and under `logs/`.

## Logging

All requests, MCP tool executions, backend API calls, latency and errors are logged to:

- Terminal (live)
- `logs/app.log`
- `logs/error.log`
- `logs/ai.log`

with `request_id` correlation and rotating file handlers.
