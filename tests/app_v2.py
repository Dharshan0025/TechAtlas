#!/usr/bin/env python3
"""
TechAtlas Backend v2.0 - Production Ready
A hardened Flask application with comprehensive error handling and logging
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
import logging
from datetime import datetime, timezone
from functools import wraps
import sys

# Configure logging with UTF-8 encoding for file handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('techatlas_backend.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global service instances with health status
services_status = {
    'firebase': False,
    'detector': False,
    'embedder': False,
    'vector_store': False,
    'rag_engine': False
}

# Global service instances (lazy initialization)
detector = None
embedder = None
vector_store = None
rag_engine = None


def standardize_response(success=True, data=None, error=None, status_code=200, message=None):
    """
    Standardize all API responses
    
    Args:
        success: Boolean indicating success/failure
        data: Response data (for success cases)
        error: Error message (for failure cases)
        status_code: HTTP status code
        message: Optional message
    
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        "success": success,
        "status_code": status_code,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if success:
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
    else:
        response["error"] = error or "An error occurred"
        if message:
            response["message"] = message
    
    return jsonify(response), status_code


def validate_json_input(required_fields=None):
    """
    Decorator to validate JSON input and required fields
    
    Args:
        required_fields: List of required field names
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check if request has JSON data
            if not request.is_json:
                logger.warning(f"Non-JSON request to {request.endpoint}")
                return standardize_response(
                    success=False,
                    error="Request must be JSON",
                    status_code=400
                )
            
            try:
                data = request.get_json()
            except Exception as e:
                logger.error(f"Failed to parse JSON: {str(e)}")
                return standardize_response(
                    success=False,
                    error="Invalid JSON format",
                    status_code=400
                )
            
            if not data:
                return standardize_response(
                    success=False,
                    error="No JSON data provided",
                    status_code=400
                )
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return standardize_response(
                        success=False,
                        error=f"Missing required fields: {', '.join(missing_fields)}",
                        status_code=400
                    )
                
                # Check for empty required fields
                empty_fields = [field for field in required_fields if not data.get(field)]
                if empty_fields:
                    return standardize_response(
                        success=False,
                        error=f"Empty required fields: {', '.join(empty_fields)}",
                        status_code=400
                    )
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def log_request():
    """Log incoming request details"""
    logger.info(f"→ {request.method} {request.path} from {request.remote_addr}")
    if request.is_json:
        # Don't log sensitive data in production
        logger.debug(f"Request data: {request.get_json()}")


def log_response(response_data, status_code):
    """Log response details"""
    logger.info(f"← {request.method} {request.path} - Status: {status_code}")
    logger.debug(f"Response: {response_data}")


def get_detector():
    """Lazy initialization of DecisionDetector with error handling"""
    global detector, services_status
    if detector is None:
        try:
            detector = DecisionDetector()
            services_status['detector'] = True
            logger.info("[OK] DecisionDetector initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize DecisionDetector: {str(e)}")
            services_status['detector'] = False
            raise
    return detector


def get_embedder():
    """Lazy initialization of GeminiEmbedder with error handling"""
    global embedder, services_status
    if embedder is None:
        try:
            embedder = GeminiEmbedder()
            services_status['embedder'] = True
            logger.info("[OK] GeminiEmbedder initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize GeminiEmbedder: {str(e)}")
            services_status['embedder'] = False
            raise
    return embedder


def get_vector_store():
    """Lazy initialization of VectorStore with error handling"""
    global vector_store, services_status
    if vector_store is None:
        try:
            vector_store = VectorStore()
            services_status['vector_store'] = True
            logger.info("[OK] VectorStore initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize VectorStore: {str(e)}")
            services_status['vector_store'] = False
            raise
    return vector_store


def get_rag_engine():
    """Lazy initialization of RAGEngine with error handling"""
    global rag_engine, services_status
    if rag_engine is None:
        try:
            rag_engine = RAGEngine()
            services_status['rag_engine'] = True
            logger.info("[OK] RAGEngine initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize RAGEngine: {str(e)}")
            services_status['rag_engine'] = False
            raise
    return rag_engine


def get_firestore():
    """Get Firestore client with error handling"""
    try:
        return firestore.client()
    except Exception as e:
        logger.error(f"[ERROR] Firestore client error: {str(e)}")
        raise


@app.before_request
def before_request():
    """Execute before each request"""
    request.start_time = datetime.now(timezone.utc)
    log_request()


@app.after_request
def after_request(response):
    """Execute after each request"""
    if hasattr(request, 'start_time'):
        duration = (datetime.now(timezone.utc) - request.start_time).total_seconds() * 1000
        logger.info(f"Request completed in {duration:.2f}ms")
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return standardize_response(
        success=False,
        error="Internal server error",
        message=str(e),
        status_code=500
    )


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return standardize_response(
        success=False,
        error="Endpoint not found",
        message=f"The endpoint {request.path} does not exist",
        status_code=404
    )


@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return standardize_response(
        success=False,
        error="Method not allowed",
        message=f"The method {request.method} is not allowed for {request.path}",
        status_code=405
    )


# ============================================================
# ENDPOINTS
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint with service status
    
    Returns:
        200: Service is healthy with service statuses
        500: Service has issues
    """
    try:
        # Check Firestore connection
        try:
            db = get_firestore()
            # Perform a lightweight operation
            db.collection('health').document('check').get()
            services_status['firebase'] = True
        except Exception as e:
            logger.warning(f"Firebase health check failed: {str(e)}")
            services_status['firebase'] = False
        
        # Determine overall health
        critical_services = ['firebase']
        is_healthy = all(services_status.get(service, False) for service in critical_services)
        
        response_data = {
            "service": "TechAtlas Backend",
            "version": "2.0",
            "status": "healthy" if is_healthy else "degraded",
            "services": services_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        status_code = 200 if is_healthy else 503
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return standardize_response(
            success=False,
            error="Health check failed",
            message=str(e),
            status_code=500
        )


@app.route('/detect-decision', methods=['POST'])
@validate_json_input(required_fields=['message'])
def detect_decision():
    """
    API 1: Detect Decision in Text
    
    Request JSON:
        {
            "message": "Text to analyze",
            "user": "user@example.com" (optional),
            "channel_id": "channel-id" (optional)
        }
    
    Response:
        200: {
            "success": true,
            "data": {
                "is_decision": true/false,
                "confidence": 0.0-1.0,
                "suggested_title": "Title"
            }
        }
        400: Invalid input
        500: Server error
    """
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user = data.get('user', 'unknown')
        channel_id = data.get('channel_id', 'unknown')
        
        # Validate message length
        if len(message) > 10000:
            return standardize_response(
                success=False,
                error="Message too long",
                message="Message must be less than 10000 characters",
                status_code=400
            )
        
        logger.info(f"Processing decision from user: {user}, channel: {channel_id}")
        logger.debug(f"Message: {message[:100]}...")
        
        # Initialize and use detector
        try:
            detector_instance = get_detector()
        except Exception as e:
            logger.error(f"Failed to initialize detector: {str(e)}")
            return standardize_response(
                success=False,
                error="Decision detection service unavailable",
                message="The decision detection service could not be initialized",
                status_code=503
            )
        
        # Perform detection
        try:
            is_decision, confidence, title = detector_instance.detect(message)
            
            result_data = {
                "is_decision": bool(is_decision),
                "confidence": float(confidence),
                "suggested_title": str(title)
            }
            
            logger.info(f"[OK] Detection result: is_decision={is_decision}, confidence={confidence:.2f}")
            
            return standardize_response(
                success=True,
                data=result_data,
                message="Decision detection completed successfully",
                status_code=200
            )
            
        except Exception as e:
            logger.error(f"Detection failed: {str(e)}", exc_info=True)
            # Return graceful fallback
            return standardize_response(
                success=False,
                data={
                    "is_decision": False,
                    "confidence": 0.0,
                    "suggested_title": ""
                },
                error="Detection processing failed",
                message=str(e),
                status_code=500
            )
    
    except Exception as e:
        logger.error(f"❌ Error in detect_decision: {str(e)}", exc_info=True)
        return standardize_response(
            success=False,
            error="Failed to process decision detection request",
            message=str(e),
            status_code=500
        )

@app.route('/save-decision', methods=['POST'])
@validate_json_input(required_fields=['title', 'owner', 'rationale', 'due_date', 'thread_link'])
def save_decision():
    """
    API 2: Save Decision
    
    Request JSON:
        {
            "title": "Decision title",
            "owner": "owner@example.com",
            "rationale": "Decision rationale",
            "due_date": "YYYY-MM-DD",
            "thread_link": "https://...",
            "participants": ["user1", "user2"] (optional),
            "channel_id": "channel-id" (optional)
        }
    
    Response:
        200: {
            "success": true,
            "data": {
                "decision_id": "uuid",
                "message": "Decision saved successfully"
            }
        }
        400: Invalid input
        500: Server error
    """
    try:
        data = request.get_json()
        
        # Validate field lengths
        if len(data.get('title', '')) > 500:
            return standardize_response(
                success=False,
                error="Title too long",
                message="Title must be less than 500 characters",
                status_code=400
            )
        
        if len(data.get('rationale', '')) > 5000:
            return standardize_response(
                success=False,
                error="Rationale too long",
                message="Rationale must be less than 5000 characters",
                status_code=400
            )
        
        logger.info(f"[SAVE] Saving decision: {data['title']}")
        
        # Create decision object
        try:
            decision = Decision(
                title=data['title'],
                owner=data['owner'],
                rationale=data['rationale'],
                due_date=data['due_date'],
                thread_link=data['thread_link'],
                participants=data.get('participants', []),
                channel_id=data.get('channel_id', '')
            )
        except Exception as e:
            logger.error(f"Failed to create decision object: {str(e)}")
            return standardize_response(
                success=False,
                error="Invalid decision data",
                message=str(e),
                status_code=400
            )
        
        # Generate embedding
        try:
            embedder_instance = get_embedder()
            embedding_text = decision.get_embedding_text()
            embedding = embedder_instance.embed(embedding_text)
            logger.info("[OK] Embedding generated")
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}", exc_info=True)
            return standardize_response(
                success=False,
                error="Embedding generation failed",
                message="Failed to generate vector embeddings for the decision",
                status_code=500
            )
        
        # Store in vector database
        try:
            vector_store_instance = get_vector_store()
            vector_store_instance.upsert(
                decision_id=decision.decision_id,
                embedding=embedding,
                metadata=decision.to_dict()
            )
            logger.info("[OK] Decision stored in vector database")
        except Exception as e:
            logger.error(f"Vector store failed: {str(e)}", exc_info=True)
            return standardize_response(
                success=False,
                error="Vector store operation failed",
                message="Failed to store decision in vector database",
                status_code=500
            )
        
        # Store in Firestore
        try:
            firestore_db = get_firestore()
            firestore_db.collection('decisions').document(decision.decision_id).set(decision.to_dict())
            logger.info(f"[OK] Decision saved to Firestore: {decision.decision_id}")
        except Exception as e:
            logger.error(f"Firestore save failed: {str(e)}", exc_info=True)
            return standardize_response(
                success=False,
                error="Database save failed",
                message="Failed to save decision to Firestore",
                status_code=500
            )
        
        result_data = {
            "decision_id": decision.decision_id,
            "title": decision.title,
            "created_at": decision.created_at
        }
        
        return standardize_response(
            success=True,
            data=result_data,
            message="Decision saved and vectorized successfully",
            status_code=200
        )
    
    except Exception as e:
        logger.error(f"[ERROR] Error in save_decision: {str(e)}", exc_info=True)
        return standardize_response(
            success=False,
            error="Failed to save decision",
            message=str(e),
            status_code=500
        )


