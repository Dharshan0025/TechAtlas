#!/usr/bin/env python3
"""Test the detect endpoint with maximum debugging"""

import requests
import json
import time

def test_detect():
    BASE_URL = "http://127.0.0.1:5000"

    # Test decision message
    payload = {
        "message": "We decided to migrate to PostgreSQL because the schema is stable",
        "user": "priya@company.com",
        "channel_id": "tech-team"
    }

    print("Sending request...")
    print(f"URL: POST {BASE_URL}/detect-decision")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload, timeout=30)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Parsed JSON: {json.dumps(data, indent=2)}")
            except:
                print("Failed to parse JSON")
        else:
            print("Request failed")

    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.ConnectionError:
        print("Connection error - server not running?")
    except Exception as e:
        print(f"Other error: {e}")

if __name__ == "__main__":
    test_detect()
