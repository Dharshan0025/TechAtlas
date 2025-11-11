from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import traceback
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("DEBUG: Starting Flask app initialization...")

try:
    # Initialize Firebase
    print("DEBUG: Initializing Firebase...")
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    print("DEBUG: Firebase initialized successfully")
except Exception as e:
    print(f"ERROR: Firebase initialization failed: {e}")
    traceback.print_exc()

try:
    from routes.detect import detect_bp
    print("DEBUG: Detect blueprint imported")
except Exception as e:
    print(f"ERROR: Failed to import detect blueprint: {e}")
    traceback.print_exc()

try:
    from routes.save import save_bp
    print("DEBUG: Save blueprint imported")
except Exception as e:
    print(f"ERROR: Failed to import save blueprint: {e}")
    traceback.print_exc()

try:
    from routes.query import query_bp
    print("DEBUG: Query blueprint imported")
except Exception as e:
    print(f"ERROR: Failed to import query blueprint: {e}")
    traceback.print_exc()

# Create Flask app
print("DEBUG: Creating Flask app...")
app = Flask(__name__)
CORS(app)

# Global error handlers
from werkzeug.exceptions import HTTPException

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Handle HTTP exceptions (404, 405, etc.) - pass them through"""
    return jsonify({
        "error": e.name,
        "message": e.description,
        "status": e.code
    }), e.code

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        "error": "Internal server error",
        "status": 500,
        "message": str(e)
    }), 500

@app.before_request
def log_request_info():
    try:
        request.start_time = datetime.now(timezone.utc)
        if request.endpoint != 'health_check':  # Skip logging for health checks
            logger.info(f"Request: {request.method} {request.path} - {request.get_json(silent=True) or request.args}")
    except Exception as e:
        logger.error(f"Error in log_request_info: {str(e)}")

@app.after_request
def log_response(response):
    try:
        if hasattr(request, 'start_time') and request.endpoint != 'health_check':
            duration = (datetime.now(timezone.utc) - request.start_time).total_seconds() * 1000
            logger.info(
                f"Response: {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.2f}ms"
            )
    except Exception as e:
        logger.error(f"Error in log_response: {str(e)}")
    return response

# Register blueprints
print("DEBUG: Registering blueprints...")
try:
    app.register_blueprint(detect_bp)
    print("DEBUG: detect_bp registered")
except Exception as e:
    print(f"ERROR: Failed to register detect_bp: {e}")
    traceback.print_exc()

try:
    app.register_blueprint(save_bp)
    print("DEBUG: save_bp registered")
except Exception as e:
    print(f"ERROR: Failed to register save_bp: {e}")
    traceback.print_exc()

try:
    app.register_blueprint(query_bp)
    print("DEBUG: query_bp registered")
except Exception as e:
    print(f"ERROR: Failed to register query_bp: {e}")
    traceback.print_exc()

print("DEBUG: All blueprints registered successfully")

@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy", "service": "TechAtlas Backend"}

@app.route('/routes', methods=['GET'])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'url': str(rule)
        })
    return jsonify(routes)

# Root endpoint
@app.route('/')
def root():
    """Root endpoint that provides service information and available endpoints."""
    from flask import url_for
    
    endpoints = [
        {"path": "/", "methods": ["GET"], "description": "Service information"},
        {"path": "/health", "methods": ["GET"], "description": "Health check"},
        {"path": "/detect-decision", "methods": ["POST"], "description": "Detect decisions in text"},
        {"path": "/save-decision", "methods": ["POST"], "description": "Save a decision"},
        {"path": "/query-decisions", "methods": ["POST"], "description": "Query saved decisions"}
    ]
    
    return jsonify({
        "service": "TechAtlas Backend",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": endpoints
    })

# Log all registered routes on startup
def log_registered_routes():
    """Log all registered routes for debugging."""
    try:
        logger.info("="*60)
        logger.info("REGISTERED ROUTES:")
        logger.info("="*60)
        for rule in app.url_map.iter_rules():
            methods = ','.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
            logger.info(f"{methods:10s} {str(rule):40s} -> {rule.endpoint}")
        logger.info("="*60)
    except Exception as e:
        logger.error(f"Error logging routes: {str(e)}")

if __name__ == '__main__':
    try:
        logger.info("Starting Flask development server...")
        logger.info(f"Debug mode: {Config.DEBUG}")
        logger.info(f"Port: {Config.PORT}")
        
        # Log all registered routes
        log_registered_routes()
        
        # Start the server
        app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}", exc_info=True)
        raise
