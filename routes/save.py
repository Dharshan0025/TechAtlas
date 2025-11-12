from flask import Blueprint, request, jsonify
from models.decision import Decision
from services.embedder import GeminiEmbedder
from services.vector_store import VectorStore
from services.audit_logger import AuditLogger
import firebase_admin
from firebase_admin import firestore
import logging
import traceback

save_bp = Blueprint('save', __name__)
logger = logging.getLogger(__name__)

# Initialize services with lazy loading
embedder = None
vector_store = None
audit_logger = None

def get_embedder():
    global embedder
    if embedder is None:
        embedder = GeminiEmbedder()
    return embedder

def get_vector_store():
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store

def get_audit_logger():
    global audit_logger
    if audit_logger is None:
        audit_logger = AuditLogger()
    return audit_logger

@save_bp.route('/save-decision', methods=['POST'])
def save_decision():
    """Save a decision with embeddings to Firestore and vector store"""
    try:
        # Validate request has JSON
        if not request.is_json:
            logger.warning("Non-JSON request received")
            return jsonify({
                "success": False,
                "error": "Invalid request",
                "message": "Request must be JSON",
                "status": 400
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'owner', 'rationale', 'due_date', 'thread_link']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                missing_fields.append(f"{field} (empty)")
        
        if missing_fields:
            logger.warning(f"Missing or empty required fields: {missing_fields}")
            return jsonify({
                "success": False,
                "error": "Missing or empty required fields",
                "missing_fields": missing_fields,
                "status": 400
            }), 400
        
        logger.info(f"Saving decision: {data['title']} by {data['owner']}")
        
        # Create Decision object
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
            logger.error(f"Failed to create Decision object: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Invalid decision data",
                "message": str(e),
                "status": 400
            }), 400
        
        # Generate embedding
        try:
            embedder_instance = get_embedder()
            embedding_text = decision.get_embedding_text()
            embedding = embedder_instance.embed(embedding_text)
            logger.info("Embedding generated successfully")
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Embedding generation failed",
                "message": "Failed to generate vector embeddings for the decision",
                "status": 500
            }), 500
        
        # Store in FAISS vector store
        try:
            vector_store_instance = get_vector_store()
            vector_store_instance.upsert(
                decision_id=decision.decision_id,
                embedding=embedding,
                metadata=decision.to_dict()
            )
            logger.info(f"Decision stored in vector database: {decision.decision_id}")
        except Exception as e:
            logger.error(f"Vector store failed: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Vector store operation failed",
                "message": "Failed to store decision in vector database",
                "status": 500
            }), 500
        
        # Store in Firestore
        try:
            db = firestore.client()
            doc_ref = db.collection('decisions').document(decision.decision_id)
            doc_ref.set(decision.to_dict())
            logger.info(f"Decision saved to Firestore: {decision.decision_id}")

            # Add creation event to history
            history_ref = doc_ref.collection('history').document()
            history_ref.set({
                'timestamp': decision.created_at,
                'user': decision.owner,
                'action': 'created',
                'changes': decision.to_dict()
            })
            logger.info(f"Creation history added for decision: {decision.decision_id}")

            # Log audit event
            audit = get_audit_logger()
            audit.log_decision_created(decision.decision_id, decision.owner, decision.to_dict())

        except Exception as e:
            logger.error(f"Firestore save failed: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Database save failed",
                "message": "Failed to save decision to Firestore",
                "status": 500
            }), 500
        
        logger.info(f"Decision saved successfully: {decision.decision_id}")
        return jsonify({
            "success": True,
            "decision_id": decision.decision_id,
            "message": "Decision saved and vectorized successfully",
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in save_decision: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred while saving the decision",
            "status": 500
        }), 500
