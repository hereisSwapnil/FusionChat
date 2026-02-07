ENTITY_CONSTRAINTS = [
    """
    CREATE CONSTRAINT entity_unique_per_chat
    IF NOT EXISTS
    FOR (e:Entity)
    REQUIRE (e.chat_id, e.name_normalized) IS UNIQUE
    """,
    """
    CREATE CONSTRAINT entity_chat_required
    IF NOT EXISTS
    FOR (e:Entity)
    REQUIRE e.chat_id IS NOT NULL
    """,
    """
    CREATE CONSTRAINT entity_name_required
    IF NOT EXISTS
    FOR (e:Entity)
    REQUIRE e.name IS NOT NULL
    """,
]

# In your graph queries file
UPSERT_ENTITY_QUERY = """
        MERGE (e:Entity {{
            chat_id: $chat_id,
            name_normalized: $name_norm
        }})
        ON CREATE SET
            e.entity_id = $entity_id,
            e.name = $name,
            e.type = $type,
            e.confidence = $confidence,
            e.created_from_chunk_id = $chunk_id,
            e.created_at = $created_at
        ON MATCH SET
            e.confidence = coalesce(e.confidence, 0) + $confidence
        """


UPSERT_RELATIONSHIP_QUERY = """
        MATCH (a:Entity {{entity_id: $src, chat_id: $chat_id}})
        MATCH (b:Entity {{entity_id: $tgt, chat_id: $chat_id}})
        MERGE (a)-[r:{} {{chat_id: $chat_id}}]->(b)
        ON CREATE SET
            r.confidence = $confidence,
            r.created_from_chunk_id = $chunk_id
        ON MATCH SET
            r.confidence = CASE WHEN $confidence > r.confidence THEN $confidence ELSE r.confidence END
        """

MATCH_QUERY = """
MATCH (e:Entity)
WHERE e.chat_id = $chat_id
  AND e.name_normalized IN $names
MATCH (e)-[r*1..{}]->(related)
RETURN e, r, related
"""

EXTRACT_ENTITIES_PROMPT = """
Extract the key entities from the question.

Return ONLY valid JSON:
{
  "entities": [
    {"name": "...", "type": "..."}
  ]
}
"""
