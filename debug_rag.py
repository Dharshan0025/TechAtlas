from services.vector_store import VectorStore
from services.embedder import GeminiEmbedder
import numpy as np
import faiss

def debug_vector_store():
    vs = VectorStore()
    embedder = GeminiEmbedder()
    
    query = "database migration"
    embedding = embedder.embed_query(query)
    
    print(f"Index ntotal: {vs.index.ntotal}")
    
    # query manually
    query_np = np.array([embedding], dtype=np.float32)
    faiss.normalize_L2(query_np)
    
    distances, indices = vs.index.search(query_np, 3)
    
    print(f"Raw indices: {indices}")
    print(f"Raw distances: {distances}")
    
    matches = vs.query(embedding)
    print(f"Matches found: {len(matches)}")
    for m in matches:
        print(f"Match ID: {m['metadata'].get('id')}, Score: {m['score']}")

if __name__ == "__main__":
    debug_vector_store()
