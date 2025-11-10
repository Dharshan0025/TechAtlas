from flask import Blueprint, request, jsonify
import traceback
import logging

query_bp = Blueprint('query', __name__)
logger = logging.getLogger(__name__)

@query_bp.route('/query-decisions', methods=['POST'])
def query_decisions():
    """Query decisions using RAG engine"""
    try:
        # Validate request has JSON
        if not request.is_json:
            logger.warning("Non-JSON request received")
            return jsonify({
                "success": False,
                "error": "Invalid request",
                "message": "Request must be JSON",
                "status": 400
            }), 400
        
        data = request.get_json()
        user_query = data.get('query', '')
        user = data.get('user', 'anonymous')
        
        # Validate query field (including whitespace-only)
        if not user_query or not user_query.strip():
            logger.warning("Empty or whitespace-only query received")
            return jsonify({
                "success": False,
                "error": "Query is required",
                "message": "Query field cannot be empty",
                "status": 400
            }), 400
        
        logger.info(f"Processing query from user: {user}")
        logger.debug(f"Query text: {user_query[:100]}...")
        
        # Import and initialize RAG engine
        try:
            from services.rag_engine import RAGEngine
            rag_engine = RAGEngine()
        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Service initialization failed",
                "message": "RAG engine could not be initialized",
                "status": 500
            }), 500
        
        # Execute query
        try:
            result = rag_engine.query(user_query)
            logger.info(f"Query completed successfully with {len(result.get('sources', []))} sources")
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Query processing failed",
                "message": str(e),
                "status": 500
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in query_decisions: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "status": 500
        }), 500
