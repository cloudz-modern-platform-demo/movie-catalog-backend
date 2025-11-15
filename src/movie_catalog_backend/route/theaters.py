from fastapi import APIRouter, status
from ..scheme.theater import TheaterCreate, TheaterUpdate, TheaterRead
from ..scheme.movie import MovieRead
from ..service import theater_service

router = APIRouter(prefix="/theaters", tags=["theaters"])


@router.post("/", response_model=TheaterRead, status_code=status.HTTP_201_CREATED)
def create_theater(theater: TheaterCreate):
    """Create a new theater"""
    return theater_service.create_theater(theater)


@router.get("/", response_model=list[TheaterRead])
def list_theaters():
    """List all theaters"""
    return theater_service.get_theaters()


@router.get("/{theater_id}", response_model=TheaterRead)
def get_theater(theater_id: str):
    """Get a specific theater by ID"""
    return theater_service.get_theater(theater_id)


@router.put("/{theater_id}", response_model=TheaterRead)
def update_theater(theater_id: str, theater: TheaterUpdate):
    """Update a theater (partial update allowed)"""
    return theater_service.update_theater(theater_id, theater)


@router.delete("/{theater_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_theater(theater_id: str):
    """Delete a theater (fails if it has associated movies)"""
    theater_service.delete_theater(theater_id)


@router.get("/{theater_id}/movies", response_model=list[MovieRead])
def get_theater_movies(theater_id: str):
    """Get all movies for a specific theater"""
    return theater_service.get_theater_movies(theater_id)
