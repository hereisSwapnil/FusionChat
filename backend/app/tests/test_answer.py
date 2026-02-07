from uuid import uuid4
from app.services.retrieval_service import RetrievalService
from app.services.answer_service import AnswerService

chat_id = "d82665c5-9830-474f-b0b0-c309a246cdbc"  # reuse same chat_id as ingestion test if needed

QUESTION = "Where is swapnil from?"


def main():
    retrieval = RetrievalService()
    answer_service = AnswerService()

    context = retrieval.retrieve_context(chat_id, QUESTION)
    answer = answer_service.generate_answer(QUESTION, context)

    print("\n=== CONTEXT ===")
    print(context)

    print("\n=== ANSWER ===")
    print(answer)


if __name__ == "__main__":
    main()
