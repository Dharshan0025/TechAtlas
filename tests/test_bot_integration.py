import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from routes.analyze import analyze_bp
import json

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(analyze_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@patch('routes.analyze.get_feasibility_analyzer')
@patch('routes.analyze.get_vector_store')
@patch('routes.analyze.get_embedder')
@patch('firebase_admin.firestore.client')
def test_analyze_saved_decision(mock_firestore, mock_get_embedder, mock_get_vector_store, mock_get_analyzer, client):
    # Mock Firestore
    mock_db = MagicMock()
    mock_firestore.return_value = mock_db
    
    # Mock Decision Document
    mock_doc_ref = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "title": "Use Redis",
        "rationale": "We need speed",
        "decision_id": "dec_123"
    }
    mock_db.collection.return_value.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value = mock_doc
    
    # Mock Embedder
    mock_embedder = MagicMock()
    mock_get_embedder.return_value = mock_embedder
    mock_embedder.embed.return_value = [0.1, 0.2]
    
    # Mock Vector Store
    mock_vector_store = MagicMock()
    mock_get_vector_store.return_value = mock_vector_store
    mock_vector_store.query.return_value = []
    
    # Mock Analyzer
    mock_analyzer = MagicMock()
    mock_get_analyzer.return_value = mock_analyzer
    mock_analyzer.analyze_with_history.return_value = {
        "feasibility_score": 85,
        "risk_level": "Low",
        "recommendation": "Go ahead"
    }
    
    # Make Request
    response = client.post('/decisions/dec_123/analyze')
    
    # Verify
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['analysis']['feasibility_score'] == 85
    
    # Verify Firestore Update
    mock_doc_ref.update.assert_called_once()
