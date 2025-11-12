from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon if not already present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except Exception:
    nltk.download('vader_lexicon')

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

@analytics_bp.route('/analytics/trends', methods=['GET'])
def decision_trends():
    """Get decision-making trends over time"""
    try:
        period = request.args.get('period', 'month')  # week/month/year
        
        db = firestore.client()
        all_decisions = db.collection('decisions').stream()
        
        # Group decisions by time period
        trends = defaultdict(int)
        
        for doc in all_decisions:
            decision_data = doc.to_dict()
            created_at = decision_data.get('created_at', '')
            
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    if period == 'week':
                        key = dt.strftime('%Y-W%U')
                    elif period == 'month':
                        key = dt.strftime('%Y-%m')
                    else:  # year
                        key = dt.strftime('%Y')
                    
                    trends[key] += 1
                except:
                    continue
        
        # Format response
        timeline = [
            {"period": period_key, "count": count}
            for period_key, count in sorted(trends.items())
        ]
        
        return jsonify({
            "success": True,
            "period": period,
            "timeline": timeline,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get trends",
            "message": str(e),
            "status": 500
        }), 500


@analytics_bp.route('/analytics/topics', methods=['GET'])
def topic_analysis():
    """Get most discussed decision topics"""
    try:
        db = firestore.client()
        all_decisions = db.collection('decisions').stream()
        
        # Extract topics from titles
        topic_counts = defaultdict(int)
        
        for doc in all_decisions:
            decision_data = doc.to_dict()
            title = decision_data.get('title', '').lower()
            
            # Simple word extraction
            words = title.split()
            for word in words:
                if len(word) > 4:  # Filter short words
                    topic_counts[word] += 1
        
        # Sort by frequency and perform sentiment analysis
        sia = SentimentIntensityAnalyzer()
        topics = []
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
            sentiment_score = sia.polarity_scores(topic)['compound']
            if sentiment_score >= 0.05:
                sentiment = "positive"
            elif sentiment_score <= -0.05:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            topics.append({
                "topic": topic,
                "frequency": count,
                "sentiment": sentiment
            })
        
        return jsonify({
            "success": True,
            "count": len(topics),
            "topics": topics,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting topic analysis: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get topic analysis",
            "message": str(e),
            "status": 500
        }), 500


@analytics_bp.route('/analytics/velocity', methods=['GET'])
def decision_velocity():
    """Average time from decision to completion"""
    try:
        db = firestore.client()
        completed_decisions = db.collection('decisions').where('status', '==', 'Completed').stream()
        
        completion_times = []
        
        for doc in completed_decisions:
            decision_data = doc.to_dict()
            created_at = decision_data.get('created_at', '')
            status_updated_at = decision_data.get('status_updated_at', '')
            
            if created_at and status_updated_at:
                try:
                    created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    completed = datetime.fromisoformat(status_updated_at.replace('Z', '+00:00'))
                    
                    days = (completed - created).days
                    completion_times.append(days)
                except:
                    continue
        
        if completion_times:
            avg_time = sum(completion_times) / len(completion_times)
            fastest = min(completion_times)
            slowest = max(completion_times)
        else:
            avg_time = 0
            fastest = 0
            slowest = 0
        
        return jsonify({
            "success": True,
            "velocity": {
                "avg_completion_time_days": round(avg_time, 2),
                "fastest_days": fastest,
                "slowest_days": slowest,
                "sample_size": len(completion_times)
            },
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting velocity: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to get velocity",
            "message": str(e),
            "status": 500
        }), 500
