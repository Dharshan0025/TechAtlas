from flask import Blueprint, request, jsonify
import traceback

detect_bp = Blueprint('detect', __name__)

@detect_bp.route('/detect-decision', methods=['POST'])
def detect_decision():
    try:
        # Import and initialize detector here
        from services.detector import DecisionDetector
        detector = DecisionDetector()
        
        data = request.json
        message = data.get('message', '')

        if not message:
            return jsonify({"error": "Message is required"}), 400

        print(f"DEBUG: Detecting decision for message: {message[:50]}...")
        is_decision, confidence, title = detector.detect(message)
        print(f"DEBUG: Detection result: is_decision={is_decision}, confidence={confidence}, title={title}")

        return jsonify({
            "is_decision": is_decision,
            "confidence": confidence,
            "suggested_title": title
        })
    except Exception as e:
        print(f"ERROR in detect_decision: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
