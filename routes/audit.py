from flask import Blueprint, request, jsonify, Response
from firebase_admin import firestore
import logging
from datetime import datetime, timezone
import csv
import json
from io import StringIO
from services.audit_logger import AuditLogger
from services.notification_manager import NotificationManager

audit_bp = Blueprint('audit', __name__)
logger = logging.getLogger(__name__)

# Initialize services with lazy loading
audit_logger = None
notification_manager = None

def get_audit_logger():
    global audit_logger
    if audit_logger is None:
        audit_logger = AuditLogger()
    return audit_logger

def get_notification_manager():
    global notification_manager
    if notification_manager is None:
        notification_manager = NotificationManager()
    return notification_manager

@audit_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get system audit trail"""
    try:
        # Query parameters
        user = request.args.get('user')
        action_type = request.args.get('action_type')
        limit = int(request.args.get('limit', 100))
        
        filters = {}
        if user:
            filters['user'] = user
        if action_type:
            filters['action'] = action_type
            
        audit = get_audit_logger()
        logs = audit.get_audit_logs(filters=filters, limit=limit)
        
        return jsonify({
            "success": True,
            "count": len(logs),
            "audit_logs": logs,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get audit logs",
            "message": str(e),
            "status": 500
        }), 500


@audit_bp.route('/export/decisions', methods=['GET'])
def export_decisions():
    """Export decisions as CSV/JSON"""
    try:
        export_format = request.args.get('format', 'json')
        status_filter = request.args.get('status')
        owner_filter = request.args.get('owner')
        
        db = firestore.client()
        query = db.collection('decisions')
        
        # Apply filters
        if status_filter:
            query = query.where('status', '==', status_filter)
        if owner_filter:
            query = query.where('owner', '==', owner_filter)
        
        # Get decisions
        decisions = []
        for doc in query.stream():
            decision_data = doc.to_dict()
            decision_data['id'] = doc.id
            decisions.append(decision_data)
        
        if export_format == 'csv':
            # Create CSV
            output = StringIO()
            if decisions:
                fieldnames = ['id', 'title', 'owner', 'status', 'created_at', 'due_date', 'risk_score']
                writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(decisions)
            
            csv_data = output.getvalue()
            
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=decisions_{datetime.now().strftime("%Y%m%d")}.csv'
                }
            )
        else:
            # Return JSON
            return Response(
                json.dumps(decisions, indent=2),
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename=decisions_{datetime.now().strftime("%Y%m%d")}.json'
                }
            )
        
    except Exception as e:
        logger.error(f"Error exporting decisions: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to export decisions",
            "message": str(e),
            "status": 500
        }), 500


@audit_bp.route('/reminders/send', methods=['POST'])
def send_reminder():
    """Trigger reminder for a decision"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON",
                "status": 400
            }), 400
        
        data = request.get_json()
        decision_id = data.get('decision_id')
        recipient_email = data.get('recipient_email')
        
        if not decision_id or not recipient_email:
            return jsonify({
                "success": False,
                "error": "decision_id and recipient_email are required",
                "status": 400
            }), 400
            
        # Get decision data
        db = firestore.client()
        doc_ref = db.collection('decisions').document(decision_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                "success": False,
                "error": "Decision not found",
                "status": 404
            }), 404
            
        decision_data = doc.to_dict()
        
        # Send reminder
        manager = get_notification_manager()
        result = manager.send_due_date_reminder(decision_data, recipient_email)
        
        if result.get('success'):
            return jsonify({
                "success": True,
                "decision_id": decision_id,
                "recipient": recipient_email,
                "reminder_sent_at": result.get('sent_at'),
                "status": 200
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to send reminder",
                "message": result.get('error'),
                "status": 500
            }), 500
        
    except Exception as e:
        logger.error(f"Error sending reminder: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to send reminder",
            "message": str(e),
            "status": 500
        }), 500
