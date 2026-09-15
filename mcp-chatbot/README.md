# GlobeTrotter MCP AI Chatbot

Natural-language interface over existing GlobeTrotter APIs via **Groq (`openai/gpt-oss-120b`) + MCP-style tools + FastAPI**.

> Chatbot capability = frontend capability. No invented features.

## Multi-step workflows (Phase 6)

The agent can chain tools, for example:

```
search_destinations → get_destination_details → search_activities
  → create_trip → add_stop_to_trip → add_activity_to_itinerary → get_trip_budget
```

Improvements in Phase 6:
- Workflow patterns documented in the system prompt
- Up to **10** tool rounds per request
- Large tool payloads compacted (top N items) to keep context healthy
- `workflow_steps` returned in API responses and logs (`search_destinations✓ → create_trip✓ → …`)

## Auth

```
Authorization: Bearer <access_token from POST /api/auth/login>
```

Without a token: public destination/activity tools only.  
With a token: same privileges as that user on the Flask backend.

## Tools

Public: `search_destinations`, `get_destination_details`, `search_activities`, `get_activity_details`  
Auth: trips, stops, itinerary, budget, share/unshare (full matrix in `docs/CAPABILITY_MATRIX.md`)

## Phases

- [x] 0–5 Foundation, MCP tools, Groq, agent, full trip mapping + JWT
- [x] **6 – Agentic multi-tool workflows**
- [ ] 7 – Durable conversation memory
- [ ] 8 – Observability polish
- [ ] 9 – Frontend Chat UI
- [ ] 10 – Production readiness

## Run

```bash
cd mcp-chatbot && source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

### Public multi-step

```bash
curl -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Find beach-related destinations and suggest highly rated activities"}'
```

### Authenticated multi-step (plan a trip)

```bash
# token from: POST http://localhost:5000/api/auth/login  {"username":"alice","password":"Password@123"}

curl -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"Search Goa, create a trip Goa Escape 2026-12-01 to 2026-12-05, add a stop, and list my trips"}'
```

Response includes `workflow_steps` and `tool_calls_made`.

### CLI workflow tests

```bash
python -m scripts.test_workflow
ACCESS_TOKEN=eyJ... python -m scripts.test_workflow
```