@app.route('/query-decisions', methods=['POST'])
@validate_json_input(required_fields=['query'])
def query_decisions():
    """
    API 3: Query Decisions (RAG)
    
    Request JSON:
        {
            "query": "Question about decisions",
            "user": "user@example.com" (optional)
        }
    
    Response:
        200: {
            "success": true,
            "data": {
                "answer": "AI-generated answer",
                "sources": [{"title": "...", "content": "..."}]
            }
        }
        400: Invalid input
        500: Server error
    """
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        user = data.get('user', 'unknown')
        
        # Validate query length
        if len(user_query) > 1000:
            return standardize_response(
                success=False,
                error="Query too long",
                message="Query must be less than 1000 characters",
                status_code=400
            )
        
        logger.info(f"[QUERY] Processing query from user: {user}")
        logger.debug(f"Query: {user_query}")
        
        # Initialize RAG engine
        try:
            rag_engine_instance = get_rag_engine()
        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {str(e)}")
            return standardize_response(
                success=False,
                error="Query service unavailable",
                message="The query service could not be initialized",
                status_code=503
            )
        
        # Perform query
        try:
            result = rag_engine_instance.query(user_query)
            
            logger.info(f"[OK] Query completed with {len(result.get('sources', []))} sources")
            
            return standardize_response(
                success=True,
                data=result,
                message="Query processed successfully",
                status_code=200
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}", exc_info=True)
            # Return graceful fallback
            return standardize_response(
                success=False,
                data={
                    "answer": "I encountered an error while processing your query. Please try again later.",
                    "sources": []
                },
                error="Query processing failed",
                message=str(e),
                status_code=500
            )
    
    except Exception as e:
        logger.error(f"[ERROR] Error in query_decisions: {str(e)}", exc_info=True)
        return standardize_response(
            success=False,
            error="Failed to process query",
            message=str(e),
            status_code=500
        )


