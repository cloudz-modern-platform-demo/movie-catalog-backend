# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Movie Catalog Backend - FastAPI-based REST API for managing theater and movie information with SQLite persistence.

**Language**: Python 3.12
**Framework**: FastAPI 0.110+
**Database**: SQLite (file-based at `data/movie_catalog.db`)
**Package Manager**: uv

## Development Commands

### Run the application
```bash
uv run movie-catalog-backend
# Server starts on http://localhost:8000 (port is fixed, cannot be changed)
# API docs: http://localhost:8000/docs (Swagger)
# API docs: http://localhost:8000/redoc (ReDoc)
```

### Environment Variables
- `HOST`: Server host (default: `0.0.0.0`)
- `RELOAD`: Enable auto-reload (default: `true`)
- `DATABASE_URL`: SQLite database path (default: `data/movie_catalog.db` relative to project root)
- **Note**: `PORT` environment variable is ignored; port is fixed at 8000

### Alternative run method
```bash
python -m movie_catalog_backend
```

## Architecture

### Layered Architecture Pattern
The codebase follows strict layer separation: `route` → `service` → `db` → `entity`/`scheme`

```
src/movie_catalog_backend/
  entity/
    models.py            # SQLModel tables: Theater, Movie (FK-based)
  scheme/
    theater.py           # TheaterCreate/TheaterUpdate/TheaterRead (Pydantic)
    movie.py             # MovieCreate/MovieUpdate/MovieRead (Pydantic)
  db/
    config.py            # Project root detection, DATABASE_URL resolution
    session.py           # SQLModel engine/session, init_db()
    seed.py              # One-time JSON→DB migration/seeding logic
  service/
    theater_service.py   # Theater CRUD + deletion constraints
    movie_service.py     # Movie CRUD + theater_id validation
  route/
    theaters.py          # /theaters router
    movies.py            # /movies router
  app.py                 # FastAPI factory: create_app() + startup hooks
  __init__.py            # main() entry point using uvicorn factory mode
```

### Key Design Principles
- **ORM relationships are simplified**: Use FK only, handle joins in service queries
- **Routes handle I/O boundary only**: Business rules in service layer
- **DB layer encapsulates environment dependencies**: Reusable across layers
- **Schemes separate input/output contracts**: API stability and validation

### Application Lifecycle
1. `create_app()` factory creates FastAPI instance
2. Startup hook calls `init_db()` to create tables
3. Startup hook calls `seed_database_if_empty()` for one-time data initialization
4. Uvicorn runs on port 8000 (fixed)

## Database Schema

### Theater
- `id: str` (UUID4, PK)
- `name: str` (NOT NULL)
- `brand: str` (NOT NULL)
- `location: str` (NOT NULL)
- `operating_hours: str` (e.g., "09:00-23:00", NOT NULL)

### Movie
- `id: str` (UUID4, PK)
- `title: str` (NOT NULL)
- `distributor: str` (NOT NULL)
- `ticket_price: int` (integer ≥0, NOT NULL) - **Must be integer, no decimals**
- `runtime_minutes: int` (integer ≥0, NOT NULL)
- `genre: str` (NOT NULL)
- `theater_id: str` (FK → Theater.id, NOT NULL, ON DELETE RESTRICT)

**Important**: Same movie title can exist for multiple theaters with different prices per theater.

## Data Initialization Strategy

### Automatic Seeding on Startup
When DB is empty, the app automatically seeds data **once** on startup:

1. **Priority 1**: Load from `data/theaters.json` and `data/movies.json` (project root)
2. **Priority 2**: If JSON missing/invalid, use embedded sample data

### JSON Format Requirements
- **Top-level must be array**
- **Theaters**: `{ id?(UUID4), name, brand, location, operating_hours }`
- **Movies**: `{ id?(UUID4), title, distributor, ticket_price(int≥0), runtime_minutes(int≥0), genre, theater_id(required) }`
- If `id` is missing, server auto-generates UUID4

### Validation & Error Handling
- **Structural errors** (JSON parse failure, wrong top-level type): Fail entire migration, fallback to embedded data
- **Record-level errors**: Skip invalid record, continue processing (commit if ≥1 record succeeds)
- **Invalid `theater_id` references**: Skip that movie record, log warning
- **Partial backfill**: If theaters exist but movies are empty, restart will auto-backfill movies only

