import threading
from openai import OpenAI
from app.core.config import settings

# Initialize OpenAI client at module level to avoid import deadlock
_client_lock = threading.Lock()
_shared_client = None


def get_openai_client():
    """Get or create the shared OpenAI client (thread-safe)."""
    global _shared_client
    if _shared_client is None:
        with _client_lock:
            if _shared_client is None:
                _shared_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                # Warm up the client to load all sub-modules before threading
                # This prevents lazy import deadlocks
                _warm_up_client(_shared_client)
    return _shared_client


def _warm_up_client(client: OpenAI):
    """Pre-load OpenAI sub-modules to prevent threading deadlocks."""
    try:
        # Access the sub-modules to trigger their imports
        _ = client.embeddings
        _ = client.chat.completions
    except Exception:
        # If warming fails, continue anyway
        pass


class LLMService:
    def __init__(self):
        self.client = get_openai_client()
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
