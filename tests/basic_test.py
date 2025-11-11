import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("Testing basic endpoints...")

# Test 1: Health
print("\n1. Testing /health...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Save decision (should work)
print("\n2. Testing /save-decision...")
try:
    payload = {
        "title": "Test Decision",
        "owner": "Test User",
        "rationale": "Testing save functionality",
        "due_date": "2025-12-31",
        "thread_link": "https://test.com",
        "participants": ["test@example.com"],
        "channel_id": "test"
    }
    response = requests.post(f"{BASE_URL}/save-decision", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Save decision works!")
        print(f"Response: {response.json()}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\nDone.")
