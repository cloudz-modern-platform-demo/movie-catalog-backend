import logging
from fastapi import FastAPI
from .db.session import init_db
from .db.seed import seed_database_if_empty
from .route import theaters, movies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    FastAPI application factory.
    Creates and configures the FastAPI application with routes and startup logic.
    """
    app = FastAPI(
        title="Movie Catalog Backend",
        description="Backend API for managing theater and movie information",
        version="0.1.0"
    )

    # Include routers
    app.include_router(theaters.router)
    app.include_router(movies.router)

    @app.on_event("startup")
    def startup_event():
        """Initialize database and seed data on application startup"""
        logger.info("Starting application...")
        init_db()
        logger.info("Database initialized")
        seed_database_if_empty()
        logger.info("Application startup complete")

    @app.get("/", tags=["health"])
    def health_check():
        """Health check endpoint"""
        return {"status": "ok", "service": "movie-catalog-backend"}

    return app
