"""FastAPI 애플리케이션 팩토리"""
import logging

from fastapi import FastAPI

from movie_catalog_backend.db.seed import seed_database_if_empty
from movie_catalog_backend.db.session import init_db
from movie_catalog_backend.route import movies, theaters

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """FastAPI 앱 생성 및 설정"""
    app = FastAPI(
        title="Movie Catalog Backend",
        description="영화관 및 영화 정보 관리 백엔드 API",
        version="0.1.0"
    )
    
    # 라우터 등록
    app.include_router(theaters.router)
    app.include_router(movies.router)
    
    # 시작 이벤트
    @app.on_event("startup")
    async def startup_event():
        """앱 시작 시 DB 초기화 및 시드"""
        logger.info("앱 시작: DB 초기화 중...")
        init_db()
        logger.info("DB 테이블 생성 완료")
        
        logger.info("시드 데이터 확인 중...")
        seed_database_if_empty()
        logger.info("시드 데이터 확인 완료")
    
    return app

