"""데이터베이스 세션 및 엔진 관리"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from movie_catalog_backend.db.config import get_database_url


# 엔진 생성
DATABASE_URL = get_database_url()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite용 설정
    echo=False
)


# SQLite에서 외래 키 제약 활성화
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """SQLite PRAGMA 설정"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_db():
    """데이터베이스 테이블 생성"""
    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """데이터베이스 세션 컨텍스트 매니저"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

