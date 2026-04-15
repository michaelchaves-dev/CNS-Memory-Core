# CNS Memory Core v1.0.9

Persistent memory API for AI systems.

## What It Does

CNS Memory Core exposes a REST API that allows AI agents and applications to save, retrieve, and health-check persistent key-value state using SQLite.

## Features

- API key authentication
- Redis rate limiting (10 req/60s per IP)
- SQLite persistence (WAL mode)
- Input validation and payload size limits
- Structured logging

## Endpoints

| Method | Route          | Description                |
|--------|----------------|----------------------------|
| POST   | `/save`        | Store a key-value pair     |
| GET    | `/load?key=`   | Retrieve a stored value    |
| GET    | `/health`      | Service health check       |

## Quick Start

**Requirements:** Python 3.9+, Redis

```bash
git clone https://github.com/michael-chaves-dev/cns-memory-core
cd cns-memory-core
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

## License

CNS Memory Core is licensed under Apache 2.0 + Commons Clause v1.0.
Non-commercial use, modification, and forking are permitted.
Commercial use, SaaS hosting, or consulting services derived from this software are prohibited without explicit written permission.

Architect & Owner: Michael Chaves
Commercial licensing inquiries: michaelfchaves@gmail.com

Any fork or derivative must include:
"CNS Memory Core was originally designed and architected by Michael Chaves."
