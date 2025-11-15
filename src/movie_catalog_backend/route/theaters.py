"""Theater API 라우터"""
from typing import List

from fastapi import APIRouter, Response, status

from movie_catalog_backend.scheme.theater import TheaterCreate, TheaterRead, TheaterUpdate
from movie_catalog_backend.service import theater_service

router = APIRouter(prefix="/theaters", tags=["theaters"])


@router.get("", response_model=List[TheaterRead])
def list_theaters():
    """전체 극장 목록 조회"""
    return theater_service.get_all_theaters()


@router.post("", response_model=TheaterRead, status_code=status.HTTP_201_CREATED)
def create_theater(theater: TheaterCreate):
    """극장 생성"""
    return theater_service.create_theater(theater)


@router.get("/{theater_id}", response_model=TheaterRead)
def get_theater(theater_id: str):
    """특정 극장 조회"""
    return theater_service.get_theater(theater_id)


@router.put("/{theater_id}", response_model=TheaterRead)
def update_theater(theater_id: str, theater: TheaterUpdate):
    """극장 정보 수정"""
    return theater_service.update_theater(theater_id, theater)


@router.delete("/{theater_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_theater(theater_id: str):
    """극장 삭제 (연결된 영화가 있으면 409 에러)"""
    theater_service.delete_theater(theater_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{theater_id}/movies", response_model=List[dict])
def get_theater_movies(theater_id: str):
    """특정 극장의 영화 목록 조회"""
    return theater_service.get_theater_movies(theater_id)

