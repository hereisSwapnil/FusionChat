from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "FusionChat"
    DEBUG: bool = False

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"

    # Neo4j Settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Qdrant Settings
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "fusion_chat"

    # Ollama Settings
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_GEN_MODEL: str = "llama3.2:1b"

    # Database Settings
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/fusionchat"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
