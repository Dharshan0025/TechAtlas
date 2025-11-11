from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import logging
from datetime import datetime, timezone

decisions_bp = Blueprint('decisions', __name__)
logger = logging.getLogger(__name__)

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
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                "success": False,
                "error": "Decision not found",
                "status": 404
            }), 404
        
        # Update allowed fields
        allowed_fields = ['title', 'rationale', 'status', 'due_date', 'participants', 'owner']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
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
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                "success": False,
                "error": "Decision not found",
                "status": 404
            }), 404
        
        doc_ref.update({
            'status': new_status,
            'status_updated_at': datetime.now(timezone.utc).isoformat()
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
        # TODO: Implement actual history tracking
        # For now, return placeholder
        
        return jsonify({
            "success": True,
            "decision_id": decision_id,
            "history": [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "user": "system",
                    "action": "created",
                    "changes": {}
                }
            ],
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
        # TODO: Implement vector similarity search
        # For now, return placeholder
        
        return jsonify({
            "success": True,
            "decision_id": decision_id,
            "related_decisions": [],
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
        for doc in query.stream():
            decision_data = doc.to_dict()
            decision_data['id'] = doc.id
            
            # Simple keyword filter (TODO: improve with full-text search)
            if keyword:
                if keyword.lower() in decision_data.get('title', '').lower() or \
                   keyword.lower() in decision_data.get('rationale', '').lower():
                    results.append(decision_data)
            else:
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
