#!/usr/bin/env python3
"""
Comprehensive TechAtlas Backend Testing Script
Tests each component individually to isolate issues
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:5000"

def print_header(title):
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def test_component(name, test_func):
    """Test a component and report results"""
    print_header(f"Testing {name}")
    try:
        result = test_func()
        if result:
            print_success(f"{name} PASSED")
            return True
        else:
            print_error(f"{name} FAILED")
            return False
    except Exception as e:
        print_error(f"{name} ERROR: {str(e)}")
        return False

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'healthy':
            print_success(f"Health check: {data}")
            return True
    print_error(f"Health check failed: {response.status_code}")
    return False

def test_firebase_connection():
    """Test Firebase connection by trying to save a decision"""
    payload = {
        "title": "Test Decision - Firebase Connection",
        "owner": "Test User",
        "rationale": "Testing Firebase connectivity",
        "due_date": "2025-12-31",
        "thread_link": "https://test.com/thread/123",
        "participants": ["test@example.com"],
        "channel_id": "test-channel"
    }

    try:
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('decision_id'):
                print_success(f"Firebase connection works. Decision ID: {data['decision_id']}")
                return data['decision_id']
        else:
            print_error(f"Firebase save failed: {response.status_code}")
            print_error(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Firebase connection error: {e}")
    return False

def test_faiss_storage():
    """Test FAISS vector storage by checking if data directory exists"""
    import os
    data_dir = "data"
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        if 'faiss_index.bin' in files and 'metadata.pkl' in files:
            print_success(f"FAISS storage exists: {files}")
            return True
    print_error("FAISS storage not found")
    return False

def test_gemini_embedding():
    """Test Gemini embedding generation"""
    try:
        from services.embedder import GeminiEmbedder
        embedder = GeminiEmbedder()

        # Test embedding generation
        test_text = "This is a test decision"
        embedding = embedder.embed(test_text)

        if isinstance(embedding, list) and len(embedding) > 0:
            print_success(f"Gemini embedding works: {len(embedding)} dimensions")
            return True
        else:
            print_error("Gemini embedding failed: invalid response")
    except Exception as e:
        print_error(f"Gemini embedding error: {e}")
        import traceback
        traceback.print_exc()
    return False

def test_vector_store():
    """Test vector store operations"""
    try:
        from services.vector_store import VectorStore
        store = VectorStore()

        # Test basic operations
        count = store.index.ntotal
        print_success(f"Vector store loaded: {count} vectors")
        return True
    except Exception as e:
        print_error(f"Vector store error: {e}")
        import traceback
        traceback.print_exc()
    return False

def test_detect_decision():
    """Test decision detection"""
    payload = {
        "message": "We decided to migrate to PostgreSQL because the schema is stable",
        "user": "priya@company.com",
        "channel_id": "tech-team"
    }

    try:
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
        if response.status_code == 200:
            data = response.json()
            if 'is_decision' in data and 'confidence' in data:
                print_success(f"Decision detection works: {data}")
                return True
        print_error(f"Decision detection failed: {response.status_code}")
        print_error(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Decision detection error: {e}")
    return False

def test_query_decisions():
    """Test RAG query system"""
    payload = {
        "query": "Why did we switch to PostgreSQL?",
        "user": "newdev@company.com"
    }

    try:
        response = requests.post(f"{BASE_URL}/query-decisions", json=payload)
        if response.status_code == 200:
            data = response.json()
            if 'answer' in data and 'sources' in data:
                print_success("Query system works!")
                print(f"Answer: {data['answer'][:100]}...")
                print(f"Sources: {len(data['sources'])} found")
                return True
        elif response.status_code == 500:
            print_error("Query system failed with 500 error")
            print_error(f"Response: {response.text}")
            # Try to get more details from server logs
            print_warning("Check server logs for detailed error")
        else:
            print_error(f"Query system failed: {response.status_code}")
            print_error(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Query system error: {e}")
        import traceback
        traceback.print_exc()
    return False

def test_full_pipeline():
    """Test the complete pipeline"""
    print_header("Testing Complete Pipeline")

    # 1. Detect decision
    print("Step 1: Detect decision...")
    if not test_detect_decision():
        return False

    # 2. Save decision
    print("Step 2: Save decision...")
    decision_id = test_firebase_connection()
    if not decision_id:
        return False

    # Wait for indexing
    print("Step 3: Wait for vector indexing...")
    time.sleep(3)

    # 3. Query decisions
    print("Step 4: Query decisions...")
    if not test_query_decisions():
        return False

    return True

def main():
    """Run all tests"""
    print("🚀 TechAtlas Backend Comprehensive Testing Suite")
    print("=" * 60)

    results = {}

    # Test basic components first
    results['health'] = test_component("Health Check", test_health)
    results['faiss'] = test_component("FAISS Storage", test_faiss_storage)
    results['firebase'] = test_component("Firebase Connection", lambda: test_firebase_connection() is not False)
    results['gemini'] = test_component("Gemini Embedding", test_gemini_embedding)
    results['vector_store'] = test_component("Vector Store", test_vector_store)

    # Test API endpoints
    results['detect'] = test_component("Detect Decision API", test_detect_decision)
    results['save'] = test_component("Save Decision API", lambda: test_firebase_connection() is not False)
    results['query'] = test_component("Query Decisions API", test_query_decisions)

    # Test full pipeline
    results['pipeline'] = test_component("Complete Pipeline", test_full_pipeline)

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(results.values())
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print_success("🎉 ALL TESTS PASSED! System is fully functional!")
    else:
        print_warning("⚠️  Some tests failed. Check output above for details.")

        print("\nFailed components:")
        for name, result in results.items():
            if not result:
                print(f"  - {name}")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
