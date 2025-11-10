from flask import Blueprint, request, jsonify
from models.decision import Decision
from services.embedder import GeminiEmbedder
from services.vector_store import VectorStore
import firebase_admin
from firebase_admin import db

save_bp = Blueprint('save', __name__)
embedder = GeminiEmbedder()
vector_store = VectorStore()

@save_bp.route('/save-decision', methods=['POST'])
def save_decision():
    data = request.json
    
    # Create Decision object
    decision = Decision(
        title=data['title'],
        owner=data['owner'],
        rationale=data['rationale'],
        due_date=data['due_date'],
        thread_link=data['thread_link'],
        participants=data.get('participants', []),
        channel_id=data.get('channel_id', '')
    )
    
    # Generate embedding
    embedding_text = decision.get_embedding_text()
    embedding = embedder.embed(embedding_text)
    
    # Store in Pinecone
    vector_store.upsert(
        decision_id=decision.decision_id,
        embedding=embedding,
        metadata=decision.to_dict()
    )
    
    # Store in Firebase
    ref = db.reference(f'decisions/{decision.decision_id}')
    ref.set(decision.to_dict())
    
    return jsonify({
        "success": True,
        "decision_id": decision.decision_id,
        "message": "Decision saved and vectorized successfully"
    })
