"""데이터베이스 초기 시드 및 마이그레이션"""
import json
import logging
from pathlib import Path
from typing import Any, List
from uuid import uuid4

from sqlmodel import select

from movie_catalog_backend.db.config import find_project_root
from movie_catalog_backend.db.session import session_scope
from movie_catalog_backend.entity.models import Movie, Theater

logger = logging.getLogger(__name__)


# 내장 샘플 데이터
SAMPLE_THEATERS = [
    {
        "id": "33bd96af-0431-47fc-aaad-08107e268393",
        "name": "CGV 강남",
        "brand": "CGV",
        "location": "서울 강남구 역삼동",
        "operating_hours": "09:00-24:00"
    },
    {
        "id": "343f8b25-22e0-4d49-a75a-5ba34a69f1bf",
        "name": "롯데시네마 월드타워",
        "brand": "롯데시네마",
        "location": "서울 송파구 잠실동",
        "operating_hours": "08:00-02:00"
    },
    {
        "id": "8d94bf5f-0cd5-4d19-b6ae-ce35fa59dfb4",
        "name": "메가박스 코엑스",
        "brand": "메가박스",
        "location": "서울 강남구 삼성동",
        "operating_hours": "09:00-01:00"
    },
    {
        "id": "e78327f8-469e-45e3-8873-c2bdf84ad038",
        "name": "CGV 용산아이파크몰",
        "brand": "CGV",
        "location": "서울 용산구 한강로3가",
        "operating_hours": "09:30-23:30"
    },
    {
        "id": "deecc0da-b267-41d3-95e2-61101c1b1107",
        "name": "롯데시네마 건대입구",
        "brand": "롯데시네마",
        "location": "서울 광진구 화양동",
        "operating_hours": "09:00-24:00"
    }
]

SAMPLE_MOVIES = [
    {
        "title": "오펜하이머",
        "distributor": "유니버설 픽처스",
        "ticket_price": 14000,
        "runtime_minutes": 180,
        "genre": "드라마",
        "theater_id": "33bd96af-0431-47fc-aaad-08107e268393"
    },
    {
        "title": "파묘",
        "distributor": "쇼박스",
        "ticket_price": 13000,
        "runtime_minutes": 134,
        "genre": "오컬트",
        "theater_id": "343f8b25-22e0-4d49-a75a-5ba34a69f1bf"
    },
    {
        "title": "듄: 파트2",
        "distributor": "워너브라더스",
        "ticket_price": 15000,
        "runtime_minutes": 166,
        "genre": "SF",
        "theater_id": "8d94bf5f-0cd5-4d19-b6ae-ce35fa59dfb4"
    }
]


def _load_json_file(file_path: Path) -> List[dict] | None:
    """JSON 파일 로드 (구조적 오류 시 None 반환)"""
    try:
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 최상위가 배열이 아니면 구조적 오류
        if not isinstance(data, list):
            logger.warning(f"{file_path}: 최상위 타입이 배열이 아님")
            return None
        
        return data
    except json.JSONDecodeError as e:
        logger.warning(f"{file_path}: JSON 파싱 실패 - {e}")
        return None
    except Exception as e:
        logger.warning(f"{file_path}: 파일 읽기 실패 - {e}")
        return None


def _insert_theaters(session: Any, theaters_data: List[dict]) -> int:
    """극장 데이터 삽입 (성공한 개수 반환)"""
    success_count = 0
    
    for theater_dict in theaters_data:
        try:
            # id가 없으면 자동 생성
            if "id" not in theater_dict or not theater_dict["id"]:
                theater_dict["id"] = str(uuid4())
            
            # 필수 필드 검증
            required = ["id", "name", "brand", "location", "operating_hours"]
            if not all(field in theater_dict for field in required):
                logger.warning(f"극장 레코드 스킵: 필수 필드 누락 - {theater_dict.get('name', 'unknown')}")
                continue
            
            theater = Theater(
                id=theater_dict["id"],
                name=theater_dict["name"],
                brand=theater_dict["brand"],
                location=theater_dict["location"],
                operating_hours=theater_dict["operating_hours"]
            )
            session.add(theater)
            success_count += 1
        except Exception as e:
            logger.warning(f"극장 레코드 스킵: {theater_dict.get('name', 'unknown')} - {e}")
            continue
    
    return success_count


