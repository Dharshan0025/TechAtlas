from flask import Blueprint, request, jsonify
import traceback

query_bp = Blueprint('query', __name__)

@query_bp.route('/query-decisions', methods=['POST'])
def query_decisions():
    try:
        # Import and initialize RAG engine here
        from services.rag_engine import RAGEngine
        rag_engine = RAGEngine()
        
        print("DEBUG: Query endpoint called")
        data = request.json
        print(f"DEBUG: Request data: {data}")
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"error": "Query is required"}), 400
        
        print(f"DEBUG: Processing query: {user_query}")
        result = rag_engine.query(user_query)
        print(f"DEBUG: Query result: {result}")
        
        return jsonify(result)
    except Exception as e:
        print(f"ERROR in query_decisions: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
