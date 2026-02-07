import asyncio
from uuid import uuid4
from app.models.chat import Chat
from app.db.session import init_db, SessionLocal
from app.services.ingestion_service import IngestionService
from app.services.retrieval_service import RetrievalService
from sqlalchemy import select

# ---- Setup ----
chat_id = "9ca4d20e-149a-4d51-934d-6705a0e5f4a3"
document_id = uuid4()

DOCUMENT_TEXT = """
Graph RAG is an advanced retrieval technique.
Graph RAG uses a graph database such as Neo4j.
Neo4j is used to store entities and relationships.
Graph RAG also uses vector databases like Qdrant for semantic search.
"""

QUESTION = "How does Graph RAG use Neo4j?"


async def main():
    print("=== Starting Graph RAG smoke test ===")

    # 0. Initialize DB
    print("\n[0] Initializing database...")
    await init_db()

    # Ensure chat exists
    async with SessionLocal() as db:
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if not chat:
            print(f"Creating test chat: {chat_id}")
            chat = Chat(id=chat_id, title="Test Chat", status="active")
            db.add(chat)
            await db.commit()

    # 1. Ingest document
    print("\n[1] Ingesting document...")
    ingestion = IngestionService()
    await ingestion.ingest_text(
        chat_id=chat_id, document_id=document_id, text=DOCUMENT_TEXT
    )
    ingestion.close()
    print("✓ Ingestion completed")

    # 2. Retrieve context
    print("\n[2] Retrieving context...")
    retrieval = RetrievalService()
    context = retrieval.retrieve_context(chat_id=chat_id, question=QUESTION)
    retrieval.close()

    print("\n=== Retrieved Context ===")
    print(context)

    print("\n=== Smoke test completed successfully ===")


if __name__ == "__main__":
    asyncio.run(main())
