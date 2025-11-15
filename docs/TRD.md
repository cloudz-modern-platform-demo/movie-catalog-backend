# 영화 카탈로그 백엔드 TRD

## 1. 시스템 개요
- 언어/런타임: Python 3.12 / FastAPI 0.110
- 앱 구조: `src/movie_catalog_backend` 모듈, 스크립트 진입점 `movie-catalog-backend` → `movie_catalog_backend:main`
- 서버 런타임: `uvicorn`을 import string + factory(`"movie_catalog_backend.app:create_app"`) 방식으로 구동
- 포트 정책: 포트는 8000 고정(`PORT` 환경변수 무시), 환경변수는 `HOST`, `RELOAD`, `DATABASE_URL`만 사용
- 데이터 저장: `data/movie_catalog.db` SQLite 파일 사용. 앱 시작 시 DB가 비어있으면 1회 마이그레이션/시드 수행:
  - `data/theaters.json`, `data/movies.json`이 존재하면 우선 JSON을 DB로 마이그레이션
  - JSON이 없으면 내장 샘플 데이터를 시드
  - 프로젝트 루트 탐색 규칙: 실행 시 가장 가까운 상위 디렉터리의 `pyproject.toml`을 루트로 간주
  - 모든 데이터 경로는 프로젝트 루트 기준(`data/*.json`, `data/movie_catalog.db`)
  - SQLite 설정: `PRAGMA foreign_keys=ON`, `check_same_thread=False`
  - 부분 백필: DB에 Theater는 있으나 Movie가 없으면 재시작 시 영화만 자동 백필

## 2. 아키텍처 개요
- 계층형 구조: `route` → `service` → `db` → `entity`/`scheme` 로 책임 분리
- 앱 팩토리(`create_app`)와 startup 훅으로 DB 초기화 및 시드 1회 수행
- SQLite 단일 파일 저장소, 요청 단위 세션 운용, FK 강제 활성화

## 3. 주요 컴포넌트
| 파일 | 설명 |
| --- | --- |
| `db/config.py` | 프로젝트 루트 탐색 및 `DATABASE_URL` 결정. 미설정 시 `data/movie_catalog.db` 사용. |
| `db/session.py` | SQLModel 엔진/세션 생성, `init_db()`로 테이블 생성, SQLite FK 강제. |
| `db/seed.py` | DB 비어있을 때 1회 JSON→DB 마이그레이션, 실패 시 내장 시드 폴백. |
| `entity/models.py` | SQLModel 테이블: `Theater`, `Movie`(FK 기반, 관계 매핑 단순화). |
| `scheme/theater.py` | `TheaterCreate`, `TheaterUpdate`, `TheaterRead` Pydantic 모델. |
| `scheme/movie.py` | `MovieCreate`, `MovieUpdate`, `MovieRead` Pydantic 모델. |
| `service/theater_service.py` | 극장 CRUD, 삭제 제약(연결 영화 존재 시 금지 409) 검증. |
| `service/movie_service.py` | 영화 CRUD, `theater_id` 존재성 검증(미존재 422). |
| `route/theaters.py` | `/theaters` 라우터. |
| `route/movies.py` | `/movies` 라우터. |
| `app.py` | FastAPI 앱 팩토리 `create_app()`과 라우터 마운트, startup 훅. |
| `__init__.py` | `main()`에서 uvicorn을 factory 모드로 실행(포트 8000 고정). |

## 4. 데이터 모델
### 4.1 영화관 (Theater)
- `id: str` (UUID4, PK)
- `name: str` (NOT NULL)
- `brand: str` (NOT NULL)
- `location: str` (NOT NULL)
- `operating_hours: str` (예: `09:00-23:00`, NOT NULL)

### 4.2 영화 (Movie)
- `id: str` (UUID4, PK)
- `title: str` (NOT NULL)
- `distributor: str` (NOT NULL)
- `ticket_price: int` (0 이상 정수, NOT NULL)
- `runtime_minutes: int` (0 이상 정수, NOT NULL)
- `genre: str` (NOT NULL)
- `theater_id: str` (FK -> Theater.id, NOT NULL, ON DELETE RESTRICT)

## 5. API 설계
### 5.1 영화관
| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/theaters/` | 전체 영화관 목록 조회. |
| POST | `/theaters/` | 영화관 생성. |
| GET | `/theaters/{theater_id}` | 단일 영화관 조회. |
| PUT | `/theaters/{theater_id}` | 영화관 정보 수정(부분 갱신). |
| DELETE | `/theaters/{theater_id}` | 영화관 삭제. 연결된 영화 있으면 `409`. |
| GET | `/theaters/{theater_id}/movies` | 해당 영화관의 영화 목록. |

### 5.2 영화
| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/movies/` | 전체 영화 목록, `theater_id` Query 지원. |
| POST | `/movies/` | 영화 생성(유효한 영화관 ID 필요). |
| GET | `/movies/{movie_id}` | 단일 영화 조회. |
| PUT | `/movies/{movie_id}` | 영화 정보 수정. `theater_id` 변경 시 존재 확인. |
| DELETE | `/movies/{movie_id}` | 영화 삭제. |

