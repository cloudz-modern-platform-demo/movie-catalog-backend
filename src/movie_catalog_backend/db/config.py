"""데이터베이스 설정 및 프로젝트 루트 탐색"""
import os
from pathlib import Path


def find_project_root() -> Path:
    """프로젝트 루트 디렉토리 탐색 (pyproject.toml 기준)"""
    current = Path.cwd()
    
    # 현재 디렉토리부터 상위로 올라가며 pyproject.toml 찾기
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    
    # 찾지 못하면 현재 디렉토리 반환
    return current


def get_database_url() -> str:
    """데이터베이스 URL 결정"""
    # 환경변수가 있으면 우선 사용
    if env_url := os.getenv("DATABASE_URL"):
        return env_url
    
    # 기본값: 프로젝트 루트의 data/movie_catalog.db
    project_root = find_project_root()
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "movie_catalog.db"
    return f"sqlite:///{db_path}"

