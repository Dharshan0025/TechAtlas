import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
from models.decision import Decision
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reproduce():
    print("Attempting to reproduce the issue...")
    try:
        # Initialize Firebase
        firebase_creds = Config.get_firebase_credentials()
        if isinstance(firebase_creds, dict):
            cred = credentials.Certificate(firebase_creds)
        else:
            cred = credentials.Certificate(firebase_creds)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("Firebase initialized.")
        
        # Create Decision object (mock data)
        data = {
            "title": "Test Decision",
            "owner": "test@example.com",
            "rationale": "Testing firestore save",
            "due_date": "2025-01-01",
            "thread_link": "http://example.com",
            "participants": ["test@example.com"],
            "channel_id": "test-channel"
        }
        
        decision = Decision(
            title=data['title'],
            owner=data['owner'],
            rationale=data['rationale'],
            due_date=data['due_date'],
            thread_link=data['thread_link'],
            participants=data.get('participants', []),
            channel_id=data.get('channel_id', '')
        )
        
        print(f"Decision created: {decision.decision_id}")
        print(f"Decision dict: {decision.to_dict()}")
        
        # Try to save to Firestore
        db = firestore.client()
        doc_ref = db.collection('decisions').document(decision.decision_id)
        doc_ref.set(decision.to_dict())
        print("Decision saved to Firestore.")
        
        # Add history
        history_ref = doc_ref.collection('history').document()
        history_ref.set({
            'timestamp': decision.created_at,
            'user': decision.owner,
            'action': 'created',
            'changes': decision.to_dict()
        })
        print("History saved.")
        
        # Audit log (simplified)
        audit_entry = {
            'action': 'create',
            'user': decision.owner,
            'resource_type': 'decision',
            'resource_id': decision.decision_id,
            'details': {
                'title': decision.title,
                'owner': decision.owner
            },
            'timestamp': decision.created_at
        }
        db.collection('audit_logs').add(audit_entry)
        print("Audit log saved.")
        
        print("SUCCESS: Could not reproduce the issue.")
        
    except Exception as e:
        print(f"ERROR CAUGHT: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
