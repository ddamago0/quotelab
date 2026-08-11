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
    DEBATE_RELEVANCE_THRESHOLD: float = 0.65
    MAX_UNITS_PER_BATCH: int = 500
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
