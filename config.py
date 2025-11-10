import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-1.5-flash'
    GEMINI_EMBEDDING_MODEL = 'models/text-embedding-004'
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
    
    # App
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Detection keywords
    DECISION_KEYWORDS = [
        "we decided", "we chose", "let's go with", "finalize",
        "agreed on", "we're using", "migration to", "switch to"
    ]
