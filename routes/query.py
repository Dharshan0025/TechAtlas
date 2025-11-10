from flask import Blueprint, request, jsonify
from services.rag_engine import RAGEngine

query_bp = Blueprint('query', __name__)
rag_engine = RAGEngine()

@query_bp.route('/query-decisions', methods=['POST'])
def query_decisions():
    data = request.json
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({"error": "Query is required"}), 400
    
    result = rag_engine.query(user_query)
    
    return jsonify(result)
