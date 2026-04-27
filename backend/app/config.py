"""
CineAI Backend - Configuration
Centraliza todas las variables de entorno con validación via pydantic-settings.
"""
import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    # --- Database ---
    database_url: str = "postgresql+asyncpg://cineai:cineai_secret_2024@db:5432/cineai_db"

    # --- Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_log_level: str = "info"

    # --- LLM Service ---
    llm_service_url: str = "http://llm_service:8001"

    # --- TMDB ---
    tmdb_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
logger.info(
    "Settings loaded: db=%s, llm_url=%s",
    settings.database_url[:30] + "...",
    settings.llm_service_url,
)
