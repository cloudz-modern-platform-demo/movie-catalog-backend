from uuid import uuid4
from sqlmodel import select
from fastapi import HTTPException
from ..db.session import session_scope
from ..entity.models import Theater, Movie
from ..scheme.theater import TheaterCreate, TheaterUpdate, TheaterRead


def _theater_to_dict(theater: Theater) -> dict:
    """Convert Theater entity to dict within session context"""
    return {
        "id": theater.id,
        "name": theater.name,
        "brand": theater.brand,
        "location": theater.location,
        "operating_hours": theater.operating_hours
    }


def create_theater(theater_data: TheaterCreate) -> TheaterRead:
    """Create a new theater"""
    with session_scope() as session:
        theater = Theater(
            id=str(uuid4()),
            **theater_data.model_dump()
        )
        session.add(theater)
        session.flush()
        return TheaterRead(**_theater_to_dict(theater))


def get_theaters() -> list[TheaterRead]:
    """Get all theaters"""
    with session_scope() as session:
        theaters = session.exec(select(Theater)).all()
        return [TheaterRead(**_theater_to_dict(t)) for t in theaters]


def get_theater(theater_id: str) -> TheaterRead:
    """Get a single theater by ID"""
    with session_scope() as session:
        theater = session.get(Theater, theater_id)
        if not theater:
            raise HTTPException(status_code=404, detail=f"Theater {theater_id} not found")
        return TheaterRead(**_theater_to_dict(theater))


def update_theater(theater_id: str, theater_data: TheaterUpdate) -> TheaterRead:
    """Update a theater (partial update)"""
    with session_scope() as session:
        theater = session.get(Theater, theater_id)
        if not theater:
            raise HTTPException(status_code=404, detail=f"Theater {theater_id} not found")

        # Apply partial updates
        update_dict = theater_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(theater, key, value)

        session.add(theater)
        session.flush()
        return TheaterRead(**_theater_to_dict(theater))


def delete_theater(theater_id: str) -> None:
    """
    Delete a theater.
    Raises 409 if theater has associated movies.
    """
    with session_scope() as session:
        theater = session.get(Theater, theater_id)
        if not theater:
            raise HTTPException(status_code=404, detail=f"Theater {theater_id} not found")

        # Check for associated movies
        movies = session.exec(
            select(Movie).where(Movie.theater_id == theater_id)
        ).first()

        if movies:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete theater {theater_id}: has associated movies"
            )

        session.delete(theater)


def get_theater_movies(theater_id: str) -> list:
    """Get all movies for a specific theater"""
    from ..scheme.movie import MovieRead
    from .movie_service import _movie_to_dict

    with session_scope() as session:
        # Verify theater exists
        theater = session.get(Theater, theater_id)
        if not theater:
            raise HTTPException(status_code=404, detail=f"Theater {theater_id} not found")

        # Get movies
        movies = session.exec(
            select(Movie).where(Movie.theater_id == theater_id)
        ).all()

        return [MovieRead(**_movie_to_dict(m)) for m in movies]
