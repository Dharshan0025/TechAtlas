from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import logging
from datetime import datetime, timezone
import time
from services.embedder import GeminiEmbedder
from services.vector_store import VectorStore
from services.audit_logger import AuditLogger
from utils.text_processing import process_text
from utils.text_processing import process_text

decisions_bp = Blueprint('decisions', __name__)
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

@decisions_bp.route('/decisions', methods=['GET'])
def list_decisions():
    """
    List all decisions with pagination and filters
    
    Query params: status, owner, channel_id, limit, offset, sort_by
    """
    try:
        db = firestore.client()
        
        # Get query parameters
        status = request.args.get('status')
        owner = request.args.get('owner')
        channel_id = request.args.get('channel_id')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        sort_by = request.args.get('sort_by', 'created_at')
        
        # Build query
        query = db.collection('decisions')
        
        if status:
            query = query.where('status', '==', status)
        if owner:
            query = query.where('owner', '==', owner)
        if channel_id:
            query = query.where('channel_id', '==', channel_id)
        
        # Apply sorting and pagination
        query = query.order_by(sort_by, direction=firestore.Query.DESCENDING)
        query = query.limit(limit).offset(offset)
        
        # Execute query
        decisions = []
        for doc in query.stream():
            decision_data = doc.to_dict()
            decision_data['id'] = doc.id
            decisions.append(decision_data)
        
        return jsonify({
            "success": True,
            "count": len(decisions),
            "decisions": decisions,
            "pagination": {
                "limit": limit,
                "offset": offset
            },
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing decisions: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to list decisions",
            "message": str(e),
            "status": 500
        }), 500


@decisions_bp.route('/decisions/<decision_id>', methods=['GET'])
def get_decision(decision_id):
    """Get single decision by ID"""
    try:
        db = firestore.client()
        doc = db.collection('decisions').document(decision_id).get()
        
        if not doc.exists:
            return jsonify({
                "success": False,
                "error": "Decision not found",
                "status": 404
            }), 404
        
        decision_data = doc.to_dict()
        decision_data['id'] = doc.id
        
        # Log audit event
        user = request.args.get('user', 'system')
        audit = get_audit_logger()
        audit.log_decision_viewed(decision_id, user)
        
        return jsonify({
            "success": True,
            "decision": decision_data,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting decision: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get decision",
            "message": str(e),
            "status": 500
        }), 500


