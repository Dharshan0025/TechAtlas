from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import logging
from datetime import datetime, timezone

risk_bp = Blueprint('risk', __name__)
logger = logging.getLogger(__name__)

def calculate_risk_score(decision_data):
    """Calculate risk score for a decision"""
    risk_score = 0
    risk_factors = []
    
    # Factor 1: Number of participants (fewer = higher risk)
    participants = decision_data.get('participants', [])
    if len(participants) <= 1:
        risk_score += 8
        risk_factors.append("Single owner - knowledge silo")
    elif len(participants) == 2:
        risk_score += 5
        risk_factors.append("Limited participants")
    else:
        risk_score += 2
    
    # Factor 2: Due date proximity
    due_date = decision_data.get('due_date', '')
    if due_date:
        try:
            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_until = (due - now).days
            
            if days_until < 0:
                risk_score += 3
                risk_factors.append("Past due date")
            elif days_until < 7:
                risk_score += 2
                risk_factors.append("Due soon")
        except:
            pass
    
    # Factor 3: Status
    status = decision_data.get('status', 'Open')
    if status == 'Open':
        risk_score += 1
        risk_factors.append("Not started")
    
    # Normalize to 0-10 scale
    risk_score = min(risk_score, 10)
    
    # Determine risk level
    if risk_score >= 7:
        risk_level = "high"
    elif risk_score >= 4:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return risk_score, risk_level, risk_factors


@risk_bp.route('/assess-risk/<decision_id>', methods=['POST'])
def assess_risk(decision_id):
    """Re-calculate risk score for a decision"""
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
        
        decision_data = doc.to_dict()
        
        # Calculate risk
        risk_score, risk_level, risk_factors = calculate_risk_score(decision_data)
        
        # Update decision
        doc_ref.update({
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_assessed_at': datetime.now(timezone.utc).isoformat()
        })
        
        return jsonify({
            "success": True,
            "decision_id": decision_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to assess risk",
            "message": str(e),
            "status": 500
        }), 500


@risk_bp.route('/decisions/reassess-all-risks', methods=['POST'])
def reassess_all_risks():
    """Recalculate risk scores for all decisions"""
    try:
        db = firestore.client()
        all_decisions = db.collection('decisions').stream()
        
        updated_count = 0
        
        for doc in all_decisions:
            decision_data = doc.to_dict()
            risk_score, risk_level, risk_factors = calculate_risk_score(decision_data)
            
            doc.reference.update({
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_assessed_at': datetime.now(timezone.utc).isoformat()
            })
            
            updated_count += 1
        
        return jsonify({
            "success": True,
            "updated_count": updated_count,
            "message": f"Reassessed risk for {updated_count} decisions",
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error reassessing risks: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to reassess risks",
            "message": str(e),
            "status": 500
        }), 500