def _insert_movies(session: Any, movies_data: List[dict]) -> int:
    """영화 데이터 삽입 (성공한 개수 반환)"""
    # 기존 극장 ID 목록 조회
    result = session.exec(select(Theater.id))
    existing_theater_ids = set(result.all())
    
    success_count = 0
    
    for movie_dict in movies_data:
        try:
            # theater_id 참조 무결성 검증
            if "theater_id" not in movie_dict or movie_dict["theater_id"] not in existing_theater_ids:
                logger.warning(f"영화 레코드 스킵: 유효하지 않은 theater_id - {movie_dict.get('title', 'unknown')}")
                continue
            
            # id가 없으면 자동 생성
            if "id" not in movie_dict or not movie_dict["id"]:
                movie_dict["id"] = str(uuid4())
            
            # 필수 필드 검증
            required = ["id", "title", "distributor", "ticket_price", "runtime_minutes", "genre", "theater_id"]
            if not all(field in movie_dict for field in required):
                logger.warning(f"영화 레코드 스킵: 필수 필드 누락 - {movie_dict.get('title', 'unknown')}")
                continue
            
            # 타입 검증
            if not isinstance(movie_dict["ticket_price"], int) or movie_dict["ticket_price"] < 0:
                logger.warning(f"영화 레코드 스킵: 잘못된 ticket_price - {movie_dict.get('title', 'unknown')}")
                continue
            
            if not isinstance(movie_dict["runtime_minutes"], int) or movie_dict["runtime_minutes"] < 0:
                logger.warning(f"영화 레코드 스킵: 잘못된 runtime_minutes - {movie_dict.get('title', 'unknown')}")
                continue
            
            movie = Movie(
                id=movie_dict["id"],
                title=movie_dict["title"],
                distributor=movie_dict["distributor"],
                ticket_price=movie_dict["ticket_price"],
                runtime_minutes=movie_dict["runtime_minutes"],
                genre=movie_dict["genre"],
                theater_id=movie_dict["theater_id"]
            )
            session.add(movie)
            success_count += 1
        except Exception as e:
            logger.warning(f"영화 레코드 스킵: {movie_dict.get('title', 'unknown')} - {e}")
            continue
    
    return success_count


def _check_db_empty(session: Any) -> tuple[bool, bool]:
    """DB가 비어있는지 확인 (theaters_empty, movies_empty)"""
    theaters_empty = session.exec(select(Theater.id).limit(1)).first() is None
    movies_empty = session.exec(select(Movie.id).limit(1)).first() is None
    return theaters_empty, movies_empty


def seed_database_if_empty():
    """DB가 비어있을 때 1회 시드 수행"""
    with session_scope() as session:
        theaters_empty, movies_empty = _check_db_empty(session)
        
        # DB에 데이터가 모두 있으면 스킵
        if not theaters_empty and not movies_empty:
            logger.info("DB에 데이터가 이미 존재합니다. 시드를 스킵합니다.")
            return
        
        # 프로젝트 루트의 JSON 파일 경로
        project_root = find_project_root()
        theaters_json_path = project_root / "data" / "theaters.json"
        movies_json_path = project_root / "data" / "movies.json"
        
        total_theaters = 0
        total_movies = 0
        
        # 극장이 비어있으면 삽입
        if theaters_empty:
            logger.info("극장 데이터를 시드합니다...")
            
            # JSON 파일 우선 시도
            theaters_data = _load_json_file(theaters_json_path)
            if theaters_data is None:
                logger.info("theaters.json을 사용할 수 없습니다. 내장 샘플 데이터를 사용합니다.")
                theaters_data = SAMPLE_THEATERS
            
            total_theaters = _insert_theaters(session, theaters_data)
            
            if total_theaters == 0:
                logger.error("극장 데이터 삽입 실패: 모든 레코드가 실패했습니다.")
                session.rollback()
                return
            
            logger.info(f"극장 {total_theaters}개 삽입 완료")
        
        # 영화가 비어있으면 삽입 (부분 백필 지원)
        if movies_empty:
            logger.info("영화 데이터를 시드합니다...")
            
            # JSON 파일 우선 시도
            movies_data = _load_json_file(movies_json_path)
            if movies_data is None:
                logger.info("movies.json을 사용할 수 없습니다. 내장 샘플 데이터를 사용합니다.")
                movies_data = SAMPLE_MOVIES
            
            total_movies = _insert_movies(session, movies_data)
            
            if total_movies == 0:
                logger.warning("영화 데이터 삽입 실패: 모든 레코드가 실패했습니다.")
                # 극장만 삽입된 경우는 롤백하지 않음 (부분 백필 허용)
                if theaters_empty and total_theaters > 0:
                    logger.info(f"극장 데이터는 성공적으로 삽입되었습니다.")
                else:
                    session.rollback()
                    return
            else:
                logger.info(f"영화 {total_movies}개 삽입 완료")
        
        # 최소 1건 이상 성공 시 커밋
        if total_theaters > 0 or total_movies > 0:
            session.commit()
            logger.info(f"시드 완료: 극장 {total_theaters}개, 영화 {total_movies}개")
        else:
            session.rollback()
            logger.error("시드 실패: 삽입된 레코드가 없습니다.")

