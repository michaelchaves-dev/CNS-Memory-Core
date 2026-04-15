# Copyright (c) 2026 Michael Chaves
# CNS Memory Core v1.0.9 (FINAL INTEGRITY LOCK)
# main.py - Memory Core API Service
#
# Licensed under Apache 2.0 with Commons Clause v1.0
# Non-commercial use, modification, forking and distribution permitted.
# Commercial sale, hosting, SaaS, consulting, or any service whose value
# derives substantially from this software is STRICTLY PROHIBITED.
#
# Architect & Owner: Michael Chaves
# Any fork/derivative/academic reference MUST include attribution:
# "CNS Memory Core was originally designed and architected by Michael Chaves."
# Full terms: See LICENSE file in repository root.
# Commercial licensing inquiries: michaelfchaves@gmail.com

import os
import json
import logging
from pathlib import Path
from contextlib import contextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import redis

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

API_KEY = os.getenv("CNS_API_KEY", "demo-key-123")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
DB_PATH = Path(__file__).parent / "cns_memory.db"
RATE_WINDOW = 60
RATE_LIMIT = 10
PAYLOAD_CAP = 50000

RATE_LIMIT_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = redis.call("INCR", key)
if current == 1 then
    redis.call("EXPIRE", key, window)
end
if current > limit then
    return 0
end
return 1
"""


@contextmanager
def get_db():
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        yield conn
    finally:
        if conn:
            conn.close()


def rate_limit_dep(request: Request):
    ip = request.client.host or "unknown"
    key = f"rate_limit:{ip}"
    try:
        allowed = redis_client.eval(RATE_LIMIT_SCRIPT, 1, key, RATE_LIMIT, RATE_WINDOW)
        if allowed == 0:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        return True
    except redis.RedisError as e:
        logger.error("Redis rate limiter unavailable: %s", e)
        raise HTTPException(status_code=503, detail="Rate limiting service unavailable")


def get_api_key(request: Request):
    key = request.headers.get("X-API-Key")
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key


app = FastAPI(title="CNS Memory Core", version="1.0.9")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cns_memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    logger.info("CNS Memory DB initialized at %s", DB_PATH)


init_db()


@app.post("/save")
def save(data: dict = Body(...), _=Depends(rate_limit_dep), __=Depends(get_api_key)):
    key = data.get("key")
    value = data.get("value")
    if not key or not isinstance(key, str) or not key.strip():
        raise HTTPException(400, "Missing or invalid 'key'")
    if len(key) > 256:
        raise HTTPException(400, "Key exceeds 256 character limit")
    if value is None:
        raise HTTPException(400, "Missing 'value'")
    serialized = json.dumps(value, ensure_ascii=False)
    if len(serialized) > PAYLOAD_CAP:
        raise HTTPException(413, f"Payload exceeds {PAYLOAD_CAP} byte limit")
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cns_memory (key, value, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, serialized)
            )
            conn.commit()
        logger.info("SAVE key=%s size=%d bytes", key, len(serialized))
        return {"status": "ok", "message": "saved"}
    except sqlite3.Error as e:
        logger.error("SAVE DB error: %s", e)
        raise HTTPException(500, "Database error")


@app.get("/load")
def load(key: str, _=Depends(rate_limit_dep), __=Depends(get_api_key)):
    if not key or len(key) > 256:
        raise HTTPException(400, "Invalid key")
    try:
        with get_db() as conn:
            row = conn.execute("SELECT value FROM cns_memory WHERE key=?", (key,)).fetchone()
            logger.info("LOAD key=%s found=%s", key, bool(row))
            if row is None:
                return {"status": "ok", "value": None}
            try:
                return {"status": "ok", "value": json.loads(row["value"])}
            except (json.JSONDecodeError, TypeError):
                return {"status": "ok", "value": row["value"]}
    except sqlite3.Error as e:
        logger.error("LOAD DB error: %s", e)
        raise HTTPException(500, "Database error")


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.9"}
