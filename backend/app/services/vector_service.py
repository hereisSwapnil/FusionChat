from qdrant_client.models import PointStruct, VectorParams, Distance
from app.db.qdrant import QdrantDBClient
from app.services.llm_service import LLMService


class VectorService:
    def __init__(self):
        self.client_wrapper = QdrantDBClient()
        self.client = self.client_wrapper.client
        self.llm_service = LLMService()

    def _get_collection_name(self, chat_id: str) -> str:
        """Get collection name for a specific chat."""
        return f"chat_{chat_id}"

    def _ensure_collection_exists(self, chat_id: str):
        """Ensure collection exists for the chat."""
        collection_name = self._get_collection_name(chat_id)

        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    def upsert_chunk(self, chunk):
        # Ensure collection exists for this chat
        self._ensure_collection_exists(str(chunk.chat_id))

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

        collection_name = self._get_collection_name(str(chunk.chat_id))
        self.client.upsert(collection_name=collection_name, points=[point])

    def search_chunks(self, query: str, chat_id: str, limit: int = 5):
        collection_name = self._get_collection_name(str(chat_id))

        # Check if collection exists
        if not self.client.collection_exists(collection_name):
            return []

        query_vector = self.llm_service.embed_text(query)

        results = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            query_filter={
                "must": [{"key": "chat_id", "match": {"value": str(chat_id)}}]
            },
        )
        return results.points

    def close(self):
        self.client_wrapper.close()
