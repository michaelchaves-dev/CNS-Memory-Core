#!/usr/bin/env python3
"""
Simple integration test for CNS Memory Core v1.0.9
Tests save and load endpoints with proper authentication and error handling.
"""
import requests
import json
import sys
from time import sleep

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "test-key-ci"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


def test_save_and_load():
    test_key = "test_session_001"
    test_value = {
        "user": "michael_chaves",
        "status": "active",
        "timestamp": "2026-04-14T20:00:00Z",
    }
