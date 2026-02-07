from app.db.queries.graph import UPSERT_ENTITY_QUERY, UPSERT_RELATIONSHIP_QUERY
from app.core.utils import normalize_name
from datetime import datetime


def upsert_entity(tx, entity):
    name_norm = normalize_name(entity.name)

    tx.run(
        UPSERT_ENTITY_QUERY.format(f"`{entity.type}`"),
        chat_id=str(entity.chat_id),
        entity_id=str(entity.id),
        name=entity.name,
        name_norm=name_norm,
        type=entity.type,
        confidence=entity.confidence or 0.0,
        chunk_id=str(entity.chunk_id),
        created_at=datetime.utcnow().isoformat(),
    )


def upsert_relationship(tx, rel):
    tx.run(
        UPSERT_RELATIONSHIP_QUERY.format(f"`{rel.type}`"),
        src=str(rel.source_id),
        tgt=str(rel.target_id),
        chat_id=str(rel.chat_id),
        confidence=rel.confidence or 0.0,
        chunk_id=str(rel.chunk_id),
    )


def build_context(chunks, graph_results) -> str:
    context_parts = []

    context_parts.append("### Relevant Information")
    for c in chunks:
        context_parts.append(f"- {c.payload['text']}")

    context_parts.append("\n### Knowledge Graph Facts")
    for record in graph_results:
        context_parts.append(str(record))

    return "\n".join(context_parts)
