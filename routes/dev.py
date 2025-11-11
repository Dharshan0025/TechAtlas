from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from models.decision import Decision
import logging
from datetime import datetime, timezone, timedelta
import random

dev_bp = Blueprint('dev', __name__)
logger = logging.getLogger(__name__)

# Sample data for seeding
SAMPLE_TITLES = [
    "Database Migration to PostgreSQL",
    "Microservices Architecture Adoption",
    "Cloud Provider Selection",
    "API Gateway Implementation",
    "CI/CD Pipeline Upgrade",
    "Security Audit Framework",
    "Performance Optimization Strategy",
    "Mobile App Development Framework",
    "Data Backup Strategy",
    "Monitoring Tool Selection"
]

SAMPLE_OWNERS = [
    "priya@company.com",
    "rahul@company.com",
    "sarah@company.com",
    "john@company.com",
    "alice@company.com"
]

SAMPLE_CHANNELS = [
    "tech-team",
    "engineering",
    "devops",
    "backend-team",
    "frontend-team"
]

SAMPLE_STATUSES = ["Open", "In Progress", "Completed", "Archived"]


@dev_bp.route('/dev/seed-data', methods=['POST'])
def seed_sample_data():
    """Populate database with sample decisions (dev only)"""
    try:
        if not request.is_json:
            count = 10
        else:
            data = request.get_json()
            count = data.get('count', 10)
        
        db = firestore.client()
        created_decisions = []
        
        for i in range(count):
            # Generate random decision data
            title = random.choice(SAMPLE_TITLES)
            owner = random.choice(SAMPLE_OWNERS)
            channel = random.choice(SAMPLE_CHANNELS)
            status = random.choice(SAMPLE_STATUSES)
            
            # Random participants
            num_participants = random.randint(1, 4)
            participants = random.sample(SAMPLE_OWNERS, num_participants)
            if owner not in participants:
                participants.append(owner)
            
            # Random dates
            days_ago = random.randint(1, 90)
            created_at = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
            
            days_ahead = random.randint(7, 60)
            due_date = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            decision = Decision(
                title=f"{title} #{i+1}",
                owner=owner,
                rationale=f"Sample rationale for {title}. This is a test decision created for development purposes.",
                due_date=due_date,
                thread_link=f"https://cliq.zoho.com/thread/{random.randint(10000, 99999)}",
                participants=participants,
                channel_id=channel
            )
            
            # Override created_at and status
            decision_dict = decision.to_dict()
            decision_dict['created_at'] = created_at
            decision_dict['status'] = status
            
            # Save to Firestore
            db.collection('decisions').document(decision.decision_id).set(decision_dict)
            created_decisions.append(decision.decision_id)
            
            logger.info(f"Created sample decision: {decision.decision_id}")
        
        return jsonify({
            "success": True,
            "created_count": len(created_decisions),
            "decision_ids": created_decisions,
            "message": f"Successfully created {len(created_decisions)} sample decisions",
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error seeding data: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to seed data",
            "message": str(e),
            "status": 500
        }), 500


@dev_bp.route('/dev/clear-data', methods=['DELETE'])
def clear_test_data():
    """Clear all test data (dev only)"""
    try:
        db = firestore.client()
        
        # Get all decisions
        decisions_ref = db.collection('decisions')
        decisions = decisions_ref.stream()
        
        deleted_count = 0
        for doc in decisions:
            doc.reference.delete()
            deleted_count += 1
        
        logger.warning(f"Deleted {deleted_count} decisions from database")
        
        return jsonify({
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} decisions",
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to clear data",
            "message": str(e),
            "status": 500
        }), 500


@dev_bp.route('/dev/validate-embeddings', methods=['POST'])
def validate_embeddings():
    """Test embedding generation (dev only)"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON",
                "status": 400
            }), 400
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Text is required",
                "status": 400
            }), 400
        
        # Import embedder
        from services.embedder import GeminiEmbedder
        
        embedder = GeminiEmbedder()
        embedding = embedder.embed(text)
        
        return jsonify({
            "success": True,
            "text": text,
            "embedding_dimension": len(embedding),
            "embedding_sample": embedding[:10],  # First 10 values
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error validating embeddings: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to validate embeddings",
            "message": str(e),
            "status": 500
        }), 500


@dev_bp.route('/dev/stats', methods=['GET'])
def dev_stats():
    """Get development environment statistics"""
    try:
        db = firestore.client()
        
        # Count decisions
        decisions = list(db.collection('decisions').stream())
        total_decisions = len(decisions)
        
        # Count by status
        status_counts = {}
        for doc in decisions:
            status = doc.to_dict().get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return jsonify({
            "success": True,
            "stats": {
                "total_decisions": total_decisions,
                "status_breakdown": status_counts,
                "environment": "development"
            },
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting dev stats: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get dev stats",
            "message": str(e),
            "status": 500
        }), 500
