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
API_KEY = "demo-key-123"  # Change to match your .env value for local testing

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def test_save_and_load():
    test_key = "test_session_001"
    test_value = {
        "user": "michael_chaves",
        "status": "active",
        "timestamp": "2026-04-14T20:00:00Z"
    }

    print("=== CNS Memory Core Integration Test ===")

    # Test SAVE
    save_payload = {"key": test_key, "value": test_value}
    response = requests.post(f"{BASE_URL}/save", json=save_payload, headers=HEADERS)

    print(f"SAVE status: {response.status_code}")
    if response.status_code != 200:
        print(f"ERROR: {response.text}")
        sys.exit(1)
    print("SAVE successful")

    # Brief pause
    sleep(0.5)

    # Test LOAD
    response = requests.get(f"{BASE_URL}/load?key={test_key}", headers=HEADERS)

    print(f"LOAD status: {response.status_code}")
    if response.status_code != 200:
        print(f"ERROR: {response.text}")
        sys.exit(1)

    data = response.json()
    if data.get("value") != test_value:
        print("ERROR: Loaded value does not match saved value")
        sys.exit(1)

    print("LOAD successful - value matches")
    print("All tests passed.")


if __name__ == "__main__":
    test_save_and_load()