## 6. 예외 및 검증 정책
- 존재하지 않는 리소스 요청: `404` + `{"detail": "... not found"}`.
- 영화관 삭제 시 연결된 영화 존재: `409`.
- 잘못된 입력(Pydantic 검증 실패): FastAPI 기본 `422`. 
- 정수/문자열 필드 길이 제한은 `models.py` 에 정의된 `Field` 조건을 따름.
### 6.1 JSON 마이그레이션 검증/오류 처리
- 위치: 프로젝트 루트 `data/theaters.json`, `data/movies.json`
- 포맷:
  - Theaters JSON: 배열. 각 객체는 `{ id?(UUID4), name, brand, location, operating_hours }`
  - Movies JSON: 배열. 각 객체는 `{ id?(UUID4), title, distributor, ticket_price(int>=0), runtime_minutes(int>=0), genre, theater_id(required) }`
- 동작:
  1. DB 완전 비어있으면(극장/영화 모두 없음) 트랜잭션 시작 → 극장 삽입 → 영화 삽입
  2. DB에 극장만 있고 영화가 없으면, 트랜잭션 시작 → 영화만 삽입(백필)
  3. 각 단계에서 레코드별 유효성 검증 실패 시 해당 레코드 스킵, 계속 진행
  4. `movies.json`에서 영화 일괄 삽입 시 `theater_id` 참조가 DB에 없으면 해당 레코드 스킵
  5. 최소 1건 이상 성공적으로 삽입되면 커밋. 전부 실패하면 롤백
- 구조적 오류(JSON 파싱 실패, 최상위 타입 불일치)는 전체 마이그레이션 실패로 간주하고 롤백
- 레코드 단위 오류는 스킵 처리하며 경고 로그를 남김(향후 관리를 위해 요약 출력)
 - 빈 DB 판단은 '존재 여부' 검사로 수행:
   - SQL 예: `SELECT 1 FROM theater LIMIT 1`, `SELECT 1 FROM movie LIMIT 1`
   - ORM(SQLModel) 예: `session.exec(select(Theater.id).limit(1)).first() is None`
 - 성공 커밋 조건: 극장 또는 영화 중 최소 1건 이상 삽입 성공

## 7. 동시성 및 저장 전략
- SQLite 트랜잭션을 사용하여 다중 요청 시 일관성 보장.
- 커넥션은 요청 단위 세션으로 분리하고 커밋/롤백을 명확히 처리.
- DB 파일은 프로젝트 루트 `data/movie_catalog.db`에 위치하며, `DATABASE_URL`로 오버라이드 가능.

## 8. 배포/실행
- 로컬 실행: `uv run movie-catalog-backend` 또는 `python -m movie_catalog_backend`
- 환경변수: `HOST`(기본 `0.0.0.0`), `RELOAD`(기본 `true`), `DATABASE_URL`(옵션)
  - 포트는 8000으로 고정(`PORT` 환경변수는 무시)
  - `DATABASE_URL` 미지정 시 프로젝트 루트 `data/movie_catalog.db` 사용

## 8.1 API 문서(FASTAPI)
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- FastAPI 내장 OpenAPI 스펙은 `GET /openapi.json` 으로 제공됨

## 9. 로깅/모니터링
- 응답 코드/지연(ms)/결과 개수 로그화
- DB 예외 시 에러 로그 및 롤백

## 10. 테스트 전략
- 단위 테스트 (추가 예정): 레포지토리 CRUD, 라우터 응답 코드, 영화관/영화 관계 검증.
- 현재는 수동 테스트(예: `httpie`, `curl`, `FastAPI docs UI`)로 시나리오 검증.

## 11. 폴더/모듈 구조
실제 코드 배치를 다음과 같이 구분한다. 

```
src/movie_catalog_backend/
  entity/
    models.py            # SQLModel 테이블: Theater, Movie (FK 중심)
  scheme/
    theater.py           # TheaterCreate/TheaterUpdate/TheaterRead
    movie.py             # MovieCreate/MovieUpdate/MovieRead
  db/
    config.py            # 프로젝트 루트 탐색, DATABASE_URL 결정
    session.py           # 엔진/세션, init_db()
    seed.py              # DB 비었을 때 1회 JSON→DB 마이그레이션/시드
  service/
    theater_service.py   # 극장 CRUD, 삭제 제약(연결 영화 존재 시 금지)
    movie_service.py     # 영화 CRUD, theater_id 존재성 검증
  route/
    theaters.py          # /theaters 라우터
    movies.py            # /movies 라우터
```

