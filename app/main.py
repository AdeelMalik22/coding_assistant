"""Main FastAPI application entry point."""

import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from utils.logger import get_logger
from app.routes import api, ui

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if settings.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    logger.info(f"Mounted static files from {settings.STATIC_DIR}")

# Include routers
app.include_router(ui.router)
app.include_router(api.router)

# Root endpoint
@app.get("/")
async def root():
    """Redirect to home page."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/")


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "api-builder",
        "version": settings.API_VERSION,
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting up AI-Powered API Builder")
    logger.info(f"Generated projects directory: {settings.GENERATED_PROJECTS_DIR}")
    logger.info(f"Templates directory: {settings.TEMPLATES_DIR}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Check Ollama connection
    from app.ai.llm import OllamaClient
    client = OllamaClient()
    if await client.health_check():
        logger.info(f"✓ Ollama is available at {settings.OLLAMA_BASE_URL}")
    else:
        logger.warning(f"⚠ Ollama is not available at {settings.OLLAMA_BASE_URL}")
        logger.warning("Make sure Ollama is running: ollama serve")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down AI-Powered API Builder")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

