from app.core.utils import chunk_text
from app.services.vector_service import VectorService
from app.schemas.chunk import Chunk
from app.schemas.entity import Entity
from app.schemas.relationship import Relationship
from app.services.graph_service import GraphService
from app.db.session import SessionLocal
from app.models.chat import Document as DocumentModel
from sqlalchemy import select


class IngestionService:
    def __init__(self):
        self.graph = GraphService()
        self.vector = VectorService()

    async def ingest_text(
        self,
        chat_id,
        document_id,
        text: str,
        file_name: str = "unknown",
        file_size: int = 0,
    ):
        # 0. Save or update document metadata in DB
        async with SessionLocal() as db:
            result = await db.execute(
                select(DocumentModel).where(DocumentModel.id == document_id)
            )
            doc = result.scalar_one_or_none()
            if not doc:
                doc = DocumentModel(
                    id=document_id,
                    chat_id=chat_id,
                    file_name=file_name,
                    file_size=file_size,
                    file_type="text",
                    checksum="",
                    status="processing",
                )
                db.add(doc)
                await db.commit()

        chunks = chunk_text(text)
        # ... (rest of the logic remains synchronous for now as vector/graph services are likely sync)
        # However, we should probably make them async if they aren't.
        # For now, let's keep the existing logic but wrapped in this async method.

        # Track all entities across chunks for this document
        global_entity_map = {}

        for index, content in enumerate(chunks):
            chunk = Chunk(
                chat_id=chat_id,
                document_id=document_id,
                content=content,
                index=index,
            )

            # 1. Vector store
            self.vector.upsert_chunk(chunk)

            # 2. Graph extraction
            extraction = self.graph.extract_entities_and_relationships(content)

            # 3. Store entities (with deduplication)
            for e in extraction.entities:
                if not e.name:
                    continue

                # Normalize name for deduplication
                name_key = e.name.lower().strip()

                # Check if entity already exists in this document
                if name_key in global_entity_map:
                    entity = global_entity_map[name_key]
                else:
                    entity = Entity(
                        chat_id=chat_id,
                        document_id=document_id,
                        name=e.name,
                        type=e.type,
                        confidence=e.confidence,
                        chunk_id=chunk.id,
                    )
                    self.graph.add_entity(entity)
                    global_entity_map[name_key] = entity

            # 4. Store relationships
            for r in extraction.relationships:
                if not r.source or not r.target:
                    continue

                # Normalize relationship names to match entity keys
                source_key = r.source.lower().strip()
                target_key = r.target.lower().strip()

                if source_key in global_entity_map and target_key in global_entity_map:
                    rel = Relationship(
                        chat_id=chat_id,
                        source_id=global_entity_map[source_key].id,
                        target_id=global_entity_map[target_key].id,
                        type=r.type,
                        confidence=r.confidence,
                        chunk_id=chunk.id,
                    )
                    self.graph.add_relationship(rel)

        # Update document status to completed
        async with SessionLocal() as db:
            result = await db.execute(
                select(DocumentModel).where(DocumentModel.id == document_id)
            )
            doc = result.scalar_one_or_none()
            if doc:
                doc.status = "completed"
                await db.commit()

    def close(self):
        self.graph.close()
        self.vector.close()