- 설계 원칙
  - ORM 관계 매핑은 단순화(FK만 사용), 조인은 서비스 쿼리로 처리.
  - route는 입출력 경계에 집중, 규칙은 service에서 일괄 처리.
  - db는 실행 환경 의존 로직을 캡슐화하여 다른 계층에서 재사용.
  - scheme은 외부 계약(API)의 안정성을 위해 입력/출력 분리.

## 12. 구현 규약 및 금지 사항(오류 예방)
- 세션 관리(중요):
  - 세션은 서비스 계층이 `session_scope()`로 소유/관리한다.
  - 라우터에서 DB 세션을 의존성 주입(`Depends(get_session)`)으로 받지 않는다.
  - `movie_catalog_backend.db.session`은 `get_session`을 공개하지 않는다. 라우터에서 임포트 금지.
  - **DetachedInstanceError 방지**: 서비스 함수는 세션 종료 전에 SQLModel 엔티티를 스키마 객체(TheaterRead/MovieRead)로 변환하여 반환한다. 세션이 종료된 후 엔티티 속성에 접근하면 DetachedInstanceError가 발생한다. 반환 타입 예: `def get_theater(id: str) -> TheaterRead`
  - 헬퍼 함수 패턴: 세션 컨텍스트 내에서 `_entity_to_dict()` 형태의 헬퍼로 엔티티를 딕셔너리로 변환 후 스키마 객체 생성. 예: `TheaterRead(**_theater_to_dict(theater))`
- 시드/마이그레이션 단일 진입점:
  - 공개 진입점은 `db/seed.py`의 `seed_database_if_empty()` 하나만 사용한다.
  - 내부 헬퍼는 현재 DB 존재 여부를 반환하는 `_presence()`를 사용하며, 내부에서 자체 세션을 연다.
  - 과거 명칭/대안 구현(`seed_initial_data_when_empty`, 세션 인자 요구 버전 등)은 사용/동시 존재 금지.
- 모델 단일 정의:
  - `entity/models.py`에는 `Theater`, `Movie`를 각각 한 번만 선언한다.
  - 동일 파일 내에 대안 구현 블록(예: 인덱스 유무/필드 옵션만 다른 버전) 동시 존재 금지. 중복 시 SQLAlchemy가 `Table ... already defined` 오류를 발생시킨다.
- 라우터 단일 정의:
  - `route/theaters.py`, `route/movies.py`는 하나의 구현 세트만 유지한다. 동일 엔드포인트의 복수 블록(예: 세션 주입 버전과 비주입 버전) 동시 존재 금지.
  - 라우터는 서비스에서 반환된 스키마 객체를 그대로 반환한다. 서비스가 이미 스키마 객체를 반환하므로 라우터에서 추가 변환 불필요.
- 앱 팩토리/스타트업:
  - `app.create_app()`의 startup 훅에서 반드시 `init_db()` → `seed_database_if_empty()` 순서로 호출한다.
  - 포트는 8000 고정, `HOST`, `RELOAD`, `DATABASE_URL`만 환경변수로 사용.
- 코드 리뷰 체크리스트(요지):
  - 동일 파일 내 중복 블록(클래스/함수/라우터) 존재 여부
  - 라우터에서 `get_session` 사용 여부
  - 시드 진입점이 `seed_database_if_empty()`인지 확인
  - 모델이 단일 선언인지 확인
  - 빈 DB 판단이 '존재 여부(first/limit)' 검사인지 확인(ScalarResult.count() 사용 금지)
  - 서비스 함수가 스키마 객체(TheaterRead/MovieRead)를 반환하는지 확인 (DetachedInstanceError 방지)
  - 서비스에서 세션 종료 전에 엔티티를 딕셔너리로 변환하고 있는지 확인
 - ORM 단일 컬럼 조회 처리:
   - `session.exec(select(Model.id))` 결과는 스칼라 시퀀스로 간주한다. 안전 패턴:  
     `result = session.exec(select(Model.id))` → `ids = set(result.all())`
   - 튜플 언팩(`for (id,) in ...`) 금지. `.scalars()` 호출은 본 코드베이스에서 사용하지 않는다.
 - Pydantic v2 직렬화 규약:
   - 서비스 계층에서 입력/수정 DTO를 모델에 적용할 때 `.model_dump()` 사용.  
     예) 생성: `Model(**dto.model_dump())`, 수정: `dto.model_dump(exclude_unset=True)`
 - 의존성 버전 정책:
   - SQLModel(>=0.0.21), SQLAlchemy 2.x, Pydantic v2, FastAPI 0.110+ 조합을 기준으로 한다. 다른 조합 사용 시 위 규약을 유지해야 한다.


## 14. Python libe dependency 
Python 패키지 관리자는 UV 를 사용해서 관리한다.