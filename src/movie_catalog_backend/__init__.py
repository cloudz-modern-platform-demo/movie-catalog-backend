import os
import uvicorn


def main() -> None:
    """
    Main entry point for running the application with uvicorn.
    Port is fixed at 8000 as per TRD requirements.
    """
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "true").lower() == "true"

    uvicorn.run(
        "movie_catalog_backend.app:create_app",
        factory=True,
        host=host,
        port=8000,
        reload=reload
    )