@decisions_bp.route('/decisions/<decision_id>', methods=['PUT'])
def update_decision(decision_id):
    """Update existing decision"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON",
                "status": 400
            }), 400
        
        data = request.get_json()
        db = firestore.client()
        
        # Check if decision exists
        doc_ref = db.collection('decisions').document(decision_id)
        original_doc = doc_ref.get()
        
        if not original_doc.exists:
            return jsonify({
                "success": False,
                "error": "Decision not found",
                "status": 404
            }), 404
            
        original_data = original_doc.to_dict()

        # Update allowed fields
        allowed_fields = ['title', 'rationale', 'status', 'due_date', 'participants', 'owner']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Log history
        changes = {}
        for key, value in update_data.items():
            if key != 'updated_at' and original_data.get(key) != value:
                changes[key] = {
                    'old': original_data.get(key),
                    'new': value
                }

        if changes:
            history_ref = doc_ref.collection('history').document()
            history_ref.set({
                'timestamp': update_data['updated_at'],
                'user': data.get('user', 'system'), # Assumes user is passed in request
                'action': 'updated',
                'changes': changes
            })
            
            # Log audit event
            audit = get_audit_logger()
            audit.log_decision_updated(decision_id, data.get('user', 'system'), changes)

        doc_ref.update(update_data)
        
        # Get updated decision
        updated_doc = doc_ref.get()
        decision_data = updated_doc.to_dict()
        decision_data['id'] = updated_doc.id
        
        return jsonify({
            "success": True,
            "decision": decision_data,
            "message": "Decision updated successfully",
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating decision: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to update decision",
            "message": str(e),
            "status": 500
        }), 500


@decisions_bp.route('/decisions/<decision_id>', methods=['DELETE'])
def delete_decision(decision_id):
    """Soft delete a decision"""
    try:
        db = firestore.client()
        doc_ref = db.collection('decisions').document(decision_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                "success": False,
                "error": "Decision not found",
                "status": 404
            }), 404
        
        # Soft delete by updating status
        doc_ref.update({
            'status': 'Archived',
            'deleted_at': datetime.now(timezone.utc).isoformat()
        })
        
        # Log audit event
        user = request.get_json(silent=True).get('user', 'system') if request.is_json else 'system'
        audit = get_audit_logger()
        audit.log_decision_deleted(decision_id, user)
        
        return jsonify({
            "success": True,
            "message": "Decision archived successfully",
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting decision: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to delete decision",
            "message": str(e),
            "status": 500
        }), 500


@decisions_bp.route('/decisions/<decision_id>/status', methods=['PATCH'])
def change_status(decision_id):
    """Update decision status"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON",
                "status": 400
            }), 400
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                "success": False,
                "error": "Status is required",
                "status": 400
            }), 400
        
        valid_statuses = ['Open', 'In Progress', 'Completed', 'Archived']
        if new_status not in valid_statuses:
            return jsonify({
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                "status": 400
            }), 400
        
        db = firestore.client()
        doc_ref = db.collection('decisions').document(decision_id)
        original_doc = doc_ref.get()
        
        if not original_doc.exists:
            return jsonify({
                "success": False,
                "error": "Decision not found",
                "status": 404
            }), 404
            
        original_data = original_doc.to_dict()
        
        update_time = datetime.now(timezone.utc).isoformat()
        doc_ref.update({
            'status': new_status,
            'status_updated_at': update_time
        })
        
        # Log history
        history_ref = doc_ref.collection('history').document()
        history_ref.set({
            'timestamp': update_time,
            'user': data.get('user', 'system'), # Assumes user is passed in request
            'action': 'status_changed',
            'changes': {
                'status': {
                    'old': original_data.get('status'),
                    'new': new_status
                }
            }
        })
        
        return jsonify({
            "success": True,
            "status": new_status,
            "message": f"Status updated to {new_status}",
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error changing status: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to change status",
            "message": str(e),
            "status": 500
        }), 500


@decisions_bp.route('/decisions/<decision_id>/history', methods=['GET'])
def decision_history(decision_id):
    """Get change log for a decision"""
    try:
        db = firestore.client()
        history_query = db.collection('decisions').document(decision_id).collection('history').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        
        history = []
        for doc in history_query:
            history.append(doc.to_dict())
            
        return jsonify({
            "success": True,
            "decision_id": decision_id,
            "history": history,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get history",
            "message": str(e),
            "status": 500
        }), 500


@decisions_bp.route('/decisions/<decision_id>/related', methods=['GET'])
def related_decisions(decision_id):
    """Find semantically similar decisions"""
    try:
        db = firestore.client()
        doc = db.collection('decisions').document(decision_id).get()
        
        if not doc.exists:
            return jsonify({"success": False, "error": "Decision not found", "status": 404}), 404
            
        decision_data = doc.to_dict()
        
        # Generate embedding for the current decision
        embedder_instance = get_embedder()
        embedding_text = f"{decision_data.get('title', '')}\n{decision_data.get('rationale', '')}"
        embedding = embedder_instance.embed(embedding_text)
        
        # Query for similar decisions
        vector_store_instance = get_vector_store()
        # Query for more results to filter out the original decision
        similar_decisions = vector_store_instance.query(embedding, top_k=4)
        
        # Filter out the original decision and format results
        related = []
        for item in similar_decisions:
            if item['metadata']['id'] != decision_id:
                related.append({
                    'id': item['metadata']['id'],
                    'title': item['metadata']['title'],
                    'score': item['score']
                })
        
        # Ensure we return at most 3
        related = related[:3]

        return jsonify({
            "success": True,
            "decision_id": decision_id,
            "related_decisions": related,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error finding related decisions: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to find related decisions",
            "message": str(e),
            "status": 500
        }), 500


