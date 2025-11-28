import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base Directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    # Default to Gemini 2.5 Flash model (v1)
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'models/gemini-2.5-flash')
    GEMINI_EMBEDDING_MODEL = 'models/text-embedding-004'
    
    # Rate limiting
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '4.0'))  # Seconds between API calls
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
    FIREBASE_CREDENTIALS_JSON = os.getenv('FIREBASE_CREDENTIALS_JSON')
    
    # App
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Detection keywords
    DECISION_KEYWORDS = [
        "we decided", "we chose", "let's go with", "finalize",
        "agreed on", "we're using", "migration to", "switch to"
    ]

    @staticmethod
    def get_firebase_credentials():
        """
        Get Firebase credentials for Railway deployment.
        Returns credentials object for Firebase initialization.
        Supports both JSON string (Railway) and file path (local dev).
        """
        # Method 1: Use JSON string from environment (Railway recommended)
        if Config.FIREBASE_CREDENTIALS_JSON:
            try:
                val = Config.FIREBASE_CREDENTIALS_JSON
                print(f"DEBUG: Parsing FIREBASE_CREDENTIALS_JSON. Length: {len(val)}, Start: {val[:20]!r}...")
                return json.loads(Config.FIREBASE_CREDENTIALS_JSON)
            except json.JSONDecodeError as e:
                print(f"ERROR: JSON decode error: {e}")
                raise ValueError("Invalid FIREBASE_CREDENTIALS_JSON format")
        
        # Method 2: Use file path (local development)
        elif Config.FIREBASE_CREDENTIALS_PATH:
            return Config.FIREBASE_CREDENTIALS_PATH
        
        else:
            raise ValueError("No Firebase credentials configured")
