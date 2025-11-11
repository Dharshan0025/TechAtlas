import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("Testing failing endpoints...")

# Test detect endpoint
print("\n1. Testing /detect-decision...")
try:
    payload = {
        "message": "We decided to migrate to PostgreSQL because the schema is stable",
        "user": "priya@company.com",
        "channel_id": "tech-team"
    }
    response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test query endpoint
print("\n2. Testing /query-decisions...")
try:
    payload = {
        "query": "Why did we switch to PostgreSQL?",
        "user": "newdev@company.com"
    }
    response = requests.post(f"{BASE_URL}/query-decisions", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
