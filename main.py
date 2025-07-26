from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.config.settings import settings, allowed_origins
from src.auth.routes import router as auth_router
from src.routes.teams import router as teams_router
from dotenv import load_dotenv

load_dotenv(override=True)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A comprehensive backend service for profile matching with authentication",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router)
app.include_router(teams_router)

@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Welcome to Profile Matcher Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "auth_endpoints": "/auth"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0"
    }


async def on_startup():
    """Application startup event handler."""
    logger.info("Application startup")

async def on_shutdown():
    """Application shutdown event handler."""
    logger.info("Application shutdown")

app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)
