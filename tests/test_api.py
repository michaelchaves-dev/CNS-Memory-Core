"""Unit tests for CNS Memory Core v1.1.0 API surface."""
from __future__ import annotations


# ────────────────────────────────── /health ────────────────────────────────────


def test_health_no_auth(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["version"] == "1.1.0"


# ──────────────────────────────────── auth ─────────────────────────────────────


def test_save_requires_api_key(client):
    r = client.post("/save", json={"key": "k", "value": "v"})
    assert r.status_code == 401


def test_save_rejects_wrong_key(client):
    r = client.post("/save", headers={"X-API-Key": "wrong"}, json={"key": "k", "value": "v"})
    assert r.status_code == 401


def test_load_requires_api_key(client):
    r = client.get("/load?key=anything")
    assert r.status_code == 401


def test_delete_requires_api_key(client):
    r = client.delete("/delete?key=anything")
    assert r.status_code == 401


def test_list_requires_api_key(client):
    r = client.get("/list")
    assert r.status_code == 401


# ──────────────────────────────────── /save ────────────────────────────────────


def test_save_happy_path(client, auth_headers):
    r = client.post("/save", headers=auth_headers, json={"key": "user:1", "value": {"name": "Alice"}})
    assert r.status_code == 200, r.text
    assert r.json() == {"status": "ok", "message": "saved"}


def test_save_overwrites_existing(client, auth_headers):
    client.post("/save", headers=auth_headers, json={"key": "k", "value": "first"})
    client.post("/save", headers=auth_headers, json={"key": "k", "value": "second"})
    r = client.get("/load?key=k", headers=auth_headers)
    assert r.json()["value"] == "second"


def test_save_rejects_missing_key(client, auth_headers):
    r = client.post("/save", headers=auth_headers, json={"value": "v"})
    assert r.status_code == 400


def test_save_rejects_empty_key(client, auth_headers):
    r = client.post("/save", headers=auth_headers, json={"key": "   ", "value": "v"})
    assert r.status_code == 400


def test_save_rejects_oversized_key(client, auth_headers):
    r = client.post("/save", headers=auth_headers, json={"key": "x" * 257, "value": "v"})
    assert r.status_code == 400


def test_save_rejects_missing_value(client, auth_headers):
    r = client.post("/save", headers=auth_headers, json={"key": "k"})
    assert r.status_code == 400


def test_save_rejects_oversized_payload(client, auth_headers):
    big_value = "x" * 60_000
    r = client.post("/save", headers=auth_headers, json={"key": "k", "value": big_value})
    assert r.status_code == 413


def test_save_accepts_nested_json(client, auth_headers):
    nested = {"a": {"b": {"c": [1, 2, 3]}}, "list": ["x", "y"]}
    client.post("/save", headers=auth_headers, json={"key": "nested", "value": nested})
    r = client.get("/load?key=nested", headers=auth_headers)
    assert r.json()["value"] == nested


# ──────────────────────────────────── /load ────────────────────────────────────


def test_load_missing_key_returns_null(client, auth_headers):
    r = client.get("/load?key=nope", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "value": None}


def test_load_rejects_oversized_key(client, auth_headers):
    r = client.get("/load", params={"key": "x" * 257}, headers=auth_headers)
    assert r.status_code == 400


def test_load_round_trip_string(client, auth_headers):
    client.post("/save", headers=auth_headers, json={"key": "s", "value": "hello"})
    r = client.get("/load?key=s", headers=auth_headers)
    assert r.json()["value"] == "hello"


def test_load_round_trip_int(client, auth_headers):
    client.post("/save", headers=auth_headers, json={"key": "n", "value": 42})
    r = client.get("/load?key=n", headers=auth_headers)
    assert r.json()["value"] == 42


# ─────────────────────────────────── /delete ───────────────────────────────────


def test_delete_existing_key(client, auth_headers):
    client.post("/save", headers=auth_headers, json={"key": "todelete", "value": "x"})
    r = client.delete("/delete?key=todelete", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "found": True}
    # Confirm gone
    r2 = client.get("/load?key=todelete", headers=auth_headers)
    assert r2.json()["value"] is None


def test_delete_missing_key_is_idempotent(client, auth_headers):
    r = client.delete("/delete?key=never-existed", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "found": False}


def test_delete_rejects_oversized_key(client, auth_headers):
    r = client.delete("/delete", params={"key": "x" * 257}, headers=auth_headers)
    assert r.status_code == 400


# ──────────────────────────────────── /list ────────────────────────────────────


def test_list_empty(client, auth_headers):
    r = client.get("/list", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body == {"status": "ok", "items": [], "total": 0, "limit": 100, "offset": 0}


def test_list_returns_keys_and_timestamps_not_values(client, auth_headers):
    client.post("/save", headers=auth_headers, json={"key": "a", "value": "secret-val"})
    r = client.get("/list", headers=auth_headers)
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["key"] == "a"
    assert "timestamp" in body["items"][0]
    assert "value" not in body["items"][0]
    assert "secret-val" not in r.text


def test_list_prefix_filter(client, auth_headers):
    for k in ("user:1", "user:2", "session:1", "session:2"):
        client.post("/save", headers=auth_headers, json={"key": k, "value": "x"})
    r = client.get("/list", params={"prefix": "user:"}, headers=auth_headers)
    body = r.json()
    assert body["total"] == 2
    assert {item["key"] for item in body["items"]} == {"user:1", "user:2"}


def test_list_prefix_escapes_sql_wildcards(client, auth_headers):
    """A prefix of '%' must NOT match everything — % is escaped."""
    for k in ("a", "b", "%real"):
        client.post("/save", headers=auth_headers, json={"key": k, "value": "x"})
    r = client.get("/list", params={"prefix": "%"}, headers=auth_headers)
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["key"] == "%real"


def test_list_pagination(client, auth_headers):
    for i in range(5):
        client.post("/save", headers=auth_headers, json={"key": f"k{i}", "value": i})
    page1 = client.get("/list", params={"limit": 2, "offset": 0}, headers=auth_headers).json()
    page2 = client.get("/list", params={"limit": 2, "offset": 2}, headers=auth_headers).json()
    page3 = client.get("/list", params={"limit": 2, "offset": 4}, headers=auth_headers).json()
    assert page1["total"] == 5
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 2
    assert len(page3["items"]) == 1
    seen = {i["key"] for i in page1["items"] + page2["items"] + page3["items"]}
    assert seen == {f"k{i}" for i in range(5)}


def test_list_rejects_bad_limit(client, auth_headers):
    r = client.get("/list", params={"limit": 0}, headers=auth_headers)
    assert r.status_code == 400
    r = client.get("/list", params={"limit": 1001}, headers=auth_headers)
    assert r.status_code == 400


def test_list_rejects_negative_offset(client, auth_headers):
    r = client.get("/list", params={"offset": -1}, headers=auth_headers)
    assert r.status_code == 400


# ─────────────────────────────── rate limiting ─────────────────────────────────


def test_rate_limit_kicks_in_at_11th_request(client, auth_headers):
    # Rate is 10 req/60s per IP; 11th should 429
    for _ in range(10):
        r = client.get("/load?key=k", headers=auth_headers)
        assert r.status_code == 200
    r = client.get("/load?key=k", headers=auth_headers)
    assert r.status_code == 429
