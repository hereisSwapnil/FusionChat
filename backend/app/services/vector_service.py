from qdrant_client.models import PointStruct
from app.db.qdrant import QdrantDBClient
from app.services.llm_service import LLMService
from app.core.config import settings


class VectorService:
    def __init__(self):
        self.client_wrapper = QdrantDBClient()
        self.client = self.client_wrapper.client
        self.llm_service = LLMService()

    def upsert_chunk(self, chunk):
        vector = self.llm_service.embed_text(chunk.content)

        point = PointStruct(
            id=str(chunk.id),
            vector=vector,
            payload={
                "chat_id": str(chunk.chat_id),
                "document_id": str(chunk.document_id),
                "chunk_id": str(chunk.id),
                "text": chunk.content,
            },
        )

        self.client.upsert(collection_name=settings.QDRANT_COLLECTION, points=[point])

    def search_chunks(self, query: str, chat_id: str, limit: int = 5):
        query_vector = self.llm_service.embed_text(query)

        results = self.client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            limit=limit,
            query_filter={
                "must": [{"key": "chat_id", "match": {"value": str(chat_id)}}]
            },
        )
        return results.points

    def close(self):
        self.client_wrapper.close()
