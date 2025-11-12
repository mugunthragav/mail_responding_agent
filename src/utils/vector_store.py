import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from .logger import get_logger

logger = get_logger(__name__)

class VectorMemory:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="/app/data/chroma")
        self.collection = self.client.get_or_create_collection("email_feedback")
        self.embeddings = OpenAIEmbeddings()

    def add_feedback(self, email_id: str, feedback: str, draft: str):
        embedding = self.embeddings.embed_query(feedback)
        self.collection.add(
            ids=[email_id],
            embeddings=[embedding],
            metadatas=[{"feedback": feedback, "draft": draft}]
        )
        logger.info(f"Feedback stored for email {email_id}")

    def retrieve_similar(self, query: str, n: int = 2):
        embedding = self.embeddings.embed_query(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n
        )
        return results['metadatas'][0] if results['metadatas'] else []