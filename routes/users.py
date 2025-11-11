from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import logging
from collections import defaultdict

users_bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)

@users_bp.route('/users/<user_email>', methods=['GET'])
def user_profile(user_email):
    """Get user profile and decision stats"""
    try:
        db = firestore.client()
        
        # Get decisions owned by user
        owned_query = db.collection('decisions').where('owner', '==', user_email)
        owned_decisions = list(owned_query.stream())
        
        # Get decisions where user participated
        all_decisions = db.collection('decisions').stream()
        participated_decisions = []
        
        for doc in all_decisions:
            decision_data = doc.to_dict()
            participants = decision_data.get('participants', [])
            if user_email in participants and decision_data.get('owner') != user_email:
                participated_decisions.append(doc)
        
        # Extract expertise areas from decision titles
        expertise_areas = set()
        for doc in owned_decisions:
            title = doc.to_dict().get('title', '')
            # Simple keyword extraction (TODO: improve with NLP)
            keywords = title.lower().split()
            expertise_areas.update(keywords[:3])  # Take first 3 words as topics
        
        return jsonify({
            "success": True,
            "user": {
                "email": user_email,
                "decisions_owned": len(owned_decisions),
                "decisions_participated": len(participated_decisions),
                "expertise_areas": list(expertise_areas)[:10],
                "total_contributions": len(owned_decisions) + len(participated_decisions)
            },
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get user profile",
            "message": str(e),
            "status": 500
        }), 500


@users_bp.route('/expertise', methods=['GET'])
def expertise_map():
    """Get expertise distribution across topics"""
    try:
        db = firestore.client()
        all_decisions = db.collection('decisions').stream()
        
        # Map topics to experts
        topic_experts = defaultdict(set)
        
        for doc in all_decisions:
            decision_data = doc.to_dict()
            title = decision_data.get('title', '')
            owner = decision_data.get('owner', '')
            
            # Extract topics (simple word extraction)
            words = title.lower().split()
            for word in words[:5]:  # First 5 words as topics
                if len(word) > 3:  # Filter short words
                    topic_experts[word].add(owner)
        
        # Format response
        expertise = []
        for topic, experts in sorted(topic_experts.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
            expertise.append({
                "topic": topic,
                "experts": list(experts),
                "expert_count": len(experts)
            })
        
        return jsonify({
            "success": True,
            "count": len(expertise),
            "expertise_map": expertise,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting expertise map: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get expertise map",
            "message": str(e),
            "status": 500
        }), 500


@users_bp.route('/users/top-contributors', methods=['GET'])
def top_contributors():
    """Get most active decision makers"""
    try:
        limit = int(request.args.get('limit', 10))
        
        db = firestore.client()
        all_decisions = db.collection('decisions').stream()
        
        # Count decisions per user
        user_counts = defaultdict(int)
        user_data = defaultdict(lambda: {
            'owned': 0,
            'participated': 0,
            'completed': 0
        })
        
        for doc in all_decisions:
            decision_data = doc.to_dict()
            owner = decision_data.get('owner', '')
            participants = decision_data.get('participants', [])
            status = decision_data.get('status', '')
            
            if owner:
                user_data[owner]['owned'] += 1
                user_counts[owner] += 1
                if status == 'Completed':
                    user_data[owner]['completed'] += 1
            
            for participant in participants:
                if participant != owner:
                    user_data[participant]['participated'] += 1
                    user_counts[participant] += 0.5  # Weight participation less
        
        # Sort and format
        top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        contributors = []
        for user_email, score in top_users:
            contributors.append({
                "email": user_email,
                "contribution_score": score,
                "decisions_owned": user_data[user_email]['owned'],
                "decisions_participated": user_data[user_email]['participated'],
                "decisions_completed": user_data[user_email]['completed']
            })
        
        return jsonify({
            "success": True,
            "count": len(contributors),
            "top_contributors": contributors,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting top contributors: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get top contributors",
            "message": str(e),
            "status": 500
        }), 500


@users_bp.route('/knowledge-gaps', methods=['GET'])
def knowledge_gaps():
    """Identify single-owner decisions (knowledge silos)"""
    try:
        db = firestore.client()
        all_decisions = db.collection('decisions').stream()
        
        gaps = []
        for doc in all_decisions:
            decision_data = doc.to_dict()
            participants = decision_data.get('participants', [])
            
            # Single participant = knowledge silo
            if len(participants) <= 1:
                decision_data['id'] = doc.id
                decision_data['gap_type'] = 'single_owner'
                decision_data['risk_level'] = 'high'
                gaps.append(decision_data)
        
        return jsonify({
            "success": True,
            "count": len(gaps),
            "knowledge_gaps": gaps,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting knowledge gaps: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get knowledge gaps",
            "message": str(e),
            "status": 500
        }), 500
