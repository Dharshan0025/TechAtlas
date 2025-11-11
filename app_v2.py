#!/usr/bin/env python3
"""
TechAtlas Backend - Complete Rewrite
A simplified Flask application without blueprints for reliability
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
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global service instances (initialized on first use)
detector = None
embedder = None
vector_store = None
rag_engine = None
db = None

def get_detector():
    global detector
    if detector is None:
        detector = DecisionDetector()
    return detector

def get_embedder():
    global embedder
    if embedder is None:
        embedder = GeminiEmbedder()
    return embedder

def get_vector_store():
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store

def get_rag_engine():
    global rag_engine
    if rag_engine is None:
        rag_engine = RAGEngine()
    return rag_engine

def get_firestore():
    return firestore.client()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "TechAtlas Backend",
        "version": "2.0"
    })

@app.route('/detect-decision', methods=['POST'])
def detect_decision():
    """API 1: Detect Decision"""
    with open('debug.log', 'a') as f:
        f.write("=== DETECT_DECISION START ===\n")

    try:
        data = request.get_json()
        with open('debug.log', 'a') as f:
            f.write(f"Request data: {data}\n")

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        message = data.get('message', '')
        user = data.get('user', 'unknown')
        channel_id = data.get('channel_id', 'unknown')

        if not message:
            return jsonify({"error": "Message is required"}), 400

        with open('debug.log', 'a') as f:
            f.write(f"Message: {message[:50]}...\n")
            f.write("Creating DecisionDetector...\n")

        # Create detector instance directly
        detector = DecisionDetector()
        with open('debug.log', 'a') as f:
            f.write("DecisionDetector created, calling detect()...\n")

        is_decision, confidence, title = detector.detect(message)

        with open('debug.log', 'a') as f:
            f.write(f"Detection result: {is_decision}, {confidence}, {title}\n")

        result = {
            "is_decision": is_decision,
            "confidence": confidence,
            "suggested_title": title
        }

        with open('debug.log', 'a') as f:
            f.write(f"Returning result: {result}\n")
            f.write("=== DETECT_DECISION END ===\n")

        return jsonify(result)

    except Exception as e:
        with open('debug.log', 'a') as f:
            f.write(f"ERROR: {str(e)}\n")
            f.write(f"Traceback: {traceback.format_exc()}\n")
            f.write("=== DETECT_DECISION ERROR ===\n")

        print(f"❌ Error in detect_decision: {e}")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "is_decision": False,
            "confidence": 0.0,
            "suggested_title": ""
        }), 500

@app.route('/save-decision', methods=['POST'])
def save_decision():
    """API 2: Save Decision"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['title', 'owner', 'rationale', 'due_date', 'thread_link']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        print(f"💾 Saving decision: {data['title']}")

        # Create decision object
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
        embedder = get_embedder()
        embedding_text = decision.get_embedding_text()
        embedding = embedder.embed(embedding_text)

        # Store in vector database
        vector_store = get_vector_store()
        vector_store.upsert(
            decision_id=decision.decision_id,
            embedding=embedding,
            metadata=decision.to_dict()
        )

        # Store in Firestore
        firestore_db = get_firestore()
        firestore_db.collection('decisions').document(decision.decision_id).set(decision.to_dict())

        result = {
            "success": True,
            "decision_id": decision.decision_id,
            "message": "Decision saved and vectorized successfully"
        }

        print(f"✅ Decision saved: {decision.decision_id}")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Error in save_decision: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to save decision"
        }), 500

@app.route('/query-decisions', methods=['POST'])
def query_decisions():
    """API 3: Query Decisions (RAG)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_query = data.get('query', '')
        user = data.get('user', 'unknown')

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        print(f"🔎 Processing query: {user_query}")

        rag_engine = get_rag_engine()
        result = rag_engine.query(user_query)

        print(f"✅ Query completed with {len(result.get('sources', []))} sources")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Error in query_decisions: {e}")
        traceback.print_exc()
        return jsonify({
            "answer": "I encountered an error processing your query.",
            "sources": [],
            "error": str(e)
        }), 500

@app.route('/routes', methods=['GET'])
def list_routes():
    """Debug endpoint to list all routes"""
    print("ROUTES ENDPOINT CALLED")
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'url': str(rule)
            })
    print(f"Found {len(routes)} routes")
    return jsonify(routes)

if __name__ == '__main__':
    print("🚀 Starting TechAtlas Backend v2.0...")

    # Initialize Firebase
    try:
        cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        exit(1)

    print("✅ All services ready")
    print(f"🌐 Server starting on http://127.0.0.1:{Config.PORT}")

    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=True
    )
