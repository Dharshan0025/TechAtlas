import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import traceback

def test_firestore():
    print("Testing Firestore connection...")
    try:
        # Try to get credentials using the same logic as app.py
        firebase_creds = Config.get_firebase_credentials()
        print(f"Credentials found: {type(firebase_creds)}")

        if isinstance(firebase_creds, dict):
            cred = credentials.Certificate(firebase_creds)
        else:
            cred = credentials.Certificate(firebase_creds)
        
        # Initialize app (if not already initialized)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("Firebase app initialized.")
        
        db = firestore.client()
        print("Firestore client obtained.")
        
        # Try a simple write
        doc_ref = db.collection('test_collection').document('test_doc')
        doc_ref.set({'test': 'value', 'timestamp': firestore.SERVER_TIMESTAMP})
        print("Successfully wrote to Firestore.")
        
        # Try a read
        doc = doc_ref.get()
        print(f"Successfully read from Firestore: {doc.to_dict()}")
        
    except Exception as e:
        print(f"Firestore test failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_firestore()
