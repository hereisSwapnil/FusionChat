from openai import OpenAI
from app.core.config import settings


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.llm_model = settings.OPENAI_LLM_MODEL
        self.embed_model = settings.OPENAI_EMBED_MODEL

    def embed_text(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.embed_model, input=text, encoding_format="float"
        )
        return response.data[0].embedding

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return response.choices[0].message.content
