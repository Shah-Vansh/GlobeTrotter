# GlobeTrotter MCP AI Chatbot

Natural-language interface over existing GlobeTrotter APIs via **Groq + tools + FastAPI**.

> **Rule:** Chatbot capability = frontend capability. Tools only wrap real APIs.

## Status: Phases 0–10 complete

| Phase | Deliverable |
|-------|-------------|
| 0–1 | Audit, logging foundation |
| 2 | MCP-style tools over existing APIs |
| 3 | Groq + gpt-oss-120b |
| 4 | Agentic tool loop |
| 5 | Full trips/stops/itinerary tools + JWT |
| 6 | Multi-step workflows |
| 7 | Durable conversation memory |
| 8 | Metrics + observability |
| 9 | React ChatWidget |
| **10** | **Tests, rate limit, production checklist** |

## Production features (Phase 10)

- Rate limiting on `/api/chat` (default 30 req / 60s per IP)
- Configurable CORS, API/LLM timeouts
- Optional `REQUIRE_GROQ_KEY`
- Automated tests: auth tools, schemas, metrics, rate limit
- Checklist: `docs/PRODUCTION_CHECKLIST.md`

```bash
pytest tests/ -q
```

## Run full stack

```bash
# Flask :5000 | Chatbot :8001 | React :5173
uvicorn app.main:app --reload --port 8001
```

Client env:

```
VITE_BASE_URL=http://localhost:5000
VITE_CHATBOT_URL=http://127.0.0.1:8001
```

## Key endpoints

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/chat` | Agent + tools (JWT optional for public tools) |
| GET | `/api/conversations` | Memory |
| GET | `/api/metrics` | Counters |
| GET | `/health` | Liveness |
