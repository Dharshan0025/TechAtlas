import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("Testing detect endpoint in detail...")

# Test 1: Non-decision (this worked)
print("\n1. Testing non-decision...")
payload1 = {
    "message": "Hey team, how is everyone doing today?",
    "user": "john@company.com",
    "channel_id": "general"
}

try:
    response = requests.post(f"{BASE_URL}/detect-decision", json=payload1)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Decision (this fails)
print("\n2. Testing decision...")
payload2 = {
    "message": "We decided to migrate to PostgreSQL because the schema is stable",
    "user": "priya@company.com",
    "channel_id": "tech-team"
}

try:
    response = requests.post(f"{BASE_URL}/detect-decision", json=payload2)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\nDone.")
