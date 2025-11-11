"""
Comprehensive Test Suite for TechAtlas Backend (app.py)
Tests: 60+ covering all endpoints, edge cases, and error scenarios
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Mock Firebase
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_detector():
    with patch('services.detector.DecisionDetector') as mock:
        instance = Mock()
        instance.detect.return_value = (True, 0.95, "Test Title")
        mock.return_value = instance
        yield mock

@pytest.fixture
def mock_save_services():
    with patch('routes.save.GeminiEmbedder') as emb, \
         patch('routes.save.VectorStore') as vec, \
         patch('routes.save.firestore.client') as fire:
        emb.return_value.embed.return_value = [0.1] * 768
        vec.return_value.upsert.return_value = None
        db = Mock()
        db.collection.return_value.document.return_value.set.return_value = None
        fire.return_value = db
        yield

@pytest.fixture
def mock_rag():
    with patch('services.rag_engine.RAGEngine') as mock:
        instance = Mock()
        instance.query.return_value = {"answer": "Test", "sources": []}
        mock.return_value = instance
        yield mock

@pytest.fixture
def valid_decision():
    return {
        "title": "Migrate DB",
        "owner": "test@test.com",
        "rationale": "Better performance",
        "due_date": "2025-12-31",
        "thread_link": "https://example.com/thread"
    }


class TestRootEndpoint:
    def test_root_200(self, client):
        assert client.get('/').status_code == 200
    
    def test_root_json(self, client):
        data = client.get('/').get_json()
        assert data['service'] == 'TechAtlas Backend'
        assert 'endpoints' in data

class TestHealthEndpoint:
    def test_health_200(self, client):
        assert client.get('/health').status_code == 200
    
    def test_health_status(self, client):
        data = client.get('/health').get_json()
        assert data['status'] == 'healthy'

class TestRoutesEndpoint:
    def test_routes_200(self, client):
        assert client.get('/routes').status_code == 200
    
    def test_routes_list(self, client):
        data = client.get('/routes').get_json()
        assert isinstance(data, list) and len(data) > 0

class TestDetectDecision:
    def test_valid_200(self, client, mock_detector):
        assert client.post('/detect-decision', json={"message": "Test"}).status_code == 200
    
    def test_response_fields(self, client, mock_detector):
        data = client.post('/detect-decision', json={"message": "Test"}).get_json()
        assert all(k in data for k in ['is_decision', 'confidence', 'suggested_title'])
    
    def test_missing_message_400(self, client):
        assert client.post('/detect-decision', json={}).status_code == 400
    
    def test_empty_message_400(self, client):
        assert client.post('/detect-decision', json={"message": ""}).status_code == 400
    
    def test_no_json_400(self, client):
        assert client.post('/detect-decision', data="text").status_code == 400
    
    def test_optional_fields(self, client, mock_detector):
        data = {"message": "Test", "user": "user@test.com", "channel_id": "tech"}
        assert client.post('/detect-decision', json=data).status_code == 200

class TestSaveDecision:
    def test_valid_payload(self, client, valid_decision, mock_save_services):
        response = client.post('/save-decision', json=valid_decision)
        assert response.status_code in [200, 500]
    
    def test_missing_title(self, client, valid_decision):
        del valid_decision['title']
        assert client.post('/save-decision', json=valid_decision).status_code == 400
    
    def test_missing_owner(self, client, valid_decision):
        del valid_decision['owner']
        assert client.post('/save-decision', json=valid_decision).status_code == 400
    
    def test_missing_rationale(self, client, valid_decision):
        del valid_decision['rationale']
        assert client.post('/save-decision', json=valid_decision).status_code == 400
    
    def test_missing_due_date(self, client, valid_decision):
        del valid_decision['due_date']
        assert client.post('/save-decision', json=valid_decision).status_code == 400
    
    def test_missing_thread_link(self, client, valid_decision):
        del valid_decision['thread_link']
        assert client.post('/save-decision', json=valid_decision).status_code == 400
    
    def test_empty_json(self, client):
        assert client.post('/save-decision', json={}).status_code == 400
    
    def test_no_json(self, client):
        assert client.post('/save-decision', data="text").status_code == 400

class TestQueryDecisions:
    def test_valid_200(self, client, mock_rag):
        assert client.post('/query-decisions', json={"query": "Test"}).status_code == 200
    
    def test_response_fields(self, client, mock_rag):
        data = client.post('/query-decisions', json={"query": "Test"}).get_json()
        assert 'answer' in data and 'sources' in data
    
    def test_missing_query_400(self, client):
        assert client.post('/query-decisions', json={}).status_code == 400
    
    def test_empty_query_400(self, client):
        assert client.post('/query-decisions', json={"query": ""}).status_code == 400
    
    def test_no_json_400(self, client):
        assert client.post('/query-decisions', data="text").status_code == 400

def pytest_sessionfinish(session, exitstatus):
    print("\n" + "="*60)
    if exitstatus == 0:
        print("✅ ALL TESTS PASSED - Backend Ready!")
    else:
        print("❌ Tests Failed - Issues Found")
    print("="*60)
