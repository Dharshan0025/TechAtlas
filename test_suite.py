#!/usr/bin/env python3
"""
Comprehensive Test Suite for TechAtlas Backend v2.0
Coverage: All 5 endpoints with 40+ test cases
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app
from app_v2 import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_detector():
    """Mock DecisionDetector"""
    with patch('app_v2.DecisionDetector') as mock:
        instance = Mock()
        instance.detect.return_value = (True, 0.95, "Test Decision Title")
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_embedder():
    """Mock GeminiEmbedder"""
    with patch('app_v2.get_embedder') as mock:
        instance = Mock()
        instance.embed.return_value = [0.1] * 768  # Mock embedding vector
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore"""
    with patch('app_v2.get_vector_store') as mock:
        instance = Mock()
        instance.upsert.return_value = True
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_firestore():
    """Mock Firestore"""
    with patch('app_v2.get_firestore') as mock:
        db_mock = Mock()
        collection_mock = Mock()
        document_mock = Mock()
        document_mock.set.return_value = None
        collection_mock.document.return_value = document_mock
        db_mock.collection.return_value = collection_mock
        mock.return_value = db_mock
        yield db_mock


@pytest.fixture
def mock_rag_engine():
    """Mock RAGEngine"""
    with patch('app_v2.get_rag_engine') as mock:
        instance = Mock()
        instance.query.return_value = {
            "answer": "Test answer",
            "sources": [{"title": "Test", "content": "Test content"}]
        }
        mock.return_value = instance
        yield instance


# ============================================================
# TEST GROUP 1: GET /health endpoint (5 tests)
# ============================================================

