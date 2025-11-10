from flask import Blueprint, request, jsonify, current_app
import traceback
from functools import wraps
from typing import Dict, Any, Tuple, Optional
import logging

# Create blueprint
detect_bp = Blueprint('detect', __name__)
logger = logging.getLogger(__name__)

def validate_json_request(required_fields: list = None) -> callable:
    """Decorator to validate JSON request and required fields."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check if request has JSON data
            if not request.is_json:
                return jsonify({
                    "error": "Invalid request",
                    "message": "Request must be JSON",
                    "status": 400
                }), 400
            
            data = request.get_json()
            
            # Check for required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        "error": "Missing required fields",
                        "missing_fields": missing_fields,
                        "status": 400
                    }), 400
                
                # Check for empty required fields (including whitespace-only)
                empty_fields = []
                for field in required_fields:
                    value = data.get(field)
                    if not value or (isinstance(value, str) and not value.strip()):
                        empty_fields.append(field)
                
                if empty_fields:
                    return jsonify({
                        "error": "Empty field values",
                        "empty_fields": empty_fields,
                        "status": 400
                    }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

@detect_bp.route('/detect-decision', methods=['POST'])
@validate_json_request(required_fields=['message'])
def detect_decision() -> Tuple[Dict[str, Any], int]:
    """
    Detect if the input message contains a decision.
    
    Request JSON format:
    {
        "message": "The decision text to analyze",
        "user": "user@example.com",
        "channel_id": "channel-123"
    }
    
    Response format (success):
    {
        "success": true,
        "is_decision": true,
        "confidence": 0.85,
        "suggested_title": "Decision about migration",
        "status": 200
    }
    
    Response format (error):
    {
        "success": false,
        "error": "Error message",
        "status": 400
    }
    """
    try:
        data = request.get_json()
        message = data['message']
        user = data.get('user', 'anonymous')
        channel_id = data.get('channel_id', 'unknown')
        
        logger.info(f"Processing detect-decision request from user: {user}, channel: {channel_id}")
        logger.debug(f"Message: {message[:100]}...")
        
        # Import here to avoid circular imports
        from services.detector import DecisionDetector
        
        try:
            detector = DecisionDetector()
            is_decision, confidence, title = detector.detect(message)
            
            logger.info(
                f"Detection result - is_decision: {is_decision}, "
                f"confidence: {confidence:.2f}, title: {title}"
            )
            
            return jsonify({
                "success": True,
                "is_decision": is_decision,
                "confidence": float(confidence),
                "suggested_title": title,
                "status": 200
            }), 200
            
        except ImportError as ie:
            logger.error(f"Import error in detect_decision: {str(ie)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Service configuration error",
                "message": "Decision detection service is not properly configured",
                "status": 500
            }), 500
            
        except Exception as e:
            logger.error(f"Error in decision detection: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Decision detection failed",
                "message": str(e),
                "status": 500
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in detect_decision: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "status": 500
        }), 500
