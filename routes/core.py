from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import logging
import os

core_bp = Blueprint('core', __name__)
logger = logging.getLogger(__name__)

@core_bp.route('/', methods=['GET'])
def root():
    """Root endpoint with service information and available endpoints"""
    endpoints = [
        {"path": "/", "methods": ["GET"], "description": "Service information"},
        {"path": "/health", "methods": ["GET"], "description": "Health check"},
        {"path": "/routes", "methods": ["GET"], "description": "List all routes"},
        {"path": "/version", "methods": ["GET"], "description": "API version info"},
        {"path": "/detect-decision", "methods": ["POST"], "description": "Detect decisions in text"},
        {"path": "/analyze-decision", "methods": ["POST"], "description": "Feasibility analysis"},
        {"path": "/save-decision", "methods": ["POST"], "description": "Save a decision"},
        {"path": "/query-decisions", "methods": ["POST"], "description": "Query saved decisions"},
        {"path": "/decisions", "methods": ["GET"], "description": "List all decisions"},
        {"path": "/dashboard/stats", "methods": ["GET"], "description": "Dashboard statistics"}
    ]
    
    return jsonify({
        "service": "TechAtlas Backend",
        "status": "operational",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": endpoints
    }), 200


@core_bp.route('/health', methods=['GET'])
def health_check():
    """Health check with component status"""
    services = {}
    
    # Check Firebase
    try:
        from firebase_admin import firestore
        db = firestore.client()
        db.collection('health').document('check').get()
        services["firebase"] = True
    except Exception as e:
        logger.warning(f"Firebase health check failed: {str(e)}")
        services["firebase"] = False

    # Check Vector Store
    try:
        from services.vector_store import VectorStore
        vector_store = VectorStore()
        services["vector_store"] = vector_store.index.ntotal > 0
    except Exception as e:
        logger.warning(f"Vector Store health check failed: {str(e)}")
        services["vector_store"] = False

    # Check Gemini AI (optional)
    try:
        # Prefer the v1 client if available
        try:
            from google import genai as genai_v1
            client = genai_v1.Client(api_key=os.getenv('GEMINI_API_KEY'))
            _ = client.models.generate_content(
                model='models/gemini-2.5-flash',
                contents='health check'
            )
            services["gemini_ai"] = True
        except ImportError:
            # Fallback: try existing analyzer (may rely on older SDK behavior)
            from services.feasibility_analyzer import FeasibilityAnalyzer
            analyzer = FeasibilityAnalyzer()
            analyzer.model.generate_content("test")
            services["gemini_ai"] = True
        except Exception as e:
            raise e
    except Exception as e:
        logger.warning(f"Gemini AI health check failed: {str(e)}")
        # Mark as not-checked (optional component)
        services["gemini_ai"] = None

    # Check Embedder
    try:
        from services.embedder import GeminiEmbedder
        embedder = GeminiEmbedder()
        embedding = embedder.embed("test")
        services["embedder"] = len(embedding) == 768
    except Exception as e:
        logger.warning(f"Embedder health check failed: {str(e)}")
        services["embedder"] = False

    # Determine overall status based on critical services only
    critical_services = ['firebase', 'embedder']
    is_healthy = all(services.get(s) for s in critical_services)
    
    return jsonify({
        "status": "healthy" if is_healthy else "degraded",
        "service": "TechAtlas Backend",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services
    }), 200


@core_bp.route('/routes', methods=['GET'])
def list_routes():
    """List all registered routes (debug/development)"""
    from flask import current_app
    
    routes = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]),
                'path': str(rule)
            })
    
    routes.sort(key=lambda x: x['path'])
    
    return jsonify({
        "success": True,
        "count": len(routes),
        "routes": routes
    }), 200


@core_bp.route('/version', methods=['GET'])
def version_info():
    """API version and build information"""
    return jsonify({
        "version": "2.0.0",
        "build": "production",
        "api_version": "v2",
        "release_date": "2024-11-11",
        "features": [
            "Decision Detection",
            "Feasibility Analysis",
            "Semantic Search",
            "RAG Engine",
            "Risk Assessment",
            "Dashboard Analytics"
        ]
    }), 200
