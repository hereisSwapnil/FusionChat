from app.services.graph_service import GraphService
from app.services.vector_service import VectorService
from app.db.utils.graph import build_context


class RetrievalService:
    def __init__(self):
        self.graph = GraphService()
        self.vector = VectorService()

    def retrieve_context(self, chat_id, question: str) -> str:
        # 1. Vector recall
        chunks = self.vector.search_chunks(question, chat_id)

        # 2. Parse question entities
        parsed = self.graph.parse(question)
        if isinstance(parsed, dict):
            entity_names = [
                e.get("name") for e in parsed.get("entities", []) if isinstance(e, dict)
            ]
        elif isinstance(parsed, list):
            entity_names = [e.get("name") for e in parsed if isinstance(e, dict)]
        else:
            entity_names = []
        entity_names = [n for n in entity_names if n]

        # 3. Graph reasoning
        graph_results = []
        if entity_names:
            graph_results = self.graph.retrieve(chat_id, entity_names)

        # 4. Build context
        return build_context(chunks, graph_results)

    def close(self):
        self.graph.close()
        self.vector.close()
