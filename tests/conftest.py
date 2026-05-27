"""
Shared pytest fixtures for CNS Memory Core.

- Stubs out Redis with a fake in-memory token bucket so the suite runs without
  a Redis service (CI still spins up real Redis for the integration job).
- Gives each test a fresh SQLite DB in a temp file.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# Make the project root importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


TEST_API_KEY = "test-key-cns-001"


class _FakeRedis:
    """In-memory stand-in for redis.Redis — supports just what main.py uses."""

    def __init__(self) -> None:
        self._counters: dict[str, tuple[int, float]] = {}  # key -> (count, expires_at)

    def eval(self, script, num_keys, *args):  # noqa: ARG002 — script body ignored, behavior matched
        key = args[0]
        limit = int(args[1])
        window = int(args[2])
        now = time.time()
        count, expires = self._counters.get(key, (0, 0.0))
        if expires < now:
            count, expires = 0, now + window
        count += 1
        self._counters[key] = (count, expires)
        return 0 if count > limit else 1

    def flushall(self) -> None:
        self._counters.clear()


@pytest.fixture
def fake_redis() -> _FakeRedis:
    return _FakeRedis()


@pytest.fixture
def client(monkeypatch, fake_redis):
    """A TestClient pointed at a fresh DB, with Redis replaced by the fake."""
    # Fresh DB file per test
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    os.unlink(db_path)

    monkeypatch.setenv("CNS_API_KEY", TEST_API_KEY)

    # main.py reads the DB path from __file__'s parent — patch it via the module
    # so each test gets isolation without touching production code.
    import importlib

    if "main" in sys.modules:
        del sys.modules["main"]
    main_mod = importlib.import_module("main")
    monkeypatch.setattr(main_mod, "DB_PATH", Path(db_path))
    monkeypatch.setattr(main_mod, "redis_client", fake_redis)

    main_mod.init_db()

    with TestClient(main_mod.app) as c:
        yield c

    try:
        os.remove(db_path)
    except OSError:
        pass


@pytest.fixture
def auth_headers():
    return {"X-API-Key": TEST_API_KEY}
