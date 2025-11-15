"""Movie Catalog Backend 메인 진입점"""
import os


def main():
    """애플리케이션 메인 진입점"""
    import uvicorn
    
    # 환경변수 읽기
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    # 포트는 8000 고정
    port = 8000
    
    # uvicorn을 factory 모드로 실행
    uvicorn.run(
        "movie_catalog_backend.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    main()

