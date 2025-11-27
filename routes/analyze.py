from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timezone
from services.feasibility_analyzer import FeasibilityAnalyzer
from services.vector_store import VectorStore
from services.embedder import GeminiEmbedder

analyze_bp = Blueprint('analyze', __name__)
logger = logging.getLogger(__name__)

# Initialize services with lazy loading
feasibility_analyzer = None
vector_store = None
embedder = None

def get_feasibility_analyzer():
    global feasibility_analyzer
    if feasibility_analyzer is None:
        feasibility_analyzer = FeasibilityAnalyzer()
    return feasibility_analyzer

def get_vector_store():
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store

def get_embedder():
    global embedder
    if embedder is None:
        embedder = GeminiEmbedder()
    return embedder

@analyze_bp.route('/analyze-decision', methods=['POST'])
def analyze_decision():
    """
    Perform AI-powered feasibility analysis on a decision
    
    Input: title, rationale, context
    Output: strengths, risks, alternatives, past_decisions, recommendation, feasibility_score
    """
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON",
                "status": 400
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'rationale']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": "Missing required fields",
                "missing_fields": missing_fields,
                "status": 400
            }), 400
        
        title = data['title']
        rationale = data['rationale']
        context = data.get('context', '')
        
        logger.info(f"Analyzing decision: {title}")
        
        # Find similar past decisions
        embedder_instance = get_embedder()
        embedding_text = f"{title}\n{rationale}"
        embedding = embedder_instance.embed(embedding_text)
        
        vector_store_instance = get_vector_store()
        similar_decisions_raw = vector_store_instance.query(embedding, top_k=3)
        
        past_decisions = []
        for item in similar_decisions_raw:
            past_decisions.append({
                "title": item['metadata']['title'],
                "status": item['metadata'].get('status', 'Unknown'),
                "similarity_score": item['score']
            })

        # Perform analysis
        analyzer = get_feasibility_analyzer()
        analysis = analyzer.analyze_with_history(title, rationale, context, past_decisions)
        analysis['analyzed_at'] = datetime.now(timezone.utc).isoformat()

        return jsonify({
            "success": True,
            "analysis": analysis,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_decision: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Analysis failed",
            "message": str(e),
            "status": 500
        }), 500


@analyze_bp.route('/decisions/<decision_id>/analyze', methods=['POST'])
def analyze_saved_decision(decision_id):
    """
    Analyze an existing saved decision by ID
    """
    try:
        from firebase_admin import firestore
        db = firestore.client()
        
        # 1. Fetch decision
        doc_ref = db.collection('decisions').document(decision_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                "success": False,
                "error": "Decision not found",
                "status": 404
            }), 404
            
        decision_data = doc.to_dict()
        title = decision_data.get('title')
        rationale = decision_data.get('rationale')
        
        # 2. Analyze
        # Find similar past decisions for context
        embedder_instance = get_embedder()
        embedding_text = f"{title}\n{rationale}"
        embedding = embedder_instance.embed(embedding_text)
        
        vector_store_instance = get_vector_store()
        similar_decisions_raw = vector_store_instance.query(embedding, top_k=3)
        
        past_decisions = []
        for item in similar_decisions_raw:
            # Exclude self if found
            if item['id'] == decision_id:
                continue
                
            past_decisions.append({
                "title": item['metadata']['title'],
                "status": item['metadata'].get('status', 'Unknown'),
                "similarity_score": item['score']
            })

        analyzer = get_feasibility_analyzer()
        analysis = analyzer.analyze_with_history(title, rationale, "", past_decisions)
        analysis['analyzed_at'] = datetime.now(timezone.utc).isoformat()
        
        # 3. Update decision with analysis
        doc_ref.update({
            'analysis': analysis,
            'last_analyzed_at': analysis['analyzed_at']
        })
        
        return jsonify({
            "success": True,
            "decision_id": decision_id,
            "analysis": analysis,
            "status": 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing saved decision: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Analysis failed",
            "message": str(e),
            "status": 500
        }), 500
