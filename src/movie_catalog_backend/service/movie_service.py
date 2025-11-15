from uuid import uuid4
from sqlmodel import select
from fastapi import HTTPException
from ..db.session import session_scope
from ..entity.models import Movie, Theater
from ..scheme.movie import MovieCreate, MovieUpdate, MovieRead


def _movie_to_dict(movie: Movie) -> dict:
    """Convert Movie entity to dict within session context"""
    return {
        "id": movie.id,
        "title": movie.title,
        "distributor": movie.distributor,
        "ticket_price": movie.ticket_price,
        "runtime_minutes": movie.runtime_minutes,
        "genre": movie.genre,
        "theater_id": movie.theater_id
    }


def _validate_theater_exists(session, theater_id: str) -> None:
    """Validate that a theater exists, raise 422 if not"""
    theater = session.get(Theater, theater_id)
    if not theater:
        raise HTTPException(
            status_code=422,
            detail=f"Theater {theater_id} does not exist"
        )


def create_movie(movie_data: MovieCreate) -> MovieRead:
    """Create a new movie"""
    with session_scope() as session:
        # Validate theater exists
        _validate_theater_exists(session, movie_data.theater_id)

        movie = Movie(
            id=str(uuid4()),
            **movie_data.model_dump()
        )
        session.add(movie)
        session.flush()
        return MovieRead(**_movie_to_dict(movie))


def get_movies(theater_id: str | None = None) -> list[MovieRead]:
    """Get all movies, optionally filtered by theater_id"""
    with session_scope() as session:
        query = select(Movie)
        if theater_id:
            query = query.where(Movie.theater_id == theater_id)

        movies = session.exec(query).all()
        return [MovieRead(**_movie_to_dict(m)) for m in movies]


def get_movie(movie_id: str) -> MovieRead:
    """Get a single movie by ID"""
    with session_scope() as session:
        movie = session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")
        return MovieRead(**_movie_to_dict(movie))


def update_movie(movie_id: str, movie_data: MovieUpdate) -> MovieRead:
    """Update a movie (partial update)"""
    with session_scope() as session:
        movie = session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")

        # Apply partial updates
        update_dict = movie_data.model_dump(exclude_unset=True)

        # If theater_id is being changed, validate it exists
        if "theater_id" in update_dict:
            _validate_theater_exists(session, update_dict["theater_id"])

        for key, value in update_dict.items():
            setattr(movie, key, value)

        session.add(movie)
        session.flush()
        return MovieRead(**_movie_to_dict(movie))


def delete_movie(movie_id: str) -> None:
    """Delete a movie"""
    with session_scope() as session:
        movie = session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")

        session.delete(movie)
