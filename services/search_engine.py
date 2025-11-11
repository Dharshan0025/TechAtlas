"""
Search Engine Service
Provides comprehensive search capabilities
"""

from firebase_admin import firestore
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Unified search engine for decisions
    """
    
    def __init__(self):
        """Initialize the Search Engine"""
        self.db = firestore.client()
        logger.info("SearchEngine initialized successfully")
    
    def keyword_search(self, keyword: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Keyword-based search in titles and rationales
        
        Args:
            keyword: Search keyword
            filters: Optional filters (status, owner, channel_id)
        
        Returns:
            List of matching decisions
        """
        try:
            query = self.db.collection('decisions')
            
            # Apply filters
            if filters:
                if 'status' in filters:
                    query = query.where('status', '==', filters['status'])
                if 'owner' in filters:
                    query = query.where('owner', '==', filters['owner'])
                if 'channel_id' in filters:
                    query = query.where('channel_id', '==', filters['channel_id'])
            
            # Get all matching documents
            results = []
            keyword_lower = keyword.lower()
            
            for doc in query.stream():
                data = doc.to_dict()
                title = data.get('title', '').lower()
                rationale = data.get('rationale', '').lower()
                
                # Check if keyword exists in title or rationale
                if keyword_lower in title or keyword_lower in rationale:
                    data['id'] = doc.id
                    
                    # Calculate relevance score
                    score = 0
                    if keyword_lower in title:
                        score += 10
                    if keyword_lower in rationale:
                        score += 5
                    
                    data['relevance_score'] = score
                    results.append(data)
            
            # Sort by relevance
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"Keyword search for '{keyword}' found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            return []
    
    def filter_search(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter-based search
        
        Args:
            filters: Dictionary of filters
                - status: Decision status
                - owner: Owner email
                - channel_id: Channel ID
                - date_from: Start date (ISO format)
                - date_to: End date (ISO format)
                - risk_level: Risk level (Low/Medium/High)
        
        Returns:
            List of matching decisions
        """
        try:
            query = self.db.collection('decisions')
            
            # Apply Firestore filters
            if 'status' in filters:
                query = query.where('status', '==', filters['status'])
            if 'owner' in filters:
                query = query.where('owner', '==', filters['owner'])
            if 'channel_id' in filters:
                query = query.where('channel_id', '==', filters['channel_id'])
            
            # Get results
            results = []
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Apply additional filters (not supported by Firestore directly)
                if 'date_from' in filters:
                    if data.get('created_at', '') < filters['date_from']:
                        continue
                
                if 'date_to' in filters:
                    if data.get('created_at', '') > filters['date_to']:
                        continue
                
                if 'risk_level' in filters:
                    if data.get('risk_level', '') != filters['risk_level']:
                        continue
                
                results.append(data)
            
            logger.info(f"Filter search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Filter search failed: {str(e)}")
            return []
    
    def semantic_search(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Semantic search using vector similarity
        
        Args:
            query_text: Natural language query
            top_k: Number of top results to return
        
        Returns:
            List of semantically similar decisions
        """
        try:
            # TODO: Implement actual vector search
            # For now, fall back to keyword search
            logger.warning("Semantic search not fully implemented, using keyword search")
            
            # Extract keywords from query
            keywords = query_text.lower().split()
            
            # Search for each keyword
            all_results = {}
            for keyword in keywords:
                if len(keyword) > 3:
                    results = self.keyword_search(keyword)
                    for result in results:
                        doc_id = result['id']
                        if doc_id in all_results:
                            all_results[doc_id]['relevance_score'] += result['relevance_score']
                        else:
                            all_results[doc_id] = result
            
            # Sort and return top K
            sorted_results = sorted(
                all_results.values(),
                key=lambda x: x['relevance_score'],
                reverse=True
            )[:top_k]
            
            return sorted_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
    
    def advanced_search(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Advanced search combining multiple criteria
        
        Args:
            search_params: Dictionary with search parameters
                - query: Text query
                - filters: Filter dictionary
                - sort_by: Field to sort by
                - sort_order: 'asc' or 'desc'
                - limit: Maximum results
        
        Returns:
            List of matching decisions
        """
        try:
            query_text = search_params.get('query', '')
            filters = search_params.get('filters', {})
            sort_by = search_params.get('sort_by', 'created_at')
            sort_order = search_params.get('sort_order', 'desc')
            limit = search_params.get('limit', 50)
            
            # Start with filter search
            results = self.filter_search(filters)
            
            # Apply text search if query provided
            if query_text:
                keyword_results = self.keyword_search(query_text, filters)
                # Merge results
                result_ids = {r['id'] for r in results}
                for kr in keyword_results:
                    if kr['id'] not in result_ids:
                        results.append(kr)
            
            # Sort results
            reverse = (sort_order == 'desc')
            results.sort(
                key=lambda x: x.get(sort_by, ''),
                reverse=reverse
            )
            
            # Apply limit
            results = results[:limit]
            
            logger.info(f"Advanced search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Advanced search failed: {str(e)}")
            return []
    
    def suggest_search_terms(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        """
        Suggest search terms based on partial input
        
        Args:
            partial_query: Partial search query
            max_suggestions: Maximum number of suggestions
        
        Returns:
            List of suggested search terms
        """
        try:
            # Get all decisions
            decisions = list(self.db.collection('decisions').stream())
            
            # Extract unique terms from titles
            terms = set()
            partial_lower = partial_query.lower()
            
            for doc in decisions:
                title = doc.to_dict().get('title', '')
                words = title.split()
                
                for word in words:
                    if word.lower().startswith(partial_lower) and len(word) > 3:
                        terms.add(word.lower())
            
            # Return top suggestions
            suggestions = sorted(list(terms))[:max_suggestions]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Search suggestion failed: {str(e)}")
            return []
    
    def get_search_history(self, user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get search history for a user
        
        Args:
            user_email: User's email
            limit: Maximum history items
        
        Returns:
            List of recent searches
        """
        try:
            # TODO: Implement actual search history tracking
            logger.warning("Search history not implemented yet")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get search history: {str(e)}")
            return []
