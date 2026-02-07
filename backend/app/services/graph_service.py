import json
from app.db.neo4j import Neo4jClient
from app.db.utils.graph import upsert_entity, upsert_relationship
from app.services.llm_service import LLMService
from app.schemas.extraction import ExtractionResult
from app.db.queries.llm import EXTRACT_ENTITIES_AND_RELATIONSHIPS_PROMPT
from app.db.queries.graph import EXTRACT_ENTITIES_PROMPT, MATCH_QUERY
from app.core.utils import normalize_name


class GraphService:
    def __init__(self):
        self.client = Neo4jClient()
        self.llm_service = LLMService()  # Initialize once to avoid import deadlock

    def add_entity(self, entity):
        with self.client.driver.session() as session:
            session.execute_write(upsert_entity, entity)

    def add_relationship(self, relationship):
        with self.client.driver.session() as session:
            session.execute_write(upsert_relationship, relationship)

    def _extract_json(self, text: str) -> str:
        # Simple extraction of JSON from text
        start_brace = text.find("{")
        start_bracket = text.find("[")

        start = -1
        if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
            start = start_brace
            end = text.rfind("}")
        elif start_bracket != -1:
            start = start_bracket
            end = text.rfind("]")

        if start != -1 and end != -1:
            return text[start : end + 1]
        return text

    def extract_entities_and_relationships(self, text: str) -> ExtractionResult:
        response = self.llm_service.generate(
            EXTRACT_ENTITIES_AND_RELATIONSHIPS_PROMPT + "\n\nText:\n" + text
        )

        data = json.loads(self._extract_json(response))

        return ExtractionResult(**data)

    def retrieve(self, chat_id, entity_names, depth: int = 2):
        query = MATCH_QUERY.format(depth)

        with self.client.driver.session() as session:
            result = session.run(
                query,
                chat_id=str(chat_id),
                names=[normalize_name(n) for n in entity_names],
            )
            return list(result)

    def parse(self, question: str):
        raw = self.llm_service.generate(
            EXTRACT_ENTITIES_PROMPT + "\n\nQuestion:\n" + question
        )
        data = json.loads(self._extract_json(raw))
        return data

    def close(self):
        self.client.close()
