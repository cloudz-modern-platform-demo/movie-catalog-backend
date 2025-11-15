# Movie Catalog Backend

영화관과 영화 정보를 관리하는 SQLite 기반 백엔드 API

## 주요 기능

- 영화관 CRUD 작업
- 영화 CRUD 작업 (영화관과 연결)
- JSON 파일을 통한 자동 데이터 시딩
- 외래 키 제약 조건 및 참조 무결성
- FastAPI 기반 REST API와 자동 문서화

## 요구사항

- Python 3.12+
- uv (패키지 매니저)

## 설치

```bash
uv sync
```

## 애플리케이션 실행

```bash
uv run movie-catalog-backend
```

서버는 `http://localhost:8000`에서 시작됩니다 (포트 고정).

### 환경 변수

- `HOST`: 서버 호스트 (기본값: `0.0.0.0`)
- `RELOAD`: 자동 리로드 활성화 (기본값: `true`)
- `DATABASE_URL`: 데이터베이스 경로 (기본값: `data/movie_catalog.db`)

## API 문서

서버 실행 후 다음 URL에서 확인:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI 스펙: http://localhost:8000/openapi.json

## API 엔드포인트

### 영화관 (Theaters)

- `GET /theaters/` - 모든 영화관 목록 조회
- `POST /theaters/` - 영화관 생성
- `GET /theaters/{id}` - 특정 영화관 조회
- `PUT /theaters/{id}` - 영화관 정보 수정
- `DELETE /theaters/{id}` - 영화관 삭제 (연결된 영화가 있으면 실패)
- `GET /theaters/{id}/movies` - 특정 영화관의 영화 목록 조회

### 영화 (Movies)

- `GET /movies/` - 모든 영화 목록 조회 (`?theater_id=` 필터 지원)
- `POST /movies/` - 영화 생성
- `GET /movies/{id}` - 특정 영화 조회
- `PUT /movies/{id}` - 영화 정보 수정
- `DELETE /movies/{id}` - 영화 삭제

## 데이터 초기화

첫 시작 시 자동으로 데이터를 시딩합니다:

1. 우선순위 1: `data/theaters.json`과 `data/movies.json`에서 로드
2. 우선순위 2: JSON 파일이 없으면 내장 샘플 데이터 사용

## 프로젝트 구조

```
src/movie_catalog_backend/
├── entity/          # SQLModel 데이터베이스 모델
├── scheme/          # Pydantic 요청/응답 스키마
├── db/              # 데이터베이스 설정 및 시딩
├── service/         # 비즈니스 로직 계층
├── route/           # FastAPI 라우트 핸들러
└── app.py           # 애플리케이션 팩토리
```

## 개발 가이드

자세한 개발 가이드라인은 [CLAUDE.md](CLAUDE.md)를 참조하세요.

## 예제 사용법

### 영화관 생성
```bash
curl -X POST http://localhost:8000/theaters/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CGV 강남",
    "brand": "CGV",
    "location": "서울 강남구",
    "operating_hours": "09:00-24:00"
  }'
```

### 영화 생성
```bash
curl -X POST http://localhost:8000/movies/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "오펜하이머",
    "distributor": "유니버설",
    "ticket_price": 14000,
    "runtime_minutes": 180,
    "genre": "드라마",
    "theater_id": "{theater_id}"
  }'
```

### 특정 영화관의 영화 조회
```bash
curl http://localhost:8000/theaters/{theater_id}/movies
```

## 기술 스택

- **Web Framework**: FastAPI 0.110+
- **ORM**: SQLModel 0.0.21+
- **Database**: SQLite
- **Validation**: Pydantic v2
- **Server**: Uvicorn
- **Package Manager**: uv

## 라이선스

MIT License
