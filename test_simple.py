import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

print("\n🧪 Testing TechAtlas Backend\n")

# Test 1: Health Check
print("1️⃣  Testing /health...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# Test 2: Save Decision (no AI needed)
print("2️⃣  Testing /save-decision...")
payload = {
    "title": "Database Migration to PostgreSQL",
    "owner": "Priya Kumar",
    "rationale": "Schema has stabilized and we need better support for complex joins",
    "due_date": "2025-12-31",
    "thread_link": "https://cliq.zoho.com/thread/12345",
    "participants": ["priya@company.com", "rahul@company.com"],
    "channel_id": "tech-team"
}

try:
    response = requests.post(f"{BASE_URL}/save-decision", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success!")
        print(f"   Decision ID: {result['decision_id']}")
        print(f"   Message: {result['message']}\n")
        decision_id = result['decision_id']
    else:
        print(f"   ❌ Error: {response.text}\n")
        decision_id = None
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    decision_id = None

# Wait for indexing
if decision_id:
    print("⏳ Waiting 2 seconds for vector indexing...\n")
    time.sleep(2)

    # Test 3: Query Decisions
    print("3️⃣  Testing /query-decisions...")
    query_payload = {
        "query": "Why did we switch to PostgreSQL?",
        "user": "newdev@company.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query-decisions", json=query_payload)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success!")
            print(f"\n   📝 Answer:\n   {result['answer']}\n")
            print(f"   📚 Sources ({len(result['sources'])}):")
            for source in result['sources']:
                print(f"      - {source['title']} (score: {source['relevance_score']:.2f})")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n✅ Testing complete!\n")
