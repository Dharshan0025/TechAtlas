#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST SUITE
Tests TechAtlas Backend against exact API specifications
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:5000"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"🧪 {text}")
    print(f"{'='*60}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def test_endpoint(name, method, url, payload=None, expected_keys=None):
    """Test an endpoint and validate response"""
    print_header(f"Testing {name}")

    try:
        if method == 'GET':
            response = requests.get(url, timeout=30)
        elif method == 'POST':
            response = requests.post(url, json=payload, timeout=30)
        else:
            print_error(f"Unsupported method: {method}")
            return False

        print(f"Method: {method}")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print_error(f"Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False

        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            # Validate expected keys
            if expected_keys:
                missing_keys = []
                for key in expected_keys:
                    if key not in data:
                        missing_keys.append(key)

                if missing_keys:
                    print_error(f"Missing required keys: {missing_keys}")
                    return False
                else:
                    print_success("Response format correct")

            return data

        except json.JSONDecodeError:
            print_error("Invalid JSON response")
            print(f"Raw response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def main():
    """Run comprehensive API tests"""
    print("🚀 TechAtlas Backend - FINAL COMPREHENSIVE TEST SUITE")
    print("Testing against exact API specifications")
    print("="*70)

    results = {}

    # Test 1: Health Check
    health_data = test_endpoint("Health Check", "GET", f"{BASE_URL}/health")
    results['health'] = health_data and health_data.get('status') == 'healthy'

    # Test 2: Detect Decision (API 1) - Exact Specification
    print_header("API 1: Detect Decision - EXACT SPECIFICATION TEST")

    payload1 = {
        "message": "We decided to migrate to PostgreSQL because the schema is stable",
        "user": "priya@company.com",
        "channel_id": "tech-team"
    }

    detect_data = test_endpoint(
        "Detect Decision",
        "POST",
        f"{BASE_URL}/detect-decision",
        payload1,
        ["is_decision", "confidence", "suggested_title"]
    )

    results['detect'] = detect_data is not False

    if detect_data:
        # Validate data types
        if not isinstance(detect_data.get('is_decision'), bool):
            print_error("is_decision should be boolean")
            results['detect'] = False
        elif not isinstance(detect_data.get('confidence'), (int, float)):
            print_error("confidence should be number")
            results['detect'] = False
        elif not isinstance(detect_data.get('suggested_title'), str):
            print_error("suggested_title should be string")
            results['detect'] = False
        else:
            print_success("Data types correct")

    # Test 3: Save Decision (API 2) - Exact Specification
    print_header("API 2: Save Decision - EXACT SPECIFICATION TEST")

    payload2 = {
        "title": "Database Migration to PostgreSQL",
        "owner": "Priya Kumar",
        "rationale": "Schema has stabilized and we need better support for complex joins",
        "due_date": "2025-12-31",
        "thread_link": "https://cliq.zoho.com/thread/12345",
        "participants": ["priya@company.com", "rahul@company.com"],
        "channel_id": "tech-team"
    }

    save_data = test_endpoint(
        "Save Decision",
        "POST",
        f"{BASE_URL}/save-decision",
        payload2,
        ["success", "decision_id", "message"]
    )

    results['save'] = save_data and save_data.get('success') and save_data.get('decision_id')

    if save_data and save_data.get('success'):
        print_success("Decision saved successfully")
        decision_id = save_data.get('decision_id')
        print(f"Decision ID: {decision_id}")

        # Wait for vector indexing
        print("⏳ Waiting 3 seconds for vector indexing...")
        time.sleep(3)
    else:
        decision_id = None

    # Test 4: Query Decisions (API 3) - Exact Specification
    print_header("API 3: Query Decisions - EXACT SPECIFICATION TEST")

    payload3 = {
        "query": "Why did we switch to PostgreSQL?",
        "user": "newdev@company.com"
    }

    query_data = test_endpoint(
        "Query Decisions",
        "POST",
        f"{BASE_URL}/query-decisions",
        payload3,
        ["answer", "sources"]
    )

    results['query'] = query_data is not False

    if query_data:
        sources = query_data.get('sources', [])
        if isinstance(sources, list):
            print_success(f"Found {len(sources)} relevant sources")
            if len(sources) > 0:
                source = sources[0]
                source_keys = ['decision_id', 'title', 'owner', 'thread_link', 'relevance_score']
                missing = [k for k in source_keys if k not in source]
                if missing:
                    print_error(f"Source missing keys: {missing}")
                    results['query'] = False
                else:
                    print_success("Source format correct")
        else:
            print_error("sources should be a list")
            results['query'] = False

    # Test Additional Scenarios
    print_header("Additional Validation Tests")

    # Test non-decision detection
    print("Testing non-decision message...")
    non_decision_payload = {
        "message": "Hey team, how is everyone doing today?",
        "user": "john@company.com",
        "channel_id": "general"
    }

    non_detect = test_endpoint(
        "Non-Decision Detection",
        "POST",
        f"{BASE_URL}/detect-decision",
        non_decision_payload
    )

    if non_detect and non_detect.get('is_decision') == False:
        print_success("Non-decision correctly identified")
        results['non_decision'] = True
    else:
        print_error("Non-decision detection failed")
        results['non_decision'] = False

    # Test empty query rejection
    print("Testing empty query handling...")
    empty_query = test_endpoint(
        "Empty Query",
        "POST",
        f"{BASE_URL}/query-decisions",
        {"query": ""},
        None  # Expect 400 status
    )

    if empty_query is False:  # Should fail with 400
        print_success("Empty query properly rejected")
        results['empty_query'] = True
    else:
        print_error("Empty query not rejected")
        results['empty_query'] = False

    # Final Results
    print_header("FINAL TEST RESULTS SUMMARY")
    print("="*70)

    all_tests = ['health', 'detect', 'save', 'query', 'non_decision', 'empty_query']
    passed = 0
    total = len(all_tests)

    for test in all_tests:
        result = results.get(test, False)
        status = "✅ PASS" if result else "❌ FAIL"
        print("25")
        if result:
            passed += 1

    print(f"\n📊 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ TechAtlas Backend is fully functional!")
        print("\n📋 API Endpoints Working:")
        print("   • GET  /health - Health check")
        print("   • POST /detect-decision - Decision detection")
        print("   • POST /save-decision - Decision storage & vectorization")
        print("   • POST /query-decisions - RAG-powered decision search")
        print("\n🚀 Ready for production!")
        return True
    else:
        failed_tests = [t for t in all_tests if not results.get(t, False)]
        print(f"\n❌ {total - passed} test(s) failed: {', '.join(failed_tests)}")
        print("Check the output above for details.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        input("\nPress Enter to exit...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
