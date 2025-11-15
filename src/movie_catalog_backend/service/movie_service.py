"""Movie 서비스 계층"""
from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException
from sqlmodel import select

from movie_catalog_backend.db.session import session_scope
from movie_catalog_backend.entity.models import Movie, Theater
from movie_catalog_backend.scheme.movie import MovieCreate, MovieRead, MovieUpdate


def _movie_to_dict(movie: Movie) -> dict:
    """Movie 엔티티를 딕셔너리로 변환 (DetachedInstanceError 방지)"""
    return {
        "id": movie.id,
        "title": movie.title,
        "distributor": movie.distributor,
        "ticket_price": movie.ticket_price,
        "runtime_minutes": movie.runtime_minutes,
        "genre": movie.genre,
        "theater_id": movie.theater_id
    }


def get_all_movies(theater_id: Optional[str] = None) -> List[MovieRead]:
    """전체 영화 목록 조회 (theater_id 필터 지원)"""
    with session_scope() as session:
        query = select(Movie)
        if theater_id:
            query = query.where(Movie.theater_id == theater_id)
        
        movies = session.exec(query).all()
        return [MovieRead(**_movie_to_dict(m)) for m in movies]


def get_movie(movie_id: str) -> MovieRead:
    """특정 영화 조회"""
    with session_scope() as session:
        movie = session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return MovieRead(**_movie_to_dict(movie))


def create_movie(movie_data: MovieCreate) -> MovieRead:
    """영화 생성 (유효한 극장 ID 필요)"""
    with session_scope() as session:
        # theater_id 존재 여부 확인
        theater = session.get(Theater, movie_data.theater_id)
        if not theater:
            raise HTTPException(status_code=422, detail="Invalid theater_id")
        
        movie = Movie(
            id=str(uuid4()),
            **movie_data.model_dump()
        )
        session.add(movie)
        session.commit()
        session.refresh(movie)
        return MovieRead(**_movie_to_dict(movie))


def update_movie(movie_id: str, movie_data: MovieUpdate) -> MovieRead:
    """영화 정보 수정"""
    with session_scope() as session:
        movie = session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # theater_id 변경 시 존재 여부 확인
        update_dict = movie_data.model_dump(exclude_unset=True)
        if "theater_id" in update_dict:
            theater = session.get(Theater, update_dict["theater_id"])
            if not theater:
                raise HTTPException(status_code=422, detail="Invalid theater_id")
        
        # 부분 업데이트
        for key, value in update_dict.items():
            setattr(movie, key, value)
        
        session.add(movie)
        session.commit()
        session.refresh(movie)
        return MovieRead(**_movie_to_dict(movie))


def delete_movie(movie_id: str) -> None:
    """영화 삭제"""
    with session_scope() as session:
        movie = session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        session.delete(movie)
        session.commit()

