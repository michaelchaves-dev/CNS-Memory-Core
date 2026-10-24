"""Startup must fail closed when CNS_API_KEY is missing."""
from __future__ import annotations

import importlib
import sys


def test_main_refuses_missing_api_key(monkeypatch):
    monkeypatch.delenv("CNS_API_KEY", raising=False)
    sys.modules.pop("main", None)
    try:
        importlib.import_module("main")
        assert False, "expected RuntimeError when CNS_API_KEY is unset"
    except RuntimeError as exc:
        assert "CNS_API_KEY" in str(exc)


def test_cns_refuses_missing_api_key(monkeypatch):
    monkeypatch.delenv("CNS_API_KEY", raising=False)
    sys.modules.pop("cns", None)
    try:
        importlib.import_module("cns")
        assert False, "expected RuntimeError when CNS_API_KEY is unset"
    except RuntimeError as exc:
        assert "CNS_API_KEY" in str(exc)


def test_main_refuses_blank_api_key(monkeypatch):
    monkeypatch.setenv("CNS_API_KEY", "   ")
    sys.modules.pop("main", None)
    try:
        importlib.import_module("main")
        assert False, "expected RuntimeError when CNS_API_KEY is blank"
    except RuntimeError as exc:
        assert "CNS_API_KEY" in str(exc)
