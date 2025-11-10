from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from config import Config
from routes.detect import detect_bp
from routes.save import save_bp
from routes.query import query_bp

# Initialize Firebase
cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(detect_bp)
app.register_blueprint(save_bp)
app.register_blueprint(query_bp)

@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy", "service": "TechAtlas Backend"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
