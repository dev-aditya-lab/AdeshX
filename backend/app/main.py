"""AdeshX — FastAPI Application Entry Point."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import documents, extraction, actions, dashboard

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="From Judgments to Just-in-Time Government Action — AI-powered court judgment analysis system",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(extraction.router)
app.include_router(actions.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"AI Available: {settings.is_ai_available}")
    logger.info(f"Demo Mode: {settings.DEMO_MODE}")
    init_db()


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "ai_available": settings.is_ai_available,
    }


@app.get("/health")
def health():
    """Health check."""
    return {"status": "healthy"}