### Recovery
- To reset DB: Delete `data/movie_catalog.db` and restart (auto-recreates and seeds)
- To backfill movies only: Restart app (no need to delete DB if theaters exist)

## Critical Implementation Rules

### Session Management
- **Services own sessions**: Use `session_scope()` context manager
- **NO dependency injection in routes**: Do NOT use `Depends(get_session)` in routers
- **DO NOT import `get_session`** from `movie_catalog_backend.db.session` in routes
- **DetachedInstanceError prevention**: Service functions MUST convert SQLModel entities to schema objects (TheaterRead/MovieRead) **before session closes**
- **Helper pattern**: Use `_entity_to_dict()` within session context, then create schema object: `TheaterRead(**_theater_to_dict(theater))`

### Model & Router Definitions
- **Single definition only**: Each model (Theater, Movie) declared exactly once in `entity/models.py`
- **No duplicate blocks**: Do NOT maintain alternative implementations (e.g., different index options) in same file
- **Router uniqueness**: Each route file (`theaters.py`, `movies.py`) has single implementation set only

### Seeding Entry Point
- **Single public entry**: Only use `seed_database_if_empty()` from `db/seed.py`
- **Internal helpers**: Use `_presence()` for DB existence checks (opens own session)
- **Forbidden**: Do NOT use alternative names like `seed_initial_data_when_empty` or session-argument versions

### ORM Query Patterns
- **Single-column selects**: Treat as scalar sequence. Safe pattern:
  ```python
  result = session.exec(select(Model.id))
  ids = set(result.all())
  ```
- **NO tuple unpacking**: Forbidden: `for (id,) in ...`
- **NO .scalars() calls**: Not used in this codebase (SQLModel/SQLAlchemy compatibility)

### Pydantic v2 Serialization
- **Use `.model_dump()`** for DTO serialization (NOT `.model_dict()`)
- **Create**: `Model(**dto.model_dump())`
- **Update**: `dto.model_dump(exclude_unset=True)`

### Empty DB Detection
- Use **existence checks** (first/limit), NOT `.count()`
- SQL: `SELECT 1 FROM theater LIMIT 1`
- ORM: `session.exec(select(Theater.id).limit(1)).first() is None`

### Application Factory & Startup
- Startup hook MUST call in order: `init_db()` → `seed_database_if_empty()`
- Port is 8000 (fixed), environment variables: `HOST`, `RELOAD`, `DATABASE_URL` only

## API Endpoints

### Theaters
- `GET /theaters/` - List all theaters
- `POST /theaters/` - Create theater
- `GET /theaters/{theater_id}` - Get single theater
- `PUT /theaters/{theater_id}` - Update theater (partial)
- `DELETE /theaters/{theater_id}` - Delete theater (409 if has movies)
- `GET /theaters/{theater_id}/movies` - List movies for theater

### Movies
- `GET /movies/` - List all movies (supports `?theater_id=` query filter)
- `POST /movies/` - Create movie (requires valid theater_id)
- `GET /movies/{movie_id}` - Get single movie
- `PUT /movies/{movie_id}` - Update movie (validates theater_id if changed)
- `DELETE /movies/{movie_id}` - Delete movie

## Error Handling Standards

- **404**: Resource not found → `{"detail": "... not found"}`
- **409**: Theater deletion blocked by movies → `{"detail": "..."}`
- **422**: Pydantic validation failure (FastAPI default)
- **204**: Delete success (NO response body per FastAPI constraint)

## SQLite Configuration

- `PRAGMA foreign_keys=ON` (enforced)
- `check_same_thread=False` (required for FastAPI)
- Transactions ensure consistency for concurrent requests

## Dependencies

- SQLModel ≥0.0.21
- SQLAlchemy 2.x
- Pydantic v2
- FastAPI 0.110+
- uvicorn (for ASGI server)

## Code Review Checklist

Before committing, verify:
- [ ] No duplicate blocks (classes/functions/routers) in same file
- [ ] Routes do NOT use `get_session` dependency injection
- [ ] Seed entry point is `seed_database_if_empty()`
- [ ] Models have single declaration only
- [ ] Empty DB checks use existence (first/limit), not count()
- [ ] Service functions return schema objects (TheaterRead/MovieRead), not entities
- [ ] Entities converted to dicts within session context before schema creation
- [ ] No tuple unpacking in ORM single-column queries
- [ ] Pydantic uses `.model_dump()` not `.model_dict()`
