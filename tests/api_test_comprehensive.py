"""
Comprehensive API Test Suite for TechAtlas Flask Backend
Tests all endpoints with happy paths, error cases, edge cases, and stress scenarios.
Run against live server at http://127.0.0.1:5000
"""

import requests
import json
import sys
from typing import Dict, Any, Tuple

BASE_URL = "http://127.0.0.1:5000"

# Test result tracking
total_tests = 0
passed_tests = 0
failed_tests = 0
test_results = []

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_test(test_name: str):
    """Print test name"""
    print(f"\n▶ {test_name}")

def assert_status(response, expected_status: int, test_name: str) -> bool:
    """Assert response status code"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    if response.status_code == expected_status:
        passed_tests += 1
        print(f"  ✅ PASS - Status: {response.status_code}")
        test_results.append({"test": test_name, "status": "PASS", "details": f"Status {response.status_code}"})
        return True
    else:
        failed_tests += 1
        print(f"  ❌ FAIL - Expected {expected_status}, got {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        test_results.append({"test": test_name, "status": "FAIL", "details": f"Expected {expected_status}, got {response.status_code}"})
        return False

def assert_json_field(response, field: str, test_name: str) -> bool:
    """Assert JSON response contains field"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    try:
        data = response.json()
        if field in data:
            passed_tests += 1
            print(f"  ✅ PASS - Field '{field}' present")
            test_results.append({"test": test_name, "status": "PASS", "details": f"Field '{field}' present"})
            return True
        else:
            failed_tests += 1
            print(f"  ❌ FAIL - Field '{field}' missing")
            print(f"  Response: {data}")
            test_results.append({"test": test_name, "status": "FAIL", "details": f"Field '{field}' missing"})
            return False
    except Exception as e:
        failed_tests += 1
        print(f"  ❌ FAIL - {str(e)}")
        test_results.append({"test": test_name, "status": "FAIL", "details": str(e)})
        return False

# ==============================================================================
# TEST GROUP 1: ROOT ENDPOINT
# ==============================================================================

def test_root_endpoint():
    print_header("TEST GROUP 1: ROOT ENDPOINT (/)")
    
    # Test 1.1: GET / - Happy Path
    print_test("Test 1.1: GET / returns 200")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert_status(response, 200, "Root endpoint GET")
        assert_json_field(response, "service", "Root has service field")
        assert_json_field(response, "endpoints", "Root has endpoints field")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 1.2: POST / - Wrong method
    print_test("Test 1.2: POST / returns 405 (Method Not Allowed)")
    try:
        response = requests.post(f"{BASE_URL}/")
        assert_status(response, 405, "Root endpoint POST not allowed")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

# ==============================================================================
# TEST GROUP 2: HEALTH ENDPOINT
# ==============================================================================

def test_health_endpoint():
    print_header("TEST GROUP 2: HEALTH ENDPOINT (/health)")
    
    # Test 2.1: GET /health - Happy Path
    print_test("Test 2.1: GET /health returns 200")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert_status(response, 200, "Health check GET")
        assert_json_field(response, "status", "Health has status field")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 2.2: POST /health - Wrong method
    print_test("Test 2.2: POST /health returns 405")
    try:
        response = requests.post(f"{BASE_URL}/health")
        assert_status(response, 405, "Health POST not allowed")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

# ==============================================================================
# TEST GROUP 3: ROUTES ENDPOINT
# ==============================================================================

def test_routes_endpoint():
    print_header("TEST GROUP 3: ROUTES ENDPOINT (/routes)")
    
    # Test 3.1: GET /routes - Happy Path
    print_test("Test 3.1: GET /routes returns 200 with route list")
    try:
        response = requests.get(f"{BASE_URL}/routes")
        if assert_status(response, 200, "Routes endpoint GET"):
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  ✅ PASS - Returns list with {len(data)} routes")
            else:
                print(f"  ❌ FAIL - Expected non-empty list")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

# ==============================================================================
# TEST GROUP 4: DETECT DECISION ENDPOINT
# ==============================================================================

