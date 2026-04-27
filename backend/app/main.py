"""
CineAI Backend - FastAPI Application Entry Point
Configura la app FastAPI, CORS, logging, y lifespan events.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import movies, chat
from app.schemas import HealthResponse

# ─── Logging ─────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.backend_log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup y shutdown events."""
    logger.info("=== CineAI Backend starting up ===")
    await init_db()
    logger.info("=== CineAI Backend ready ===")
    yield
    logger.info("=== CineAI Backend shutting down ===")


# ─── App ─────────────────────────────────────────────────
app = FastAPI(
    title="CineAI - Catálogo de Películas",
    description="API REST para gestión de catálogo de películas con recomendaciones por IA.",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ──────────────────────────────────────────────
app.include_router(movies.router)
app.include_router(chat.router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", service="backend")


logger.info("CineAI Backend app configured. Routes: /api/movies, /api/chat, /api/health")
