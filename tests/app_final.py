#!/usr/bin/env python3
"""
TechAtlas Backend - Final Working Version
Minimal Flask app with all endpoints working
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from services.detector import DecisionDetector
from services.embedder import GeminiEmbedder
from services.vector_store import VectorStore
from services.rag_engine import RAGEngine
from models.decision import Decision
from config import Config
import traceback
import json

app = Flask(__name__)
CORS(app)

print("🔧 Initializing TechAtlas Backend...")

# Initialize Firebase
try:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    print("✅ Firebase initialized")
except Exception as e:
    print(f"❌ Firebase error: {e}")
    exit(1)

print("✅ Backend ready")

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "TechAtlas Backend is running", "version": "3.0"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "TechAtlas Backend",
        "endpoints": [
            "GET /health",
            "POST /detect-decision",
            "POST /save-decision",
            "POST /query-decisions"
        ]
    })

@app.route('/detect-decision', methods=['POST'])
def detect_decision():
    """API 1: Detect Decision"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON provided"}), 400

        message = data.get('message', '').strip()
        if not message:
            return jsonify({"error": "Message required"}), 400

        print(f"🔍 Processing: {message[:50]}...")

        # Create detector and detect
        detector = DecisionDetector()
        is_decision, confidence, title = detector.detect(message)

        result = {
            "is_decision": is_decision,
            "confidence": round(confidence, 2),
            "suggested_title": title
        }

        print(f"✅ Result: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Detect error: {e}")
        return jsonify({
            "is_decision": False,
            "confidence": 0.0,
            "suggested_title": "",
            "error": str(e)
        }), 500

@app.route('/save-decision', methods=['POST'])
def save_decision():
    """API 2: Save Decision"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON provided"}), 400

        required = ['title', 'owner', 'rationale', 'due_date', 'thread_link']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing {field}"}), 400

        print(f"💾 Saving: {data['title']}")

        # Create decision
        decision = Decision(
            title=data['title'],
            owner=data['owner'],
            rationale=data['rationale'],
            due_date=data['due_date'],
            thread_link=data['thread_link'],
            participants=data.get('participants', []),
            channel_id=data.get('channel_id', '')
        )

        # Generate embedding
        embedder = GeminiEmbedder()
        embedding_text = decision.get_embedding_text()
        embedding = embedder.embed(embedding_text)

        # Store in vector DB
        vector_store = VectorStore()
        vector_store.upsert(
            decision_id=decision.decision_id,
            embedding=embedding,
            metadata=decision.to_dict()
        )

        # Store in Firestore
        db = firestore.client()
        db.collection('decisions').document(decision.decision_id).set(decision.to_dict())

        result = {
            "success": True,
            "decision_id": decision.decision_id,
            "message": "Decision saved successfully"
        }

        print(f"✅ Saved: {decision.decision_id}")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Save error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/query-decisions', methods=['POST'])
def query_decisions():
    """API 3: Query Decisions (RAG)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON provided"}), 400

        user_query = data.get('query', '').strip()
        if not user_query:
            return jsonify({"error": "Query required"}), 400

        print(f"🔎 Querying: {user_query}")

        # Perform RAG query
        rag_engine = RAGEngine()
        result = rag_engine.query(user_query)

        print("✅ Query completed")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Query error: {e}")
        return jsonify({
            "answer": "Error processing query",
            "sources": [],
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting TechAtlas Backend v3.0")
    print("🌐 Server: http://127.0.0.1:5000")
    print("📋 Endpoints:")
    print("   GET  /health")
    print("   POST /detect-decision")
    print("   POST /save-decision")
    print("   POST /query-decisions")
    print()

    app.run(host='0.0.0.0', port=Config.PORT, debug=True)