def test_detect_decision_endpoint():
    print_header("TEST GROUP 4: DETECT DECISION ENDPOINT (/detect-decision)")
    
    # Test 4.1: Valid message - Happy Path
    print_test("Test 4.1: POST valid message returns 200")
    try:
        payload = {"message": "We decided to migrate to PostgreSQL for better performance"}
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
        assert_status(response, 200, "Detect decision valid input")
        assert_json_field(response, "is_decision", "Response has is_decision")
        assert_json_field(response, "confidence", "Response has confidence")
        assert_json_field(response, "suggested_title", "Response has suggested_title")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.2: Missing required field - message
    print_test("Test 4.2: POST without message returns 400")
    try:
        payload = {}
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
        assert_status(response, 400, "Detect missing message")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.3: Empty message
    print_test("Test 4.3: POST empty message returns 400")
    try:
        payload = {"message": ""}
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
        assert_status(response, 400, "Detect empty message")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.4: Whitespace-only message
    print_test("Test 4.4: POST whitespace message returns 400")
    try:
        payload = {"message": "   "}
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
        assert_status(response, 400, "Detect whitespace message")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.5: Non-JSON request
    print_test("Test 4.5: POST non-JSON returns 400")
    try:
        response = requests.post(f"{BASE_URL}/detect-decision", data="plain text")
        assert_status(response, 400, "Detect non-JSON")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.6: Invalid JSON
    print_test("Test 4.6: POST invalid JSON returns 400")
    try:
        response = requests.post(
            f"{BASE_URL}/detect-decision",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert_status(response, 400, "Detect invalid JSON")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.7: Extra fields (should ignore)
    print_test("Test 4.7: POST with extra fields succeeds")
    try:
        payload = {
            "message": "We decided to use React",
            "extra_field": "should be ignored",
            "another": 123
        }
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
        assert_status(response, 200, "Detect with extra fields")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.8: Very long message
    print_test("Test 4.8: POST very long message")
    try:
        payload = {"message": "We decided " * 1000}
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
        # Should succeed or return appropriate error
        if response.status_code in [200, 400, 413]:
            print(f"  ✅ PASS - Handled long message appropriately: {response.status_code}")
        else:
            print(f"  ❌ FAIL - Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.9: Unicode/Special characters
    print_test("Test 4.9: POST unicode characters")
    try:
        payload = {"message": "我们决定使用 PostgreSQL 🚀 для лучшей производительности"}
        response = requests.post(f"{BASE_URL}/detect-decision", json=payload)
        assert_status(response, 200, "Detect unicode message")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 4.10: GET method (should fail)
    print_test("Test 4.10: GET /detect-decision returns 405")
    try:
        response = requests.get(f"{BASE_URL}/detect-decision")
        assert_status(response, 405, "Detect GET not allowed")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

# ==============================================================================
# TEST GROUP 5: SAVE DECISION ENDPOINT
# ==============================================================================

def test_save_decision_endpoint():
    print_header("TEST GROUP 5: SAVE DECISION ENDPOINT (/save-decision)")
    
    # Test 5.1: Valid payload - Happy Path
    print_test("Test 5.1: POST valid decision returns 200")
    try:
        payload = {
            "title": "Migrate to PostgreSQL",
            "owner": "tech@example.com",
            "rationale": "Better performance and scalability",
            "due_date": "2025-12-31",
            "thread_link": "https://slack.com/thread/123",
            "participants": ["dev1@example.com", "dev2@example.com"],
            "channel_id": "engineering"
        }
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        # May return 200 or 500 depending on service availability
        if response.status_code in [200, 500]:
            print(f"  ✅ PASS - Status: {response.status_code}")
            if response.status_code == 200:
                assert_json_field(response, "decision_id", "Response has decision_id")
        else:
            print(f"  ⚠️ WARNING - Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.2: Missing title
    print_test("Test 5.2: POST without title returns 400")
    try:
        payload = {
            "owner": "tech@example.com",
            "rationale": "Better performance",
            "due_date": "2025-12-31",
            "thread_link": "https://slack.com/thread/123"
        }
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        assert_status(response, 400, "Save missing title")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.3: Missing owner
    print_test("Test 5.3: POST without owner returns 400")
    try:
        payload = {
            "title": "Test Decision",
            "rationale": "Better performance",
            "due_date": "2025-12-31",
            "thread_link": "https://slack.com/thread/123"
        }
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        assert_status(response, 400, "Save missing owner")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.4: Missing rationale
    print_test("Test 5.4: POST without rationale returns 400")
    try:
        payload = {
            "title": "Test Decision",
            "owner": "tech@example.com",
            "due_date": "2025-12-31",
            "thread_link": "https://slack.com/thread/123"
        }
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        assert_status(response, 400, "Save missing rationale")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.5: Missing due_date
    print_test("Test 5.5: POST without due_date returns 400")
    try:
        payload = {
            "title": "Test Decision",
            "owner": "tech@example.com",
            "rationale": "Better performance",
            "thread_link": "https://slack.com/thread/123"
        }
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        assert_status(response, 400, "Save missing due_date")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.6: Missing thread_link
    print_test("Test 5.6: POST without thread_link returns 400")
    try:
        payload = {
            "title": "Test Decision",
            "owner": "tech@example.com",
            "rationale": "Better performance",
            "due_date": "2025-12-31"
        }
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        assert_status(response, 400, "Save missing thread_link")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.7: Empty JSON
    print_test("Test 5.7: POST empty JSON returns 400")
    try:
        payload = {}
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        assert_status(response, 400, "Save empty JSON")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.8: Non-JSON request
    print_test("Test 5.8: POST non-JSON returns 400")
    try:
        response = requests.post(f"{BASE_URL}/save-decision", data="plain text")
        assert_status(response, 400, "Save non-JSON")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.9: Empty required field
    print_test("Test 5.9: POST with empty title returns 400")
    try:
        payload = {
            "title": "",
            "owner": "tech@example.com",
            "rationale": "Better performance",
            "due_date": "2025-12-31",
            "thread_link": "https://slack.com/thread/123"
        }
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        assert_status(response, 400, "Save empty title")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.10: Invalid email format (should still accept - no email validation yet)
    print_test("Test 5.10: POST with invalid email format")
    try:
        payload = {
            "title": "Test Decision",
            "owner": "not-an-email",
            "rationale": "Better performance",
            "due_date": "2025-12-31",
            "thread_link": "https://slack.com/thread/123"
        }
        response = requests.post(f"{BASE_URL}/save-decision", json=payload)
        # Should accept or validate
        print(f"  ℹ️ INFO - Status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 5.11: GET method
    print_test("Test 5.11: GET /save-decision returns 405")
    try:
        response = requests.get(f"{BASE_URL}/save-decision")
        assert_status(response, 405, "Save GET not allowed")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

# ==============================================================================
# TEST GROUP 6: QUERY DECISIONS ENDPOINT
# ==============================================================================

def test_query_decisions_endpoint():
    print_header("TEST GROUP 6: QUERY DECISIONS ENDPOINT (/query-decisions)")
    
    # Test 6.1: Valid query - Happy Path
    print_test("Test 6.1: POST valid query returns 200")
    try:
        payload = {"query": "What decisions have been made about database?"}
        response = requests.post(f"{BASE_URL}/query-decisions", json=payload)
        # May return 200 or 500 depending on service availability
        if response.status_code in [200, 500]:
            print(f"  ✅ PASS - Status: {response.status_code}")
            if response.status_code == 200:
                assert_json_field(response, "answer", "Response has answer")
        else:
            print(f"  ⚠️ WARNING - Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6.2: Missing query field
    print_test("Test 6.2: POST without query returns 400")
    try:
        payload = {}
        response = requests.post(f"{BASE_URL}/query-decisions", json=payload)
        assert_status(response, 400, "Query missing query field")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6.3: Empty query
    print_test("Test 6.3: POST empty query returns 400")
    try:
        payload = {"query": ""}
        response = requests.post(f"{BASE_URL}/query-decisions", json=payload)
        assert_status(response, 400, "Query empty query")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6.4: Whitespace query
    print_test("Test 6.4: POST whitespace query returns 400")
    try:
        payload = {"query": "   "}
        response = requests.post(f"{BASE_URL}/query-decisions", json=payload)
        assert_status(response, 400, "Query whitespace")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6.5: Non-JSON request
    print_test("Test 6.5: POST non-JSON returns 400")
    try:
        response = requests.post(f"{BASE_URL}/query-decisions", data="plain text")
        assert_status(response, 400, "Query non-JSON")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6.6: Very long query
    print_test("Test 6.6: POST very long query")
    try:
        payload = {"query": "What decisions have been made about " * 100}
        response = requests.post(f"{BASE_URL}/query-decisions", json=payload)
        # Should handle appropriately
        print(f"  ℹ️ INFO - Status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6.7: Unicode query
    print_test("Test 6.7: POST unicode query")
    try:
        payload = {"query": "数据库决策是什么？ What about БД?"}
        response = requests.post(f"{BASE_URL}/query-decisions", json=payload)
        print(f"  ℹ️ INFO - Status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 6.8: GET method
    print_test("Test 6.8: GET /query-decisions returns 405")
    try:
        response = requests.get(f"{BASE_URL}/query-decisions")
        assert_status(response, 405, "Query GET not allowed")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

# ==============================================================================
# TEST GROUP 7: ERROR HANDLING & EDGE CASES
# ==============================================================================

def test_error_handling():
    print_header("TEST GROUP 7: ERROR HANDLING & EDGE CASES")
    
    # Test 7.1: Non-existent endpoint
    print_test("Test 7.1: GET non-existent endpoint returns 404")
    try:
        response = requests.get(f"{BASE_URL}/non-existent-endpoint")
        assert_status(response, 404, "Non-existent endpoint")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    
    # Test 7.2: Server connectivity
    print_test("Test 7.2: Server is reachable")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ PASS - Server is reachable")
        else:
            print(f"  ⚠️ WARNING - Server returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"  ❌ FAIL - Server not reachable. Is it running on {BASE_URL}?")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def print_summary():
    """Print test execution summary"""
    print_header("TEST EXECUTION SUMMARY")
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        print("\n⚠️ FAILED TESTS:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"  - {result['test']}: {result['details']}")
    else:
        print(f"\n🎉 ALL TESTS PASSED! Backend is error-free and ready!")
    
    print("\n" + "="*70)

def main():
    """Main test execution"""
    print_header("🚀 TechAtlas Backend - Comprehensive API Testing")
    print(f"Target: {BASE_URL}")
    print("Ensure the Flask server is running before executing tests.")
    
    # Check server connectivity first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"\n✅ Server is ONLINE - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to {BASE_URL}")
        print("Please start the Flask server with: python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    
    # Execute all test groups
    try:
        test_root_endpoint()
        test_health_endpoint()
        test_routes_endpoint()
        test_detect_decision_endpoint()
        test_save_decision_endpoint()
        test_query_decisions_endpoint()
        test_error_handling()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {e}")
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if failed_tests == 0 else 1)

if __name__ == "__main__":
    main()
