from qdrant_client import QdrantClient as LibQdrantClient
from qdrant_client.models import VectorParams, Distance
from app.core.config import settings


class QdrantDBClient:
    def __init__(self):
        self.client = LibQdrantClient(url=settings.QDRANT_URL)

        # Ensure collection exists and has correct dimensions
        if self.client.collection_exists(settings.QDRANT_COLLECTION):
            collection_info = self.client.get_collection(settings.QDRANT_COLLECTION)
            # OpenAI text-embedding-3-small uses 1536 dimensions
            if collection_info.config.params.vectors.size != 1536:
                print(
                    f"Dimension mismatch in {settings.QDRANT_COLLECTION}. Recreating..."
                )
                self.client.delete_collection(settings.QDRANT_COLLECTION)

        if not self.client.collection_exists(settings.QDRANT_COLLECTION):
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    def close(self):
        # Qdrant library handles connection pooling; explicit close is often optional but good practice if available
        pass
