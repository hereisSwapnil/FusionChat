"""
Test script to inspect Qdrant and Neo4j storage and retrieval.
Run this to see what data was stored during document ingestion.
"""

import asyncio
from app.services.vector_service import VectorService
from app.services.graph_service import GraphService
from app.services.retrieval_service import RetrievalService
from uuid import UUID

# Your chat ID from the logs
CHAT_ID = UUID("f2deff5e-6f1e-4bc6-a069-327184825b09")


def inspect_qdrant():
    """Inspect what's stored in Qdrant vector database."""
    print("=" * 80)
    print("QDRANT VECTOR STORE INSPECTION")
    print("=" * 80)

    vector_service = VectorService()

    try:
        # Get collection info
        collection_name = f"chat_{CHAT_ID}"
        print(f"\n📦 Collection: {collection_name}")

        # Try to get collection info
        try:
            collection_info = vector_service.client.get_collection(collection_name)
            print(f"✅ Collection exists")
            print(f"   Points count: {collection_info.points_count}")
            print(f"   Vector size: {collection_info.config.params.vectors.size}")
        except Exception as e:
            print(f"❌ Collection not found or error: {e}")
            return

        # Search for some sample chunks
        print(f"\n🔍 Sample search: 'experience'")
        results = vector_service.search_chunks("experience", CHAT_ID, limit=3)

        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} (Score: {result.score:.4f}) ---")
            print(f"Text preview: {result.payload['text'][:200]}...")
            print(f"Chunk ID: {result.payload.get('chunk_id', 'N/A')}")
            print(f"Document ID: {result.payload.get('document_id', 'N/A')}")

    except Exception as e:
        print(f"❌ Error inspecting Qdrant: {e}")
    finally:
        vector_service.close()


def inspect_neo4j():
    """Inspect what's stored in Neo4j graph database."""
    print("\n" + "=" * 80)
    print("NEO4J GRAPH STORE INSPECTION")
    print("=" * 80)

    graph_service = GraphService()

    try:
        with graph_service.client.driver.session() as session:
            # Count entities
            result = session.run(
                "MATCH (n) WHERE n.chat_id = $chat_id RETURN count(n) as count",
                chat_id=str(CHAT_ID),
            )
            entity_count = result.single()["count"]
            print(f"\n📊 Total entities: {entity_count}")

            # Get entity types
            result = session.run(
                "MATCH (n) WHERE n.chat_id = $chat_id RETURN labels(n)[0] as type, count(*) as count ORDER BY count DESC LIMIT 10",
                chat_id=str(CHAT_ID),
            )
            print("\n🏷️  Entity types:")
            for record in result:
                print(f"   {record['type']}: {record['count']}")

            # Sample entities
            result = session.run(
                "MATCH (n) WHERE n.chat_id = $chat_id RETURN n.name as name, labels(n)[0] as type, n.confidence as confidence LIMIT 10",
                chat_id=str(CHAT_ID),
            )
            print("\n📝 Sample entities:")
            for record in result:
                print(
                    f"   {record['type']}: {record['name']} (confidence: {record.get('confidence', 'N/A')})"
                )

            # Count relationships
            result = session.run(
                """
                MATCH (a)-[r]->(b) 
                WHERE a.chat_id = $chat_id 
                RETURN count(r) as count
                """,
                chat_id=str(CHAT_ID),
            )
            rel_count = result.single()["count"]
            print(f"\n🔗 Total relationships: {rel_count}")

            # Sample relationships
            result = session.run(
                """
                MATCH (a)-[r]->(b) 
                WHERE a.chat_id = $chat_id 
                RETURN a.name as source, type(r) as relationship, b.name as target, r.confidence as confidence 
                LIMIT 10
                """,
                chat_id=str(CHAT_ID),
            )
            print("\n🔗 Sample relationships:")
            for record in result:
                print(
                    f"   {record['source']} --[{record['relationship']}]--> {record['target']} (confidence: {record.get('confidence', 'N/A')})"
                )

    except Exception as e:
        print(f"❌ Error inspecting Neo4j: {e}")
        import traceback

        traceback.print_exc()
    finally:
        graph_service.close()


def test_retrieval():
    """Test the full retrieval pipeline."""
    print("\n" + "=" * 80)
    print("RETRIEVAL PIPELINE TEST")
    print("=" * 80)

    retrieval_service = RetrievalService()

    test_questions = [
        "What is Swapnil's experience?",
        "What technologies does Swapnil know?",
        "Where did Swapnil work?",
    ]

    for question in test_questions:
        print(f"\n❓ Question: {question}")
        print("-" * 80)

        try:
            context = retrieval_service.retrieve_context(CHAT_ID, question)
            print(f"📄 Retrieved context ({len(context)} chars):")
            print(context[:500] + "..." if len(context) > 500 else context)
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()

    retrieval_service.close()


def main():
    """Run all inspections."""
    print("\n🔬 DOCUMENT INGESTION INSPECTION")
    print("Testing what was stored in Qdrant and Neo4j\n")

    # Inspect vector store
    inspect_qdrant()

    # Inspect graph store
    inspect_neo4j()

    # Test retrieval
    test_retrieval()

    print("\n" + "=" * 80)
    print("✅ INSPECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
