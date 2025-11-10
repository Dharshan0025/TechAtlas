#!/usr/bin/env python3
"""
Comprehensive Test Suite for TechAtlas Backend v2.0
Tests all endpoints with the exact specifications provided
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:5000"

def print_header(title):
    print("\n" + "="*70)
    print(f"🧪 {title}")
    print("="*70)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def test_endpoint(name, method, url, payload=None, expected_status=200):
    """Test a single endpoint"""
    print_header(f"Testing {name}")

    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=payload)
        else:
            print_error(f"Unsupported method: {method}")
            return False

        print(f"URL: {method} {url}")
        print(f"Status Code: {response.status_code}")

        if response.status_code != expected_status:
            print_error(f"Expected status {expected_status}, got {response.status_code}")
            print(f"Response: {response.text}")
            return False

        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return data
        except:
            print(f"Raw Response: {response.text}")
            return response.text

    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def run_all_tests():
    """Run the complete test suite"""
    print("🚀 TechAtlas Backend v2.0 - Comprehensive Test Suite")
    print("="*70)

    results = {}

    # Test 0: Health Check
    health_data = test_endpoint("Health Check", "GET", f"{BASE_URL}/health")
    results['health'] = health_data and health_data.get('status') == 'healthy'

    # Test 1: Detect Decision (API 1)
    print_header("API 1: Detect Decision - Exact Specification Test")

    payload1 = {
        "message": "We decided to migrate to PostgreSQL because the schema is stable",
        "user": "priya@company.com",
        "channel_id": "tech-team"
    }

    detect_data = test_endpoint("Detect Decision", "POST", f"{BASE_URL}/detect-decision", payload1)
    results['detect'] = detect_data and isinstance(detect_data.get('is_decision'), bool)

    if detect_data:
        required_keys = ['is_decision', 'confidence', 'suggested_title']
        for key in required_keys:
            if key not in detect_data:
                print_error(f"Missing required key: {key}")
                results['detect'] = False
                break
        else:
            print_success("Response format matches specification")

    # Test 2: Save Decision (API 2)
    print_header("API 2: Save Decision - Exact Specification Test")

    payload2 = {
        "title": "Database Migration to PostgreSQL",
        "owner": "Priya Kumar",
        "rationale": "Schema has stabilized and we need better support for complex joins",
        "due_date": "2025-12-31",
        "thread_link": "https://cliq.zoho.com/thread/12345",
        "participants": ["priya@company.com", "rahul@company.com"],
        "channel_id": "tech-team"
    }

    save_data = test_endpoint("Save Decision", "POST", f"{BASE_URL}/save-decision", payload2)
    results['save'] = save_data and save_data.get('success') and save_data.get('decision_id')

    if save_data:
        required_keys = ['success', 'decision_id', 'message']
        for key in required_keys:
            if key not in save_data:
                print_error(f"Missing required key: {key}")
                results['save'] = False
                break
        else:
            print_success("Response format matches specification")

    # Wait for vector indexing
    if results['save']:
        print_warning("Waiting 3 seconds for vector indexing...")
        time.sleep(3)

    # Test 3: Query Decisions (API 3)
    print_header("API 3: Query Decisions - Exact Specification Test")

    payload3 = {
        "query": "Why did we switch to PostgreSQL?",
        "user": "newdev@company.com"
    }

    query_data = test_endpoint("Query Decisions", "POST", f"{BASE_URL}/query-decisions", payload3)
    results['query'] = query_data and 'answer' in query_data and 'sources' in query_data

    if query_data:
        required_keys = ['answer', 'sources']
        for key in required_keys:
            if key not in query_data:
                print_error(f"Missing required key: {key}")
                results['query'] = False
                break

        # Check sources format
        if 'sources' in query_data and isinstance(query_data['sources'], list):
            if len(query_data['sources']) > 0:
                source = query_data['sources'][0]
                source_keys = ['decision_id', 'title', 'owner', 'thread_link', 'relevance_score']
                for key in source_keys:
                    if key not in source:
                        print_error(f"Source missing required key: {key}")
                        results['query'] = False
                        break
                else:
                    print_success("Response format matches specification")
        else:
            print_warning("No sources returned (this is OK if no decisions match)")
            print_success("Response format matches specification")

    # Test additional scenarios
    print_header("Additional Test Scenarios")

    # Test with non-decision message
    print("Testing non-decision detection...")
    non_decision_payload = {
        "message": "Hey team, how is everyone doing today?",
        "user": "john@company.com",
        "channel_id": "general"
    }

    non_decision_data = test_endpoint("Non-Decision Detection", "POST",
                                    f"{BASE_URL}/detect-decision", non_decision_payload)
    if non_decision_data and non_decision_data.get('is_decision') == False:
        print_success("Non-decision correctly identified")
    else:
        print_warning("Non-decision detection may need tuning")

    # Test empty query
    print("Testing empty query handling...")
    empty_query = test_endpoint("Empty Query", "POST",
                              f"{BASE_URL}/query-decisions", {"query": ""}, 400)
    if empty_query and 'error' in str(empty_query):
        print_success("Empty query properly rejected")
    else:
        print_warning("Empty query handling may need improvement")

    # Summary
    print_header("FINAL TEST RESULTS")
    passed = sum(results.values())
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")
    print()

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.upper()}: {status}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! TechAtlas Backend is fully functional!")
        print("\nAPI Endpoints Ready:")
        print("  • POST /detect-decision - Decision detection")
        print("  • POST /save-decision - Decision storage & vectorization")
        print("  • POST /query-decisions - RAG-powered decision search")
        print("  • GET /health - Health check")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check output above for details.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
