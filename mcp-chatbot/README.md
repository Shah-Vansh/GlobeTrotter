# GlobeTrotter MCP AI Chatbot

Natural-language interface over existing GlobeTrotter APIs via **Groq + tools + FastAPI**.

> Chatbot capability = frontend capability. No invented features.

## Frontend (Phase 9)

A floating **ChatWidget** is mounted in `client/src/layout/MainLayout.jsx` (authenticated shell only).

- Uses `VITE_CHATBOT_URL` (default `http://127.0.0.1:8001`)
- Sends `Authorization: Bearer` from `tokenStorage` (same JWT as the app)
- Keeps `conversation_id` in `localStorage` for multi-turn memory
- Shows workflow steps under assistant replies when tools ran

### Run full stack

```bash
# Terminal 1 – Flask backend
cd server && flask run   # :5000

# Terminal 2 – MCP chatbot
cd mcp-chatbot && source venv/bin/activate
uvicorn app.main:app --reload --port 8001

# Terminal 3 – React client
cd client && npm run dev   # :5173
```

Set in `client/.env`:

```
VITE_BASE_URL=http://localhost:5000
VITE_CHATBOT_URL=http://127.0.0.1:8001
```

## Observability

`GET /api/metrics` · `GET /api/observability` · rotating logs under `logs/`

## Phases

- [x] 0–8 Backend agent, tools, memory, metrics
- [x] **9 – Frontend Chat UI**
- [ ] 10 – Testing & production readiness
