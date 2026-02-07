from app.services.llm_service import LLMService
from app.db.queries.llm import ANSWER_QUESTION_PROMPT


class AnswerService:
    def __init__(self):
        self.llm = LLMService()

    def generate_answer(self, question: str, context: str) -> str:
        prompt = f"""
{ANSWER_QUESTION_PROMPT}

Context:
{context}

Question:
{question}

Answer:
"""
        return self.llm.generate(prompt)
