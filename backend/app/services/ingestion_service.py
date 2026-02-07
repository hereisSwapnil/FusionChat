import asyncio
import time
from app.services.vector_service import VectorService
from app.services.graph_service import GraphService
from app.schemas.chunk import Chunk
from app.schemas.entity import Entity
from app.schemas.relationship import Relationship
from app.db.session import SessionLocal
from app.models.chat import Document as DocumentModel
from sqlalchemy import select
from app.core.utils import chunk_text_semantic
import logging

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, max_workers=10):  # Increased from 3 to 10 for faster processing
        self.max_workers = max_workers
        self.vector = VectorService()
        self.graph = GraphService()
        print(
            f"✓ IngestionService initialized with {self.max_workers} parallel workers"
        )
        logger.info(
            f"✓ IngestionService initialized with {self.max_workers} parallel workers"
        )

    async def ingest_text(
        self,
        chat_id,
        document_id,
        text: str,
        file_name: str = "unknown",
        file_size: int = 0,
        timeout_seconds: float = 300.0,
    ):
        start_time = time.time()
        logger.info(f"Starting parallel ingestion for document {document_id}")

        try:
            # Run async ingestion with timeout
            result = await asyncio.wait_for(
                self._ingest_async(chat_id, document_id, text, file_name, file_size),
                timeout=timeout_seconds,
            )

            end_time = time.time()
            logger.info(
                f"Parallel ingestion completed in {end_time - start_time:.2f} seconds"
            )
            return result

        except asyncio.TimeoutError:
            logger.error(f"Ingestion timed out after {timeout_seconds} seconds")
            await self._update_status(document_id, "failed")
            raise Exception(f"Ingestion timed out after {timeout_seconds} seconds")
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            await self._update_status(document_id, "failed")
            raise

    async def _ingest_async(self, chat_id, document_id, text, file_name, file_size):
        """Main async ingestion logic with parallel chunk processing."""
        await self._save_document_metadata(document_id, chat_id, file_name, file_size)

        chunks_with_metadata = chunk_text_semantic(text)
        total_chunks = len(chunks_with_metadata)
        logger.info("\n" + "=" * 60)
        logger.info(f"📄 Document: {file_name}")
        logger.info(f"📊 Total chunks: {total_chunks}")
        logger.info(f"⚙️  Max workers: {self.max_workers}")
        logger.info("🚀 Starting parallel processing...")
        logger.info("=" * 60 + "\n")

        # Process chunks in parallel with concurrency limit
        semaphore = asyncio.Semaphore(self.max_workers)
        self._total_chunks = chunks_with_metadata  # Store for progress tracking
        tasks = [
            self._process_chunk_async(semaphore, chat_id, document_id, chunk_data, i)
            for i, chunk_data in enumerate(chunks_with_metadata)
        ]

        logger.info(
            f"⏳ Processing {total_chunks} chunks with up to {self.max_workers} parallel workers..."
        )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("✓ All chunks processed!\n")

        # Collect all entities and build global entity map
        global_entity_map = {}
        all_chunk_results = []

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Chunk processing error: {result}")
                continue
            if isinstance(result, dict) and result.get("status") == "success":
                all_chunk_results.append(result)
                # Add entities to global map
                for entity_data in result.get("entities", []):
                    if entity_data and entity_data.get("name"):
                        name_key = entity_data["name"].lower().strip()
                        if name_key not in global_entity_map:
                            global_entity_map[name_key] = entity_data

        # Add all unique entities to graph
        logger.info("\n📈 RESULTS:")
        logger.info(f"  • Total unique entities: {len(global_entity_map)}")
        logger.info(
            f"  • Successfully processed chunks: {len(all_chunk_results)}/{total_chunks}"
        )
        logger.info("\n🔗 Adding entities to graph...")
        for entity_data in global_entity_map.values():
            try:
                entity = Entity(
                    chat_id=chat_id,
                    document_id=document_id,
                    name=entity_data["name"],
                    type=entity_data.get("type", "Entity"),
                    confidence=entity_data.get("confidence", 0.5),
                    chunk_id=entity_data["chunk_id"],
                )
                await asyncio.to_thread(self.graph.add_entity, entity)
                entity_data["entity_obj"] = entity
            except Exception as e:
                logger.warning(f"Failed to add entity {entity_data['name']}: {e}")

        # Add relationships
        total_relationships = sum(
            len(chunk.get("relationships", [])) for chunk in all_chunk_results
        )
        logger.info(f"\n🔗 Adding {total_relationships} relationships to graph...")
        for chunk_result in all_chunk_results:
            for rel_data in chunk_result.get("relationships", []):
                if (
                    not rel_data
                    or not rel_data.get("source")
                    or not rel_data.get("target")
                ):
                    continue

                source_key = rel_data["source"].lower().strip()
                target_key = rel_data["target"].lower().strip()

                if source_key in global_entity_map and target_key in global_entity_map:
                    source_entity = global_entity_map[source_key].get("entity_obj")
                    target_entity = global_entity_map[target_key].get("entity_obj")

                    if source_entity and target_entity:
                        try:
                            rel = Relationship(
                                chat_id=chat_id,
                                source_id=source_entity.id,
                                target_id=target_entity.id,
                                type=rel_data.get("type", "RELATED_TO"),
                                confidence=rel_data.get("confidence", 0.5),
                                chunk_id=rel_data["chunk_id"],
                            )
                            await asyncio.to_thread(self.graph.add_relationship, rel)
                        except Exception as e:
                            logger.warning(f"Failed to add relationship: {e}")

        await self._update_status(document_id, "completed")
        logger.info("\n" + "=" * 60)
        logger.info("✅ INGESTION COMPLETE!")
        logger.info("=" * 60 + "\n")
        return True

    async def _process_chunk_async(
        self, semaphore, chat_id, document_id, chunk_data, index
    ):
        """Process a single chunk: vector upsert + entity extraction in parallel."""
        async with semaphore:
            chunk_start = time.time()
            try:
                logger.info(
                    f"🔄 Worker processing chunk {index + 1}/{len(self._total_chunks)} ({(index + 1) / len(self._total_chunks) * 100:.1f}%)"
                )

                chunk = Chunk(
                    chat_id=chat_id,
                    document_id=document_id,
                    content=chunk_data["content"],
                    index=chunk_data["metadata"]["chunk_index"],
                    char_start=chunk_data["metadata"]["char_start"],
                    char_end=chunk_data["metadata"]["char_end"],
                    position_ratio=chunk_data["metadata"]["position_ratio"],
                    content_type=chunk_data["metadata"]["content_type"],
                    headings=chunk_data["metadata"]["headings"],
                )

                # Run vector upsert and entity extraction in parallel
                vector_task = asyncio.to_thread(self.vector.upsert_chunk, chunk)
                entity_task = asyncio.to_thread(
                    self.graph.extract_entities_and_relationships, chunk.content
                )

                # Wait for both to complete
                vector_result, extraction = await asyncio.gather(
                    vector_task, entity_task, return_exceptions=True
                )

                if isinstance(vector_result, Exception):
                    logger.warning(
                        f"Vector upsert failed for chunk {index}: {vector_result}"
                    )

                # Process extraction results
                entities = []
                relationships = []

                if not isinstance(extraction, Exception):
                    if hasattr(extraction, "entities") and extraction.entities:
                        for e in extraction.entities:
                            if e.name:
                                entities.append(
                                    {
                                        "name": e.name,
                                        "type": e.type or "Entity",
                                        "confidence": e.confidence or 0.5,
                                        "chunk_id": chunk.id,
                                    }
                                )

                    if (
                        hasattr(extraction, "relationships")
                        and extraction.relationships
                    ):
                        for r in extraction.relationships:
                            if r.source and r.target:
                                relationships.append(
                                    {
                                        "source": r.source,
                                        "target": r.target,
                                        "type": r.type or "RELATED_TO",
                                        "confidence": r.confidence or 0.5,
                                        "chunk_id": chunk.id,
                                    }
                                )
                else:
                    logger.warning(
                        f"Entity extraction failed for chunk {index}: {extraction}"
                    )

                chunk_time = time.time() - chunk_start
                logger.info(
                    f"✓ Chunk {index + 1} completed in {chunk_time:.2f}s (Entities: {len(entities)}, Relationships: {len(relationships)})"
                )

                return {
                    "chunk_id": chunk.id,  # Keep chunk_id for consistency in _ingest_async processing
                    "status": "success",
                    "entities": entities,
                    "relationships": relationships,
                }

            except Exception as e:
                logger.error(f"❌ Chunk {index} processing failed: {e}")
                return {"chunk_id": None, "status": "error", "error": str(e)}

    async def _save_document_metadata(self, document_id, chat_id, file_name, file_size):
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

    async def _update_status(self, document_id, status):
        try:
            async with SessionLocal() as db:
                result = await db.execute(
                    select(DocumentModel).where(DocumentModel.id == document_id)
                )
                doc = result.scalar_one_or_none()
                if doc:
                    doc.status = status
                    await db.commit()
        except Exception as e:
            logger.error(f"Failed to update document status: {e}")

    def close(self):
        self.vector.close()
        self.graph.close()
