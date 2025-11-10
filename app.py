from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from config import Config
import traceback

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

@app.before_request
def log_request_info():
    from flask import request
    print(f"REQUEST: {request.method} {request.url} - Data: {request.get_json(silent=True)}")

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

if __name__ == '__main__':
    print("DEBUG: Starting Flask development server...")
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)
