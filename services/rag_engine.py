import google.generativeai as genai
from config import Config
from services.embedder import GeminiEmbedder
from services.vector_store import VectorStore

genai.configure(api_key=Config.GEMINI_API_KEY)

class RAGEngine:
    def __init__(self):
        self.embedder = GeminiEmbedder()
        self.vector_store = VectorStore()
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def query(self, user_query: str) -> dict:
        """
        RAG pipeline: Retrieve → Augment → Generate
        """
        try:
            # 1. Convert query to embedding
            print(f"Embedding query: {user_query}")
            query_embedding = self.embedder.embed_query(user_query)
            print(f"Query embedding generated: {len(query_embedding)} dimensions")
            
            # 2. Retrieve similar decisions
            print("Searching vector store...")
            matches = self.vector_store.query(query_embedding, top_k=3)
            print(f"Found {len(matches)} matches")
        except Exception as e:
            print(f"Error in RAG query: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        if not matches:
            return {
                "answer": "I couldn't find any relevant decisions in the knowledge base.",
                "sources": []
            }
        
        # 3. Build context from retrieved decisions
        context = "Here are the relevant past decisions:\n\n"
        sources = []
        
        for i, match in enumerate(matches, 1):
            metadata = match['metadata']
            context += f"Decision {i}:\n"
            context += f"Title: {metadata['title']}\n"
            context += f"Rationale: {metadata['rationale']}\n"
            context += f"Owner: {metadata['owner']}\n"
            context += f"Date: {metadata['created_at']}\n\n"
            
            sources.append({
                "decision_id": metadata.get('decision_id', metadata.get('id', '')),
                "title": metadata['title'],
                "owner": metadata['owner'],
                "thread_link": metadata.get('thread_link', ''),
                "relevance_score": match['score']
            })
        
        # 4. Generate answer with Gemini
        prompt = f"""
        You are TechAtlas, a helpful assistant that answers questions about past team decisions.
        
        Context (past decisions):
        {context}
        
        User Question: {user_query}
        
        Instructions:
        - Answer based ONLY on the provided decisions
        - Be concise and natural
        - Always cite the decision title and owner
        - If the context doesn't contain the answer, say so
        
        Answer:
        """
        
        response = self.model.generate_content(prompt)
        answer = response.text
        
        return {
            "answer": answer,
            "sources": sources
        }
