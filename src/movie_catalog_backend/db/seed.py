import json
import logging
from pathlib import Path
from uuid import uuid4
from sqlmodel import select
from .session import session_scope
from .config import find_project_root
from ..entity.models import Theater, Movie

logger = logging.getLogger(__name__)


# Embedded sample data as fallback
SAMPLE_THEATERS = [
    {
        "name": "CGV 강남",
        "brand": "CGV",
        "location": "서울 강남구",
        "operating_hours": "09:00-24:00"
    },
    {
        "name": "롯데시네마 월드타워",
        "brand": "롯데시네마",
        "location": "서울 송파구",
        "operating_hours": "08:00-02:00"
    },
    {
        "name": "메가박스 코엑스",
        "brand": "메가박스",
        "location": "서울 강남구",
        "operating_hours": "09:00-01:00"
    }
]

SAMPLE_MOVIES = [
    {
        "title": "오펜하이머",
        "distributor": "유니버설 픽처스",
        "ticket_price": 14000,
        "runtime_minutes": 180,
        "genre": "드라마"
    },
    {
        "title": "파묘",
        "distributor": "쇼박스",
        "ticket_price": 13000,
        "runtime_minutes": 134,
        "genre": "오컬트"
    },
    {
        "title": "듄: 파트2",
        "distributor": "워너브라더스",
        "ticket_price": 15000,
        "runtime_minutes": 166,
        "genre": "SF"
    }
]


def _check_db_presence() -> tuple[bool, bool]:
    """
    Check if theaters and movies exist in DB.
    Returns: (has_theaters, has_movies)
    """
    with session_scope() as session:
        has_theaters = session.exec(select(Theater.id).limit(1)).first() is not None
        has_movies = session.exec(select(Movie.id).limit(1)).first() is not None
        return has_theaters, has_movies


def _load_json_file(file_path: Path) -> list[dict] | None:
    """
    Load and validate JSON file.
    Returns None if file doesn't exist or has structural errors.
    """
    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            logger.warning(f"JSON file {file_path} top-level is not an array, skipping")
            return None

        return data
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON file {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None


def _seed_theaters(session, theater_data: list[dict]) -> int:
    """
    Seed theaters from data. Returns count of successful insertions.
    """
    success_count = 0

    for item in theater_data:
        try:
            theater_id = item.get("id") or str(uuid4())
            theater = Theater(
                id=theater_id,
                name=item["name"],
                brand=item["brand"],
                location=item["location"],
                operating_hours=item["operating_hours"]
            )
            session.add(theater)
            success_count += 1
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Skipping invalid theater record: {e}")
            continue

    return success_count


def _seed_movies(session, movie_data: list[dict]) -> int:
    """
    Seed movies from data. Returns count of successful insertions.
    Validates theater_id references against DB.
    """
    # Get existing theater IDs
    result = session.exec(select(Theater.id))
    existing_theater_ids = set(result.all())

    success_count = 0

    for item in movie_data:
        try:
            # Validate theater_id exists
            theater_id = item["theater_id"]
            if theater_id not in existing_theater_ids:
                logger.warning(f"Skipping movie '{item.get('title')}': theater_id {theater_id} not found")
                continue

            movie_id = item.get("id") or str(uuid4())
            movie = Movie(
                id=movie_id,
                title=item["title"],
                distributor=item["distributor"],
                ticket_price=int(item["ticket_price"]),
                runtime_minutes=int(item["runtime_minutes"]),
                genre=item["genre"],
                theater_id=theater_id
            )
            session.add(movie)
            success_count += 1
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Skipping invalid movie record: {e}")
            continue

    return success_count


def _seed_from_embedded_data(session) -> bool:
    """
    Seed database with embedded sample data.
    Returns True if successful.
    """
    logger.info("Seeding from embedded sample data")

    # Create theaters with generated IDs
    theater_ids = []
    for theater_data in SAMPLE_THEATERS:
        theater_id = str(uuid4())
        theater = Theater(
            id=theater_id,
            **theater_data
        )
        session.add(theater)
        theater_ids.append(theater_id)

    # Create movies linked to theaters
    for i, movie_data in enumerate(SAMPLE_MOVIES):
        movie = Movie(
            id=str(uuid4()),
            **movie_data,
            theater_id=theater_ids[i % len(theater_ids)]
        )
        session.add(movie)

    session.flush()
    logger.info(f"Seeded {len(SAMPLE_THEATERS)} theaters and {len(SAMPLE_MOVIES)} movies from embedded data")
    return True


def seed_database_if_empty():
    """
    Main entry point for database seeding.
    Seeds data only if DB is empty, with priority:
    1. Load from data/theaters.json and data/movies.json
    2. Fallback to embedded sample data
    Supports partial backfill (movies only if theaters exist).
    """
    has_theaters, has_movies = _check_db_presence()

    # Skip if DB already has data
    if has_theaters and has_movies:
        logger.info("Database already contains data, skipping seed")
        return

    project_root = find_project_root()
    theaters_json = project_root / "data" / "theaters.json"
    movies_json = project_root / "data" / "movies.json"

    with session_scope() as session:
        theater_count = 0
        movie_count = 0

        # Seed theaters if needed
        if not has_theaters:
            theater_data = _load_json_file(theaters_json)
            if theater_data:
                theater_count = _seed_theaters(session, theater_data)
                logger.info(f"Loaded {theater_count} theaters from {theaters_json}")
            else:
                # No JSON file or invalid, use embedded data
                if _seed_from_embedded_data(session):
                    logger.info("Seeded theaters and movies from embedded data")
                    return
                else:
                    raise RuntimeError("Failed to seed database with embedded data")

        # Seed movies if needed (including partial backfill)
        if not has_movies:
            movie_data = _load_json_file(movies_json)
            if movie_data:
                movie_count = _seed_movies(session, movie_data)
                logger.info(f"Loaded {movie_count} movies from {movies_json}")
            elif not has_theaters:
                # Already handled by embedded data above
                pass
            else:
                # Partial backfill: theaters exist but no movies, and no JSON
                logger.warning("No movies.json found for partial backfill")

        # Commit only if we successfully inserted at least one record
        if theater_count > 0 or movie_count > 0:
            session.flush()
            logger.info(f"Seed completed: {theater_count} theaters, {movie_count} movies")
        elif not has_theaters and not has_movies:
            # Complete failure, rollback
            raise RuntimeError("Failed to seed any data")