@app.route('/routes', methods=['GET'])
def list_routes():
    """
    Debug endpoint to list all registered routes
    
    Returns:
        200: List of all registered routes
    """
    try:
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]),
                    'path': str(rule)
                })
        
        # Sort by path
        routes.sort(key=lambda x: x['path'])
        
        return jsonify({
            "success": True,
            "count": len(routes),
            "routes": routes
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing routes: {str(e)}", exc_info=True)
        return standardize_response(
            success=False,
            error="Failed to list routes",
            message=str(e),
            status_code=500
        )


# ============================================================
# INITIALIZATION AND STARTUP
# ============================================================

def initialize_firebase():
    """Initialize Firebase with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            services_status['firebase'] = True
            logger.info("[OK] Firebase initialized successfully")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Firebase initialization attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                logger.critical("Firebase initialization failed after all retries")
                services_status['firebase'] = False
                return False
    return False

if __name__ == '__main__':
    print("="*60)
    print("🚀 TechAtlas Backend v2.0 - Production")
    print("="*60)
    
    # Initialize Firebase
    if not initialize_firebase():
        logger.critical("CRITICAL: Firebase initialization failed. Exiting...")
        sys.exit(1)
    
    # Log configuration
    logger.info("Configuration:")
    logger.info(f"   - Port: {Config.PORT}")
    logger.info(f"   - Debug: {Config.DEBUG}")
    logger.info(f"   - Firebase: {Config.FIREBASE_CREDENTIALS_PATH}")
    
    # Log service status
    logger.info("Service Status:")
    for service, status in services_status.items():
        status_text = "[OK]" if status else "[NOT READY]"
        logger.info(f"   {status_text} {service}: {'Ready' if status else 'Not initialized'}")
    
    print("="*60)
    print(f"🌐 Server starting on http://0.0.0.0:{Config.PORT}")
    print("="*60)
    
    # Start server
    try:
        app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Server failed to start: {str(e)}", exc_info=True)
        sys.exit(1)
