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

# Import all blueprints
try:
    from routes.core import core_bp
    from routes.detect import detect_bp
    from routes.analyze import analyze_bp
    from routes.save import save_bp
    from routes.query import query_bp
    from routes.decisions import decisions_bp
    from routes.dashboard import dashboard_bp
    from routes.users import users_bp
    from routes.analytics import analytics_bp
    from routes.risk import risk_bp
    from routes.audit import audit_bp
    from routes.dev import dev_bp
    print("DEBUG: All blueprints imported successfully")
except Exception as e:
    print(f"ERROR: Failed to import blueprints: {e}")
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

# Register all blueprints
print("DEBUG: Registering blueprints...")
try:
    # Core routes (/, /health, /routes, /version)
    app.register_blueprint(core_bp)
    print("DEBUG: core_bp registered")
    
    # Decision detection and analysis
    app.register_blueprint(detect_bp)
    print("DEBUG: detect_bp registered")
    
    app.register_blueprint(analyze_bp)
    print("DEBUG: analyze_bp registered")
    
    # Decision storage
    app.register_blueprint(save_bp)
    print("DEBUG: save_bp registered")
    
    # Query and search
    app.register_blueprint(query_bp)
    print("DEBUG: query_bp registered")
    
    # Decision CRUD operations
    app.register_blueprint(decisions_bp)
    print("DEBUG: decisions_bp registered")
    
    # Dashboard and analytics
    app.register_blueprint(dashboard_bp)
    print("DEBUG: dashboard_bp registered")
    
    # User management
    app.register_blueprint(users_bp)
    print("DEBUG: users_bp registered")
    
    # Analytics and trends
    app.register_blueprint(analytics_bp)
    print("DEBUG: analytics_bp registered")
    
    # Risk assessment
    app.register_blueprint(risk_bp)
    print("DEBUG: risk_bp registered")
    
    # Audit and export
    app.register_blueprint(audit_bp)
    print("DEBUG: audit_bp registered")
    
    # Development utilities
    app.register_blueprint(dev_bp)
    print("DEBUG: dev_bp registered")
    
    print("DEBUG: All blueprints registered successfully")
except Exception as e:
    print(f"ERROR: Failed to register blueprints: {e}")
    traceback.print_exc()

# Note: Core routes (/, /health, /routes, /version) are now handled by core_bp

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
