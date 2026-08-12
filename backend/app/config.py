from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "QuoteLab API"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # Configurable Parameters (ready for calibration)
    DATASET_PATH: str = "data/citas.xlsx"
    DEBATE_RELEVANCE_THRESHOLD: float = 0.65
    DEBATE_EVIDENCE_TOP_K: int = 3
    LLM_PROVIDER: str = "mock-dev"
    MAX_UNITS_PER_BATCH: int = 500
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    DEFAULT_TOP_K: int = 3

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    OLLAMA_TIMEOUT: float = 60.0


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
