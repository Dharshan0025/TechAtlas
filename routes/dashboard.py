from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import logging
from datetime import datetime, timezone, timedelta

dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Overview statistics for dashboard"""
    try:
        db = firestore.client()
        decisions_ref = db.collection('decisions')
        
        # Get all decisions
        all_decisions = list(decisions_ref.stream())
        total_decisions = len(all_decisions)
        
        # Count by status
        open_decisions = sum(1 for doc in all_decisions if doc.to_dict().get('status') == 'Open')
        in_progress = sum(1 for doc in all_decisions if doc.to_dict().get('status') == 'In Progress')
        completed = sum(1 for doc in all_decisions if doc.to_dict().get('status') == 'Completed')
        
        # Count high risk (risk_score >= 7)
        high_risk_count = sum(1 for doc in all_decisions if doc.to_dict().get('risk_score', 0) >= 7)
        
        # Recent decisions (last 30 days)
        thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        recent_count = sum(1 for doc in all_decisions 
                          if doc.to_dict().get('created_at', '') >= thirty_days_ago)
        
        return jsonify({
            "success": True,
            "stats": {
                "total_decisions": total_decisions,
                "open_decisions": open_decisions,
                "in_progress": in_progress,
                "completed": completed,
                "high_risk_count": high_risk_count,
                "recent_count": recent_count
            },
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get stats",
            "message": str(e),
            "status": 500
        }), 500


@dashboard_bp.route('/decisions/high-risk', methods=['GET'])
def high_risk_decisions():
    """Get decisions with risk_score >= 7"""
    try:
        db = firestore.client()
        
        # Query high risk decisions
        query = db.collection('decisions').where('risk_score', '>=', 7)
        
        decisions = []
        for doc in query.stream():
            decision_data = doc.to_dict()
            decision_data['id'] = doc.id
            decisions.append(decision_data)
        
        # Sort by risk score descending
        decisions.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
        
        return jsonify({
            "success": True,
            "count": len(decisions),
            "high_risk_decisions": decisions,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting high-risk decisions: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get high-risk decisions",
            "message": str(e),
            "status": 500
        }), 500


@dashboard_bp.route('/decisions/recent', methods=['GET'])
def recent_decisions():
    """Get decisions from last N days"""
    try:
        days = int(request.args.get('days', 30))
        
        db = firestore.client()
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # Get all decisions and filter by date
        all_decisions = db.collection('decisions').stream()
        
        recent = []
        for doc in all_decisions:
            decision_data = doc.to_dict()
            if decision_data.get('created_at', '') >= cutoff_date:
                decision_data['id'] = doc.id
                recent.append(decision_data)
        
        # Sort by created_at descending
        recent.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            "success": True,
            "count": len(recent),
            "days": days,
            "decisions": recent,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recent decisions: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get recent decisions",
            "message": str(e),
            "status": 500
        }), 500


@dashboard_bp.route('/decisions/by-owner/<owner_email>', methods=['GET'])
def decisions_by_owner(owner_email):
    """Get all decisions owned by a specific person"""
    try:
        db = firestore.client()
        query = db.collection('decisions').where('owner', '==', owner_email)
        
        decisions = []
        for doc in query.stream():
            decision_data = doc.to_dict()
            decision_data['id'] = doc.id
            decisions.append(decision_data)
        
        # Calculate stats
        total = len(decisions)
        open_count = sum(1 for d in decisions if d.get('status') == 'Open')
        completed_count = sum(1 for d in decisions if d.get('status') == 'Completed')
        
        return jsonify({
            "success": True,
            "owner": owner_email,
            "stats": {
                "total": total,
                "open": open_count,
                "completed": completed_count
            },
            "decisions": decisions,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting decisions by owner: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get decisions by owner",
            "message": str(e),
            "status": 500
        }), 500


@dashboard_bp.route('/decisions/by-channel/<channel_id>', methods=['GET'])
def decisions_by_channel(channel_id):
    """Get all decisions from a specific channel"""
    try:
        db = firestore.client()
        query = db.collection('decisions').where('channel_id', '==', channel_id)
        
        decisions = []
        for doc in query.stream():
            decision_data = doc.to_dict()
            decision_data['id'] = doc.id
            decisions.append(decision_data)
        
        return jsonify({
            "success": True,
            "channel_id": channel_id,
            "count": len(decisions),
            "decisions": decisions,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting decisions by channel: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get decisions by channel",
            "message": str(e),
            "status": 500
        }), 500


@dashboard_bp.route('/decisions/aging', methods=['GET'])
def aging_decisions():
    """Get decisions past due date or unreviewed"""
    try:
        days_threshold = int(request.args.get('days_threshold', 30))
        
        db = firestore.client()
        all_decisions = db.collection('decisions').stream()
        
        aging = []
        now = datetime.now(timezone.utc).isoformat()
        
        for doc in all_decisions:
            decision_data = doc.to_dict()
            due_date = decision_data.get('due_date', '')
            
            # Check if past due or old
            if due_date and due_date < now:
                decision_data['id'] = doc.id
                decision_data['aging_reason'] = 'past_due'
                aging.append(decision_data)
        
        return jsonify({
            "success": True,
            "count": len(aging),
            "aging_decisions": aging,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting aging decisions: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get aging decisions",
            "message": str(e),
            "status": 500
        }), 500


@dashboard_bp.route('/decisions/upcoming-due', methods=['GET'])
def upcoming_due_dates():
    """Get decisions due soon"""
    try:
        days_ahead = int(request.args.get('days_ahead', 7))
        
        db = firestore.client()
        all_decisions = db.collection('decisions').stream()
        
        now = datetime.now(timezone.utc)
        future_date = (now + timedelta(days=days_ahead)).isoformat()
        now_iso = now.isoformat()
        
        upcoming = []
        for doc in all_decisions:
            decision_data = doc.to_dict()
            due_date = decision_data.get('due_date', '')
            
            if now_iso <= due_date <= future_date:
                decision_data['id'] = doc.id
                decision_data['days_until_due'] = (
                    datetime.fromisoformat(due_date.replace('Z', '+00:00')) - now
                ).days
                upcoming.append(decision_data)
        
        # Sort by due date
        upcoming.sort(key=lambda x: x.get('due_date', ''))
        
        return jsonify({
            "success": True,
            "count": len(upcoming),
            "days_ahead": days_ahead,
            "upcoming_decisions": upcoming,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting upcoming due dates: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get upcoming due dates",
            "message": str(e),
            "status": 500
        }), 500
