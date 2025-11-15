"""Movie API 라우터"""
from typing import List, Optional

from fastapi import APIRouter, Query, Response, status

from movie_catalog_backend.scheme.movie import MovieCreate, MovieRead, MovieUpdate
from movie_catalog_backend.service import movie_service

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=List[MovieRead])
def list_movies(theater_id: Optional[str] = Query(None)):
    """전체 영화 목록 조회 (theater_id 필터 지원)"""
    return movie_service.get_all_movies(theater_id)


@router.post("", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate):
    """영화 생성 (유효한 극장 ID 필요)"""
    return movie_service.create_movie(movie)


@router.get("/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: str):
    """특정 영화 조회"""
    return movie_service.get_movie(movie_id)


@router.put("/{movie_id}", response_model=MovieRead)
def update_movie(movie_id: str, movie: MovieUpdate):
    """영화 정보 수정"""
    return movie_service.update_movie(movie_id, movie)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: str):
    """영화 삭제"""
    movie_service.delete_movie(movie_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