@decisions_bp.route('/search-decisions', methods=['POST'])
def search_decisions():
    """Structured search with filters"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON",
                "status": 400
            }), 400
        
        data = request.get_json()
        keyword = data.get('keyword', '')
        owner = data.get('owner')
        date_range = data.get('date_range', {})
        status = data.get('status')
        channel_id = data.get('channel_id')
        
        db = firestore.client()
        query = db.collection('decisions')
        
        # Apply filters
        if owner:
            query = query.where('owner', '==', owner)
        if status:
            query = query.where('status', '==', status)
        if channel_id:
            query = query.where('channel_id', '==', channel_id)
        
        # Execute query
        results = []
        processed_keyword = process_text(keyword) if keyword else []

        for doc in query.stream():
            decision_data = doc.to_dict()
            decision_data['id'] = doc.id
            
            if not keyword:
                results.append(decision_data)
                continue

            # Improved keyword filter
            title_text = decision_data.get('title', '')
            rationale_text = decision_data.get('rationale', '')
            
            decision_text = f"{title_text} {rationale_text}"
            processed_decision_text = process_text(decision_text)
            
            if any(kw in processed_decision_text for kw in processed_keyword):
                results.append(decision_data)

        return jsonify({
            "success": True,
            "count": len(results),
            "decisions": results,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching decisions: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Search failed",
            "message": str(e),
            "status": 500
        }), 500


@decisions_bp.route('/decisions/bulk', methods=['POST'])
def create_bulk_decisions():
    """
    Create multiple decisions in a single batch request
    Request body: {"decisions": [...]}
    Returns: {"success": true, "created": N, "decision_ids": [...]} 
    """
    try:
        data = request.get_json()
        decisions_data = data.get('decisions', [])
        
        # Validation
        if not decisions_data or not isinstance(decisions_data, list):
            return jsonify({
                "success": False,
                "error": "Invalid request: 'decisions' array required"
            }), 400
        
        if len(decisions_data) == 0:
            return jsonify({
                "success": False,
                "error": "At least one decision required"
            }), 400
        
        if len(decisions_data) > 50:
            return jsonify({
                "success": False,
                "error": "Maximum 50 decisions allowed per bulk request"
            }), 400
        
        # Process each decision
        db = firestore.client()
        created_ids = []
        
        for idx, decision in enumerate(decisions_data):
            # Generate unique decision ID (add small delay to ensure uniqueness)
            if idx > 0:
                time.sleep(0.001)  # 1ms delay between IDs
            timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
            decision_id = f"dec_{timestamp_ms}"
            
            # Prepare decision data with defaults
            now_iso = datetime.utcnow().isoformat() + "+00:00"
            decision_data = {
                'decision_id': decision_id,
                'title': decision.get('title', ''),
                'owner': decision.get('owner', 'system'),
                'rationale': decision.get('rationale', ''),
                'status': decision.get('status', 'Open'),
                'risk_score': decision.get('risk_score', 5),
                'participants': decision.get('participants', []),
                'channel_id': decision.get('channel_id', ''),
                'thread_link': decision.get('thread_link', ''),
                'due_date': decision.get('due_date', ''),
                'created_at': now_iso,
                'updated_at': now_iso,
                'history': [{
                    'action': 'created',
                    'timestamp': now_iso,
                    'user': 'system',
                    'changes': {}
                }]
            }
            
            # Save to Firestore
            db.collection('decisions').document(decision_id).set(decision_data)
            
            created_ids.append(decision_id)
        
        # Return success response
        response = {
            "success": True,
            "created": len(created_ids),
            "decision_ids": created_ids
        }
        
        return jsonify(response), 201
        
    except Exception as e:
        logger.error(f"Bulk creation failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Bulk creation failed: {str(e)}"
        }), 500
