from flask import Blueprint, request, jsonify
from services.detector import DecisionDetector

detect_bp = Blueprint('detect', __name__)
detector = DecisionDetector()

@detect_bp.route('/detect-decision', methods=['POST'])
def detect_decision():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    is_decision, confidence, title = detector.detect(message)
    
    return jsonify({
        "is_decision": is_decision,
        "confidence": confidence,
        "suggested_title": title
    })
