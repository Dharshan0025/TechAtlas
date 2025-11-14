import faiss
import numpy as np
import pickle
import os
from pathlib import Path
import logging

class VectorStore:
    def __init__(self):
        self.dimension = 768  # Gemini embedding dimension
        self.index_path = Path('data/faiss_index.bin')
        self.metadata_path = Path('data/metadata.pkl')
        
        # Create data directory if it doesn't exist
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create FAISS index
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'rb') as f:
                self.metadata_store = pickle.load(f)
        else:
            # Create new index with cosine similarity
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product for cosine
            self.metadata_store = {}
            self._save()
    
    def _save(self):
        """Save index and metadata to disk"""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata_store, f)
    
    def upsert(self, decision_id: str, embedding: list[float], metadata: dict):
        """Store decision vector"""
        # Normalize embedding for cosine similarity
        embedding_np = np.array([embedding], dtype=np.float32)
        faiss.normalize_L2(embedding_np)
        
        # Add to index
        self.index.add(embedding_np)
        
        # Store metadata with the index position
        idx = self.index.ntotal - 1
        self.metadata_store[idx] = {
            'id': decision_id,
            **metadata
        }
        
        self._save()
    
    def query(self, query_embedding: list[float], top_k: int = 3):
        """Search for similar decisions"""
        try:
            # Validate index
            if not hasattr(self, 'index') or self.index is None or not hasattr(self.index, 'ntotal'):
                logging.getLogger(__name__).warning("FAISS index not initialized")
                return []

            if self.index.ntotal == 0:
                logging.getLogger(__name__).warning("FAISS index is empty")
                return []

            # Cap k to available items
            safe_k = min(max(int(top_k), 1), self.index.ntotal)
            if safe_k <= 0:
                return []

            # Normalize query embedding
            query_np = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_np)

            # Search
            distances, indices = self.index.search(query_np, safe_k)

            # Format results
            matches = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx != -1 and idx in self.metadata_store:
                    matches.append({
                        'score': float(dist),
                        'metadata': self.metadata_store[idx]
                    })

            return matches
        except Exception as e:
            logging.getLogger(__name__).error(f"Error in vector store query: {str(e)}")
            return []
