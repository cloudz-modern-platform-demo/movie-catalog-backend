from fastapi import APIRouter, status, Query
from ..scheme.movie import MovieCreate, MovieUpdate, MovieRead
from ..service import movie_service

router = APIRouter(tags=["movies"])


@router.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate):
    """Create a new movie"""
    return movie_service.create_movie(movie)


@router.get("/movies", response_model=list[MovieRead])
def list_movies(theater_id: str | None = Query(default=None)):
    """List all movies, optionally filtered by theater_id"""
    return movie_service.get_movies(theater_id)


@router.get("/movies/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: str):
    """Get a specific movie by ID"""
    return movie_service.get_movie(movie_id)


@router.put("/movies/{movie_id}", response_model=MovieRead)
def update_movie(movie_id: str, movie: MovieUpdate):
    """Update a movie (partial update allowed)"""
    return movie_service.update_movie(movie_id, movie)


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: str):
    """Delete a movie"""
    movie_service.delete_movie(movie_id)
