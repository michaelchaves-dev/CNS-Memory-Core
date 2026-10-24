# CNS Memory Core v1.1.0

Lightweight single-node REST API that provides persistent key-value memory for AI agents and applications.

## What It Does

CNS Memory Core exposes a REST API that allows AI agents and applications to save, retrieve, and health-check persistent key-value state using SQLite.

## Features

- API key authentication (`CNS_API_KEY` required; no demo fallback)
- Redis rate limiting (10 req/60s per IP)
- SQLite persistence (WAL mode)
- Single-node deployment (lightweight, runs on one server)
- Input validation and payload size limits
- Structured logging

## Security

- Set `CNS_API_KEY` as a hosting-platform secret (or local `.env`). The process exits if it is missing.
- Never put `CNS_API_KEY` in browser JavaScript, `NEXT_PUBLIC_*`, `VITE_*`, or any client-visible config. CORS is browser policy, not authentication — the API key is what protects CNS.

## Endpoints

| Method | Route                       | Description                                       |
|--------|-----------------------------|---------------------------------------------------|
| POST   | `/save`                     | Store a key-value pair                            |
| GET    | `/load?key=`                | Retrieve a stored value                           |
| DELETE | `/delete?key=`              | Remove a key (idempotent)                         |
| GET    | `/list?prefix=&limit=&offset=` | Enumerate keys (paginated, keys + timestamps only) |
| GET    | `/health`                   | Service health check                              |

### Sample list response

```json
{
  "status": "ok",
  "items": [{"key": "user:1", "timestamp": "2026-05-27 03:45:00"}],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

## Quick Start

**Requirements:** Python 3.9+, Redis

```bash
git clone https://github.com/michael-chaves-dev/cns-memory-core
cd cns-memory-core
pip install -r requirements.txt
cp .env.example .env   # set a real CNS_API_KEY before starting
export $(grep -v '^#' .env | xargs)
uvicorn main:app --reload
```

## Running tests

The unit suite stubs out Redis with an in-memory fake so it runs anywhere:

```bash
pip install -r requirements.txt
pytest -q
```

The integration test (`test_load.py`) requires a running server and live
Redis — CI runs it after the unit suite passes.

## License

CNS Memory Core is licensed under Apache 2.0 + Commons Clause v1.0.
Non-commercial use, modification, and forking are permitted.
Commercial use, SaaS hosting, or consulting services derived from this software are prohibited without explicit written permission.

Architect & Owner: Michael Chaves
Commercial licensing inquiries: michaelfchaves@gmail.com

Any fork or derivative must include:
"CNS Memory Core was originally designed and architected by Michael Chaves."

<!-- SAS-IP-FOOTER-v1 -->
---
**Subtract Architect Studios™**  
Copyright © 2026 Michael F. Chaves. All rights reserved in original Subtract Architect Studios materials except as expressly licensed. See [IP_NOTICE.md](./IP_NOTICE.md). Existing open-source and third-party licenses remain controlling for materials they cover.
