"""
CineAI LLM Service - Configuration
"""
import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuración del servicio LLM."""

    gemini_api_key: str = ""
    llm_host: str = "0.0.0.0"
    llm_port: int = 8001
    gemini_model: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
logger.info("LLM Service settings loaded. Model: %s", settings.gemini_model)
