import os
from pathlib import Path


def find_project_root() -> Path:
    """
    Find project root by looking for pyproject.toml in current or parent directories.
    """
    current = Path.cwd()

    # Search upwards for pyproject.toml
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent

    # Fallback to current directory
    return current


def get_database_url() -> str:
    """
    Get database URL from environment or default to data/movie_catalog.db in project root.
    """
    if db_url := os.getenv("DATABASE_URL"):
        return db_url

    project_root = find_project_root()
    db_path = project_root / "data" / "movie_catalog.db"

    # Ensure data directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return f"sqlite:///{db_path}"
