import pinecone
from config import Config

class VectorStore:
    def __init__(self):
        pinecone.init(api_key=Config.PINECONE_API_KEY, environment=Config.PINECONE_ENVIRONMENT)
        self.index_name = Config.PINECONE_INDEX_NAME
        
        # Create index if doesn't exist
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                dimension=768,  # Gemini embedding dimension
                metric='cosine'
            )
        
        self.index = pinecone.Index(self.index_name)
    
    def upsert(self, decision_id: str, embedding: list[float], metadata: dict):
        """Store decision vector"""
        self.index.upsert(vectors=[{
            'id': decision_id,
            'values': embedding,
            'metadata': metadata
        }])
    
    def query(self, query_embedding: list[float], top_k: int = 3):
        """Search for similar decisions"""
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return results['matches']
