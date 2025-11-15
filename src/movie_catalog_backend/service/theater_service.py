"""Theater 서비스 계층"""
from typing import List
from uuid import uuid4

from fastapi import HTTPException
from sqlmodel import select

from movie_catalog_backend.db.session import session_scope
from movie_catalog_backend.entity.models import Movie, Theater
from movie_catalog_backend.scheme.theater import TheaterCreate, TheaterRead, TheaterUpdate


def _theater_to_dict(theater: Theater) -> dict:
    """Theater 엔티티를 딕셔너리로 변환 (DetachedInstanceError 방지)"""
    return {
        "id": theater.id,
        "name": theater.name,
        "brand": theater.brand,
        "location": theater.location,
        "operating_hours": theater.operating_hours
    }


def get_all_theaters() -> List[TheaterRead]:
    """전체 극장 목록 조회"""
    with session_scope() as session:
        theaters = session.exec(select(Theater)).all()
        return [TheaterRead(**_theater_to_dict(t)) for t in theaters]


def get_theater(theater_id: str) -> TheaterRead:
    """특정 극장 조회"""
    with session_scope() as session:
        theater = session.get(Theater, theater_id)
        if not theater:
            raise HTTPException(status_code=404, detail="Theater not found")
        return TheaterRead(**_theater_to_dict(theater))


def create_theater(theater_data: TheaterCreate) -> TheaterRead:
    """극장 생성"""
    with session_scope() as session:
        theater = Theater(
            id=str(uuid4()),
            **theater_data.model_dump()
        )
        session.add(theater)
        session.commit()
        session.refresh(theater)
        return TheaterRead(**_theater_to_dict(theater))


def update_theater(theater_id: str, theater_data: TheaterUpdate) -> TheaterRead:
    """극장 정보 수정"""
    with session_scope() as session:
        theater = session.get(Theater, theater_id)
        if not theater:
            raise HTTPException(status_code=404, detail="Theater not found")
        
        # 부분 업데이트
        update_dict = theater_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(theater, key, value)
        
        session.add(theater)
        session.commit()
        session.refresh(theater)
        return TheaterRead(**_theater_to_dict(theater))


def delete_theater(theater_id: str) -> None:
    """극장 삭제 (연결된 영화가 있으면 삭제 차단)"""
    with session_scope() as session:
        theater = session.get(Theater, theater_id)
        if not theater:
            raise HTTPException(status_code=404, detail="Theater not found")
        
        # 연결된 영화가 있는지 확인
        movies = session.exec(select(Movie).where(Movie.theater_id == theater_id)).first()
        if movies:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete theater with associated movies"
            )
        
        session.delete(theater)
        session.commit()


def get_theater_movies(theater_id: str) -> List[dict]:
    """특정 극장의 영화 목록 조회"""
    with session_scope() as session:
        # 극장 존재 여부 확인
        theater = session.get(Theater, theater_id)
        if not theater:
            raise HTTPException(status_code=404, detail="Theater not found")
        
        # 영화 목록 조회
        movies = session.exec(select(Movie).where(Movie.theater_id == theater_id)).all()
        return [
            {
                "id": m.id,
                "title": m.title,
                "distributor": m.distributor,
                "ticket_price": m.ticket_price,
                "runtime_minutes": m.runtime_minutes,
                "genre": m.genre,
                "theater_id": m.theater_id
            }
            for m in movies
        ]

