# GlobeTrotter MCP AI Chatbot

Natural-language interface over existing GlobeTrotter APIs via **Groq + tools + FastAPI**.

> Chatbot capability = frontend capability. No invented features.

## Observability (Phase 8)

Every request is correlated with a `request_id` across:

- Terminal logs
- `logs/app.log` (rotating, 5 MB × 5)
- `logs/error.log` (errors only)
- `logs/ai.log` (LLM / tools / tokens)

### Metrics API

```
GET  /api/metrics           # request counts, tokens, tool stats, latency
POST /api/metrics/reset     # reset counters
GET  /api/observability     # log file status + metrics snapshot
GET  /health
```

Example metrics payload fields: `requests.total/success/failed`, `llm.input_tokens/output_tokens`, `tools.by_name`, `latency_seconds.avg/max`.

### Tests

```bash
cd mcp-chatbot && source venv/bin/activate
pytest tests/test_logging.py -q
```

## Memory (Phase 7)

Reuse `conversation_id` across turns. Manage via `/api/conversations`.

## Auth

`Authorization: Bearer <access_token>` for trip tools.

## Phases

- [x] 0–7 Foundation through durable memory
- [x] **8 – Observability (metrics, log rotation, tests)**
- [ ] 9 – Frontend Chat UI
- [ ] 10 – Production readiness

## Run

```bash
cd mcp-chatbot && source venv/bin/activate
uvicorn app.main:app --reload --port 8001

curl http://127.0.0.1:8001/api/metrics
curl http://127.0.0.1:8001/api/observability
```
