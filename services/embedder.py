import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

class GeminiEmbedder:
    def __init__(self):
        self.model = Config.GEMINI_EMBEDDING_MODEL
    
    def embed(self, text: str) -> list[float]:
        """
        Generate embedding vector for text using Gemini
        """
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    
    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for search query
        """
        result = genai.embed_content(
            model=self.model,
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']
