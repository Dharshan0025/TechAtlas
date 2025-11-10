import requests

BASE_URL = "http://127.0.0.1:5000"

print("Testing routes endpoint...")
try:
    response = requests.get(f"{BASE_URL}/routes")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        routes = response.json()
        print("Registered routes:")
        for route in routes:
            print(f"  {route['methods']} {route['url']} -> {route['endpoint']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")
