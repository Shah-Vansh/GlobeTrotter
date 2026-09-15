# GlobeTrotter MCP AI Chatbot

Natural-language interface over the existing GlobeTrotter application using **MCP + Groq (`openai/gpt-oss-120b`) + FastAPI**.

> **Core rule**: Chatbot capability = existing frontend capability. Tools only wrap real APIs. No invented features.

## Auth model

```
Frontend JWT  →  Authorization: Bearer <token>  →  /api/chat  →  agent  →  tools  →  same backend APIs
```

The chatbot never gets more privilege than the logged-in user.

## Implemented tools (Phase 5)

**Public**
| Tool | API |
|------|-----|
| `search_destinations` | `GET /api/cities` |
| `get_destination_details` | `GET /api/cities/{id}` |
| `search_activities` | `GET /api/activities` |
| `get_activity_details` | `GET /api/activities/{id}` |

**Authenticated (JWT required)**
| Tool | API |
|------|-----|
| `list_trips` | `GET /api/trips` |
| `create_trip` | `POST /api/trips` |
| `get_trip` | `GET /api/trips/{id}` |
| `update_trip` | `PUT /api/trips/{id}` |
| `delete_trip` | `DELETE /api/trips/{id}` |
| `get_trip_budget` | `GET /api/trips/{id}/budget` |
| `share_trip` / `unshare_trip` | `POST .../share` / `unshare` |
| `add_stop_to_trip` | `POST .../stops` |
| `update_stop` / `remove_stop` | `PUT/DELETE .../stops/{id}` |
| `reorder_stops` | `PUT .../stops/reorder` |
| `list_itinerary` | `GET .../itinerary` |
| `add_activity_to_itinerary` | `POST .../itinerary` |
| `update_itinerary_activity` | `PUT .../itinerary/{id}` |
| `remove_activity_from_itinerary` | `DELETE .../itinerary/{id}` |

## Phases

- [x] Phase 0–4
- [x] **Phase 5 – Full trip/itinerary API → tools + JWT**
- [ ] Phase 6 – Richer multi-tool workflows polish
- [ ] Phase 7 – Durable conversation memory
- [ ] Phase 8 – Observability polish
- [ ] Phase 9 – Frontend Chat UI
- [ ] Phase 10 – Production readiness

## Quick start

```bash
cd mcp-chatbot
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # GROQ_API_KEY + GLOBETROTTER_API_URL

# Terminal 1: Flask backend
# Terminal 2:
uvicorn app.main:app --reload --port 8001
```

### Public query

```bash
curl -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search destinations related to Goa"}'
```

### Authenticated query (use token from POST /api/auth/login)

```bash
curl -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"message": "Create a 5-day Goa trip starting 2026-12-01 and list my trips"}'
```

Demo users from seed: `alice` / `Password@123`

### CLI agent

```bash
python -m scripts.test_agent "Find highly rated activities"
```

## Logging

Every request logs `request_id`, tool names, API endpoints, latency, tokens, and errors to terminal + `logs/`.
