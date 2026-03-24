# FastAPITemplate

A production-ready FastAPI template with clean architecture, dishka DI, and modern Python patterns.

## Features

### Core Architecture
- **Dishka DI** — Type-safe dependency injection with APP/REQUEST scopes
- **Repository Pattern** — Generic `BaseRepository[T]` with CRUD, filtering, and counting
- **Unit of Work** — Transaction management with automatic commit/rollback
- **Service Layer** — Dedicated layer for business logic
- **Domain Exceptions** — Clean exception hierarchy decoupled from HTTP

### Database & ORM
- **PostgreSQL** with asyncpg driver
- **SQLAlchemy 2.0** — Async ORM with mapped type hints
- **UUID7 Primary Keys** — Via `IDType` alias and `uuid.uuid7`
- **Alembic** — Async migrations with auto-run in Docker
- **Connection Pooling** — Configurable pool with health checks

### API
- **FastAPI** with `ORJSONResponse` for high-performance JSON
- **Centralized Exception Handlers** — `register_exception_handlers(app)`
- **CORS** — Configurable allowed origins
- **OpenAPI** — Auto-generated JSON schema on startup

### Configuration
- **Pydantic Settings** — Nested config with `__` delimiter (`DATABASE__URL`, `LOGGING__LEVEL`)
- **Strict typing** — mypy strict + ruff with extended rules

### Development & Deployment
- **uv** — Fast dependency management
- **Python 3.14+** — PEP 695 generics (`class Foo[T]: ...`)
- **Docker Compose** — Separate dev/prod configs with PostgreSQL
- **Docker** — Multi-stage build with uv, nonroot user, auto-migrations
- **CI** — GitHub Actions (ruff + mypy on PR)
- **pytest** + **pytest-asyncio** — Test scaffold ready
- **Ruff** — Linter + formatter (line-length 100)
- **mypy** — Strict mode

## Project Structure

```
.
├── docker-compose.yaml              # Base compose (database + backend)
├── docker-compose.dev.yaml          # Dev overrides (ports, volumes, hot-reload)
├── docker-compose.prod.yaml         # Prod overrides (production Dockerfile)
├── Makefile
├── README.md
└── backend/
    ├── Dockerfile                   # Production (nonroot, compiled bytecode)
    ├── Dockerfile.dev               # Development (hot-reload)
    ├── pyproject.toml
    ├── alembic.ini
    ├── migrations/
    ├── tests/                       # Test scaffold
    └── src/
        ├── main.py                  # FastAPI app, lifespan, dishka setup
        ├── api/
        │   ├── __init__.py          # Router aggregation
        │   ├── exception_handlers.py
        │   ├── firewall.py          # Auth/security dependencies
        │   └── utils.py             # generate_openapi_file()
        ├── core/
        │   ├── config.py            # Pydantic Settings
        │   ├── exceptions.py        # AppError, NotFoundError, ValidationError
        │   ├── types.py             # IDType (UUID), UNSET sentinel
        │   └── schemas/
        │       └── base.py          # PaginatedResponse[T]
        ├── dependencies/
        │   ├── config.py            # ConfigProvider (dishka)
        │   └── db.py                # DBProvider (dishka)
        ├── infra/
        │   └── db/
        │       ├── helper.py        # DatabaseHelper (engine + session factory)
        │       ├── uow.py           # UnitOfWork (session_factory)
        │       ├── models/
        │       │   └── base.py      # Base (DeclarativeBase, UUID7 PK)
        │       └── repositories/
        │           └── base.py      # BaseRepository[T: Base]
        └── services/                # Business logic
```

## Quick Start

```bash
# Dev environment with Docker
cp .env.template .env
cp backend/.env.template backend/.env
# fill in DATABASE__URL and POSTGRES_* vars

make dev
```

```bash
# Local development without Docker
cd backend
cp .env.template .env
uv sync
alembic upgrade head
uv run hypercorn src.main:app --bind ::
```

## Makefile

```
make dev         # docker compose up --build (dev, hot-reload)
make prod        # docker compose up --build (prod)
make down        # docker compose down
make logs        # docker compose logs -f
make migrate     # alembic upgrade head
make migration   # alembic revision --autogenerate -m '...'
make format      # ruff check --fix + ruff format
make check       # ruff check + mypy
make test        # pytest tests/ -v
```
