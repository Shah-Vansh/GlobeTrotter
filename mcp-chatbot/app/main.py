"""
FastAPI entrypoint for the GlobeTrotter MCP AI Chatbot.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.observability import router as observability_router
from app.config import get_settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.logger import setup_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger("app.main")
    settings = get_settings()
    if settings.require_groq_key and not settings.groq_api_key:
        logger.error("GROQ_API_KEY is required but missing (require_groq_key=true)")
        raise RuntimeError("GROQ_API_KEY is required")
    logger.info(
        "Starting GlobeTrotter MCP Chatbot | host=%s port=%s model=%s rate_limit=%d/%ds",
        settings.chatbot_host,
        settings.chatbot_port,
        settings.groq_model,
        settings.rate_limit_requests,
        settings.rate_limit_window_seconds,
    )
    yield
    logger.info("Shutting down GlobeTrotter MCP Chatbot")


app = FastAPI(
    title="GlobeTrotter MCP AI Chatbot",
    description=(
        "Natural-language interface over the existing GlobeTrotter application. "
        "MCP tools wrap only existing backend capabilities."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


@app.get("/health", tags=["health"])
async def health():
    s = get_settings()
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "globetrotter-mcp-chatbot",
            "model": s.groq_model,
            "globetrotter_api": s.globetrotter_api_url,
            "rate_limit": {
                "requests": s.rate_limit_requests,
                "window_seconds": s.rate_limit_window_seconds,
            },
        },
    }


app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(conversations_router, prefix="/api")
app.include_router(observability_router, prefix="/api")
