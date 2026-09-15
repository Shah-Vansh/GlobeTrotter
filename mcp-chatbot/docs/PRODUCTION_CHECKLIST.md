# Production readiness checklist

## Security

- [ ] `GROQ_API_KEY` set via secret manager / env (never commit)
- [ ] `REQUIRE_GROQ_KEY=true` in production
- [ ] `CORS_ORIGINS` limited to real frontend origins (no `*`)
- [ ] Chatbot only reachable from trusted network or behind reverse proxy
- [ ] GlobeTrotter JWT still required for all trip mutations (verified by tests)
- [ ] Rate limit enabled (`RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW_SECONDS`)

## Reliability

- [ ] `GLOBETROTTER_API_URL` points at production Flask API over HTTPS
- [ ] `API_TIMEOUT_SECONDS` and `LLM_TIMEOUT_SECONDS` tuned for your latency
- [ ] Process supervised (systemd / Docker restart policy / k8s)
- [ ] Log directory writable; rotation active (`logs/app.log`, `error.log`, `ai.log`)
- [ ] Monitor `GET /health` and `GET /api/metrics`

## Functional verification

```bash
cd mcp-chatbot && source venv/bin/activate
pytest tests/ -q

# Manual
curl -s http://127.0.0.1:8001/health
curl -s -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Search destinations related to beach"}'

# Auth path (token from Flask login)
curl -s -X POST http://127.0.0.1:8001/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"List my trips"}'
```

## Capability boundary (do not break)

- Chatbot must only call existing GlobeTrotter APIs via tools
- No booking, payments, flights, or hotels
- Unauthorized users cannot mutate trips through chat

## Deploy sketch

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2
```

Put nginx/Caddy in front for TLS and additional rate limiting if needed.
