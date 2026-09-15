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
│   ├── mcp/              # MCP client + server
│   ├── tools/            # MCP tools (wrappers around GlobeTrotter APIs)
│   ├── services/         # LLM service, GlobeTrotter HTTP client
│   └── utils/            # logger, helpers
├── logs/                 # Rotating log files (app.log, error.log, ai.log)
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Capability Matrix (Phase 0 Audit)

Based on actual routes in `server/app/routes/`:

| Frontend Feature              | Existing API                          | Auth Required | Planned MCP Tool                  | Status |
|-------------------------------|---------------------------------------|---------------|-----------------------------------|--------|
| List / Search Cities          | `GET /api/cities`                     | No            | `search_destinations`             | ⬜     |
| Get City Details              | `GET /api/cities/{id}`                | No            | `get_destination_details`         | ⬜     |
| List / Search Activities      | `GET /api/activities`                 | No            | `search_activities`               | ⬜     |
| Get Activity Details          | `GET /api/activities/{id}`            | No            | `get_activity_details`            | ⬜     |
| List My Trips                 | `GET /api/trips`                      | Yes           | `list_trips`                      | ⬜     |
| Create Trip                   | `POST /api/trips`                     | Yes           | `create_trip`                     | ⬜     |
| Get Trip (with stops)         | `GET /api/trips/{id}`                 | Yes           | `get_trip`                        | ⬜     |
| Update Trip                   | `PUT /api/trips/{id}`                 | Yes           | `update_trip`                     | ⬜     |
| Delete Trip                   | `DELETE /api/trips/{id}`              | Yes           | `delete_trip`                     | ⬜     |
| Add Stop to Trip              | `POST /api/trips/{id}/stops`          | Yes           | `add_stop_to_trip`                | ⬜     |
| Update / Delete Stop          | `PUT/DELETE .../stops/{stop_id}`      | Yes           | `update_stop` / `remove_stop`     | ⬜     |
| Reorder Stops                 | `PUT .../stops/reorder`               | Yes           | `reorder_stops`                   | ⬜     |
| Get Budget Breakdown          | `GET /api/trips/{id}/budget`          | Yes           | `get_trip_budget`                 | ⬜     |
| Share / Unshare Trip          | `POST .../share` / `unshare`          | Yes           | `share_trip` / `unshare_trip`     | ⬜     |
| List Itinerary for Stop       | `GET .../itinerary`                   | Yes           | `list_itinerary`                  | ⬜     |
| Add Activity to Itinerary     | `POST .../itinerary`                  | Yes           | `add_activity_to_itinerary`       | ⬜     |
| Update / Remove Itinerary Act | `PUT/DELETE .../itinerary/{id}`       | Yes           | `update_itinerary_activity` etc.  | ⬜     |
| Auth (login / me)             | `POST /api/auth/login`, `GET /me`     | –             | (handled via token passing)       | ⬜     |

Admin-only endpoints (create/update/delete cities & activities) will **not** be exposed to normal users via the chatbot unless the authenticated user is an admin.

## Environment Variables

See `.env.example`.

## Development Phases (Current Status)

- [x] **Phase 0** – Audit existing APIs & create capability matrix
- [ ] **Phase 1** – Foundation + Logging
- [ ] **Phase 2** – MCP Server foundation (one real tool)
- [ ] **Phase 3** – Groq + gpt-oss-120b integration
- [ ] **Phase 4** – LLM + MCP tool calling
- [ ] **Phase 5** – Full API → MCP tool mapping
- [ ] **Phase 6** – Agentic multi-tool workflows
- [ ] **Phase 7** – Conversation memory / state
- [ ] **Phase 8** – Full observability
- [ ] **Phase 9** – Frontend Chat UI integration
- [ ] **Phase 10** – Testing, security, production readiness

## Running (once implemented)

```bash
cd mcp-chatbot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill GROQ_API_KEY etc.
uvicorn app.main:app --reload --port 8001
```

## Logging

All requests, LLM calls, MCP tool executions, backend API calls, token usage, latency and errors are logged to:

- Terminal (live)
- `logs/app.log`
- `logs/error.log`
- `logs/ai.log`

with request_id correlation and rotating file handlers.
