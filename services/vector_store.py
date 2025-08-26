from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import uuid
from config.settings import settings

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
    
    def create_collection(self, collection_name: str, vector_size: int = 3072):
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
        except Exception as e:
            raise Exception(f"Failed to create collection: {str(e)}")
    
    def store_embeddings(self, collection_name: str, texts: List[str], embeddings: List[List[float]], document_id: str):
        points = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    "document_id": document_id,
                    "chunk_index": i
                }
            )
            points.append(point)
        
        try:
            self.client.upsert(collection_name=collection_name, points=points)
        except Exception as e:
            raise Exception(f"Failed to store embeddings: {str(e)}")
    
    def search_similar(self, collection_name: str, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            return [
                {
                    "text": hit.payload["text"],
                    "score": hit.score,
                    "document_id": hit.payload["document_id"]
                }
                for hit in search_result
            ]
        except Exception as e:
            raise Exception(f"Failed to search vectors: {str(e)}")