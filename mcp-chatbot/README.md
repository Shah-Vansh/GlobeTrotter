# GlobeTrotter MCP AI Chatbot

Natural-language interface over existing GlobeTrotter APIs via **Groq + tools + FastAPI**.

> Chatbot capability = frontend capability. No invented features.

## Conversation memory (Phase 7)

- Reuse the same `conversation_id` across messages to keep history
- Messages stored in memory + JSON files under `data/conversations/`
- Windowed to the last **40** messages
- Idle conversations expire from RAM after **12 hours** (disk files remain until deleted)
- Session metadata tracks `last_trip_id`, `last_stop_id`, `recent_tools` and is injected into the system prompt so follow-ups like “add activities to that trip” work

### Memory APIs

```
GET    /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}
```

### Multi-turn example

```bash
# Turn 1
curl -s -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"Create a trip Goa Escape from 2026-12-01 to 2026-12-05"}'
# → note conversation_id from response

# Turn 2 (same conversation_id)
curl -s -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"conversation_id":"conv_…","message":"Add a stop for the Goa city we found and list my trips"}'
```

## Auth

`Authorization: Bearer <access_token>` — same JWT as the GlobeTrotter frontend.

## Phases

- [x] 0–6 Foundation, tools, Groq, agent, trips, multi-step workflows
- [x] **7 – Durable conversation memory**
- [ ] 8 – Observability polish
- [ ] 9 – Frontend Chat UI
- [ ] 10 – Production readiness

## Run

```bash
cd mcp-chatbot && source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

Inspect memory:

```bash
curl http://127.0.0.1:8001/api/conversations
curl http://127.0.0.1:8001/api/conversations/conv_xxxx
```
