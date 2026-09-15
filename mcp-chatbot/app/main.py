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
from app.utils.logger import setup_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger("app.main")
    settings = get_settings()
    logger.info(
        "Starting GlobeTrotter MCP Chatbot | host=%s port=%s model=%s",
        settings.chatbot_host,
        settings.chatbot_port,
        settings.groq_model,
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health():
    settings = get_settings()
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "globetrotter-mcp-chatbot",
            "model": settings.groq_model,
            "globetrotter_api": settings.globetrotter_api_url,
        },
    }


app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(conversations_router, prefix="/api")
app.include_router(observability_router, prefix="/api")
