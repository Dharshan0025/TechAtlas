import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    print(f"{'='*60}\n")

def test_detect_decision():
    """Test API 1: Detect Decision"""
    url = f"{BASE_URL}/detect-decision"
    payload = {
        "message": "We decided to migrate to PostgreSQL because the schema is stable",
        "user": "priya@company.com",
        "channel_id": "tech-team"
    }
    
    response = requests.post(url, json=payload)
    print_response("API 1: Detect Decision", response)
    return response.json()

def test_save_decision():
    """Test API 2: Save Decision"""
    url = f"{BASE_URL}/save-decision"
    payload = {
        "title": "Database Migration to PostgreSQL",
        "owner": "Priya Kumar",
        "rationale": "Schema has stabilized and we need better support for complex joins",
        "due_date": "2025-12-31",
        "thread_link": "https://cliq.zoho.com/thread/12345",
        "participants": ["priya@company.com", "rahul@company.com"],
        "channel_id": "tech-team"
    }
    
    response = requests.post(url, json=payload)
    print_response("API 2: Save Decision", response)
    return response.json()

def test_query_decisions():
    """Test API 3: Query Decisions (RAG)"""
    url = f"{BASE_URL}/query-decisions"
    payload = {
        "query": "Why did we switch to PostgreSQL?",
        "user": "newdev@company.com"
    }
    
    response = requests.post(url, json=payload)
    print_response("API 3: Query Decisions (RAG)", response)
    return response.json()

def test_health_check():
    """Test health endpoint"""
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print_response("Health Check", response)
    return response.json()

def run_all_tests():
    """Run all API tests in sequence"""
    print("\n" + "🚀 " * 30)
    print("Starting TechAtlas API Tests")
    print("🚀 " * 30)
    
    try:
        # Test 0: Health check
        print("\n📍 Step 0: Testing server health...")
        test_health_check()
        
        # Test 1: Detect Decision
        print("\n📍 Step 1: Testing decision detection...")
        detect_result = test_detect_decision()
        
        # Test 2: Save Decision
        print("\n📍 Step 2: Testing decision save...")
        save_result = test_save_decision()
        
        # Wait a moment for indexing
        print("\n⏳ Waiting 2 seconds for vector indexing...")
        time.sleep(2)
        
        # Test 3: Query Decisions
        print("\n📍 Step 3: Testing RAG query...")
        query_result = test_query_decisions()
        
        print("\n" + "✅ " * 30)
        print("All tests completed successfully!")
        print("✅ " * 30 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server at", BASE_URL)
        print("Make sure the Flask app is running: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