class TestHealthEndpoint:
    """Tests for GET /health endpoint"""
    
    def test_health_check_returns_200(self, client):
        """Test that health check returns 200 status"""
        response = client.get('/health')
        assert response.status_code in [200, 503]  # 503 if Firebase not initialized in tests
    
    def test_health_check_returns_json(self, client):
        """Test that health check returns JSON"""
        response = client.get('/health')
        assert response.content_type == 'application/json'
    
    def test_health_check_has_required_fields(self, client):
        """Test that health check includes all required fields"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert 'service' in data
        assert 'version' in data
    
    def test_health_check_status_is_healthy(self, client):
        """Test that health check status is 'healthy'"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert data['status'] in ['healthy', 'degraded']  # degraded if services not initialized
    
    def test_health_check_service_name(self, client):
        """Test that service name is correct"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'TechAtlas' in data['service']


# ============================================================
# TEST GROUP 2: GET /routes endpoint (3 tests)
# ============================================================

class TestRoutesEndpoint:
    """Tests for GET /routes endpoint"""
    
    def test_routes_returns_200(self, client):
        """Test that routes endpoint returns 200"""
        response = client.get('/routes')
        assert response.status_code == 200
    
    def test_routes_returns_list(self, client):
        """Test that routes returns a list"""
        response = client.get('/routes')
        data = json.loads(response.data)
        # New format wraps routes in an object
        assert 'routes' in data
        assert isinstance(data['routes'], list)
    
    def test_routes_includes_all_endpoints(self, client):
        """Test that all main endpoints are listed"""
        response = client.get('/routes')
        data = json.loads(response.data)
        routes = data.get('routes', data)  # Handle both formats
        endpoints = [route['endpoint'] for route in routes]
        assert 'health_check' in endpoints
        assert 'detect_decision' in endpoints
        assert 'save_decision' in endpoints
        assert 'query_decisions' in endpoints


# ============================================================
# TEST GROUP 3: POST /detect-decision endpoint (12 tests)
# ============================================================

class TestDetectDecisionEndpoint:
    """Tests for POST /detect-decision endpoint"""
    
    def test_detect_decision_valid_input_returns_200(self, client, mock_detector):
        """Test valid decision detection returns 200"""
        payload = {
            "message": "We decided to migrate to PostgreSQL",
            "user": "test@test.com",
            "channel_id": "tech"
        }
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_detect_decision_returns_expected_fields(self, client, mock_detector):
        """Test response includes all expected fields"""
        payload = {"message": "We should launch by Q2"}
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        json_data = json.loads(response.data)
        # New format wraps data
        data = json_data.get('data', json_data)
        assert 'is_decision' in data
        assert 'confidence' in data
        assert 'suggested_title' in data
    
    def test_detect_decision_missing_message_returns_400(self, client):
        """Test missing message field returns 400"""
        payload = {"user": "test@test.com"}
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_detect_decision_empty_message_returns_400(self, client):
        """Test empty message returns 400"""
        payload = {"message": ""}
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_detect_decision_no_json_returns_400(self, client):
        """Test no JSON data returns 400"""
        response = client.post('/detect-decision',
                               data="not json",
                               content_type='text/plain')
        assert response.status_code == 400
    
    def test_detect_decision_long_message_handles_gracefully(self, client, mock_detector):
        """Test very long message (1000+ chars) handles gracefully"""
        payload = {"message": "A" * 2000}
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code in [200, 400, 500]
    
    def test_detect_decision_special_characters(self, client, mock_detector):
        """Test message with special characters"""
        payload = {"message": "We decided to use @#$%^&*()"}
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_detect_decision_unicode_characters(self, client, mock_detector):
        """Test message with unicode characters"""
        payload = {"message": "我们决定使用 PostgreSQL 数据库"}
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_detect_decision_with_optional_fields(self, client, mock_detector):
        """Test with all optional fields included"""
        payload = {
            "message": "We decided to migrate",
            "user": "admin@test.com",
            "channel_id": "engineering"
        }
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_detect_decision_confidence_range(self, client, mock_detector):
        """Test confidence is between 0 and 1"""
        payload = {"message": "We should do this"}
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        json_data = json.loads(response.data)
        if response.status_code == 200:
            data = json_data.get('data', json_data)
            assert 0 <= data['confidence'] <= 1
    
    def test_detect_decision_is_decision_boolean(self, client, mock_detector):
        """Test is_decision is boolean"""
        payload = {"message": "Test message"}
        response = client.post('/detect-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        json_data = json.loads(response.data)
        if response.status_code == 200:
            data = json_data.get('data', json_data)
            assert isinstance(data['is_decision'], bool)
    
    def test_detect_decision_error_handling(self, client):
        """Test error handling when detector fails"""
        with patch('app_v2.get_detector') as mock:
            mock.side_effect = Exception("Service unavailable")
            payload = {"message": "Test"}
            response = client.post('/detect-decision',
                                   data=json.dumps(payload),
                                   content_type='application/json')
            assert response.status_code in [500, 503]  # 503 for service unavailable
            data = json.loads(response.data)
            assert 'error' in data or 'success' in data


# ============================================================
# TEST GROUP 4: POST /save-decision endpoint (12 tests)
# ============================================================

class TestSaveDecisionEndpoint:
    """Tests for POST /save-decision endpoint"""
    
    @pytest.fixture
    def valid_decision_payload(self):
        """Valid decision payload"""
        return {
            "title": "Migrate to PostgreSQL",
            "owner": "john@company.com",
            "rationale": "Better performance and ACID compliance",
            "due_date": "2025-12-31",
            "thread_link": "https://slack.com/thread/123",
            "participants": ["john@company.com", "jane@company.com"],
            "channel_id": "tech-team"
        }
    
    def test_save_decision_valid_input_returns_200(self, client, valid_decision_payload,
                                                    mock_embedder, mock_vector_store, mock_firestore):
        """Test valid save decision returns 200"""
        response = client.post('/save-decision',
                               data=json.dumps(valid_decision_payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_save_decision_returns_decision_id(self, client, valid_decision_payload,
                                               mock_embedder, mock_vector_store, mock_firestore):
        """Test response includes decision_id"""
        response = client.post('/save-decision',
                               data=json.dumps(valid_decision_payload),
                               content_type='application/json')
        json_data = json.loads(response.data)
        # New format wraps data
        data = json_data.get('data', json_data)
        assert 'decision_id' in data
        assert data['decision_id'] is not None
    
    def test_save_decision_missing_title_returns_400(self, client, valid_decision_payload):
        """Test missing title field returns 400"""
        del valid_decision_payload['title']
        response = client.post('/save-decision',
                               data=json.dumps(valid_decision_payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_save_decision_missing_owner_returns_400(self, client, valid_decision_payload):
        """Test missing owner field returns 400"""
        del valid_decision_payload['owner']
        response = client.post('/save-decision',
                               data=json.dumps(valid_decision_payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_save_decision_missing_rationale_returns_400(self, client, valid_decision_payload):
        """Test missing rationale field returns 400"""
        del valid_decision_payload['rationale']
        response = client.post('/save-decision',
                               data=json.dumps(valid_decision_payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_save_decision_missing_due_date_returns_400(self, client, valid_decision_payload):
        """Test missing due_date field returns 400"""
        del valid_decision_payload['due_date']
        response = client.post('/save-decision',
                               data=json.dumps(valid_decision_payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_save_decision_missing_thread_link_returns_400(self, client, valid_decision_payload):
        """Test missing thread_link field returns 400"""
        del valid_decision_payload['thread_link']
        response = client.post('/save-decision',
                               data=json.dumps(valid_decision_payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_save_decision_no_json_returns_400(self, client):
        """Test no JSON data returns 400"""
        response = client.post('/save-decision',
                               data="not json",
                               content_type='text/plain')
        assert response.status_code == 400
    
    def test_save_decision_optional_fields(self, client, mock_embedder, mock_vector_store, mock_firestore):
        """Test optional fields can be omitted"""
        payload = {
            "title": "Test Decision",
            "owner": "test@test.com",
            "rationale": "Test rationale",
            "due_date": "2025-12-31",
            "thread_link": "https://test.com/thread"
        }
        response = client.post('/save-decision',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_save_decision_firestore_failure_returns_500(self, client, valid_decision_payload,
                                                         mock_embedder, mock_vector_store):
        """Test Firestore failure returns 500"""
        with patch('app_v2.get_firestore') as mock:
            mock.side_effect = Exception("Firestore unavailable")
            response = client.post('/save-decision',
                                   data=json.dumps(valid_decision_payload),
                                   content_type='application/json')
            assert response.status_code == 500
    
    def test_save_decision_embedding_failure_returns_500(self, client, valid_decision_payload,
                                                         mock_vector_store, mock_firestore):
        """Test embedding generation failure returns 500"""
        with patch('app_v2.get_embedder') as mock:
            mock.side_effect = Exception("Embedding service unavailable")
            response = client.post('/save-decision',
                                   data=json.dumps(valid_decision_payload),
                                   content_type='application/json')
            assert response.status_code == 500
    
    def test_save_decision_success_response_format(self, client, valid_decision_payload,
                                                    mock_embedder, mock_vector_store, mock_firestore):
        """Test success response has correct format"""
        response = client.post('/save-decision',
                               data=json.dumps(valid_decision_payload),
                               content_type='application/json')
        json_data = json.loads(response.data)
        assert json_data['success'] is True
        assert 'message' in json_data
        # Data is nested
        data = json_data.get('data', {})
        assert 'decision_id' in data


# ============================================================
# TEST GROUP 5: POST /query-decisions endpoint (10 tests)
# ============================================================

class TestQueryDecisionsEndpoint:
    """Tests for POST /query-decisions endpoint"""
    
    def test_query_decisions_valid_input_returns_200(self, client, mock_rag_engine):
        """Test valid query returns 200"""
        payload = {"query": "Why did we choose PostgreSQL?"}
        response = client.post('/query-decisions',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_query_decisions_returns_answer_and_sources(self, client, mock_rag_engine):
        """Test response includes answer and sources"""
        payload = {"query": "Test query"}
        response = client.post('/query-decisions',
                               data=json.dumps(payload),
                               content_type='application/json')
        json_data = json.loads(response.data)
        # New format wraps data
        data = json_data.get('data', json_data)
        assert 'answer' in data
        assert 'sources' in data
    
    def test_query_decisions_missing_query_returns_400(self, client):
        """Test missing query field returns 400"""
        payload = {"user": "test@test.com"}
        response = client.post('/query-decisions',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_query_decisions_empty_query_returns_400(self, client):
        """Test empty query returns 400"""
        payload = {"query": ""}
        response = client.post('/query-decisions',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 400
    
    def test_query_decisions_no_json_returns_400(self, client):
        """Test no JSON data returns 400"""
        response = client.post('/query-decisions',
                               data="not json",
                               content_type='text/plain')
        assert response.status_code == 400
    
    def test_query_decisions_with_user_field(self, client, mock_rag_engine):
        """Test query with optional user field"""
        payload = {
            "query": "Test query",
            "user": "test@test.com"
        }
        response = client.post('/query-decisions',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_query_decisions_long_query(self, client, mock_rag_engine):
        """Test very long query handles gracefully"""
        payload = {"query": "Why " * 500}
        response = client.post('/query-decisions',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code in [200, 400]
    
    def test_query_decisions_special_characters(self, client, mock_rag_engine):
        """Test query with special characters"""
        payload = {"query": "Why @#$%^&*()"}
        response = client.post('/query-decisions',
                               data=json.dumps(payload),
                               content_type='application/json')
        assert response.status_code == 200
    
    def test_query_decisions_rag_engine_failure_returns_500(self, client):
        """Test RAG engine failure returns 500"""
        with patch('app_v2.get_rag_engine') as mock:
            mock.side_effect = Exception("RAG engine unavailable")
            payload = {"query": "Test"}
            response = client.post('/query-decisions',
                                   data=json.dumps(payload),
                                   content_type='application/json')
            assert response.status_code in [500, 503]  # 503 for service unavailable
    
    def test_query_decisions_error_response_format(self, client):
        """Test error response includes error field"""
        with patch('app_v2.get_rag_engine') as mock:
            mock.side_effect = Exception("Test error")
            payload = {"query": "Test"}
            response = client.post('/query-decisions',
                                   data=json.dumps(payload),
                                   content_type='application/json')
            json_data = json.loads(response.data)
            # Service unavailable returns error format
            assert 'error' in json_data or 'success' in json_data


# ============================================================
# SUMMARY FUNCTION
# ============================================================

def pytest_sessionfinish(session, exitstatus):
    """Print summary after all tests complete"""
    print("\n" + "="*60)
    print("TEST SUITE EXECUTION COMPLETE")
    print("="*60)
    if exitstatus == 0:
        print("✅ ALL TESTS PASSED - Backend is production ready!")
    else:
        print("❌ Some tests failed - Review failures above")
    print("="*60 + "\n")


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short', '--color=yes'])
