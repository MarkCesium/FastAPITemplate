# FastAPITemplate

A production-ready FastAPI template for quick project setup with best practices and a clean architecture.

## Features

### Core Architecture
- **Repository Pattern** - Generic base repository with full CRUD operations, pagination, filtering, and querying
- **Unit of Work Pattern** - Transaction management with automatic commit/rollback
- **Service Layer** - Abstract base service interface for business logic
- **Exception Handling** - Centralized exception handlers for database, SQLAlchemy, and general errors
- **DTO Support** - Data Transfer Object pattern for structured data validation

### Database & ORM
- **PostgreSQL** - Production-ready PostgreSQL database support
- **SQLAlchemy 2.0** - Modern async ORM with type hints
- **Alembic Migrations** - Asynchronous database migrations with auto-formatting hooks
- **Connection Pooling** - Configurable connection pool with health checks
- **Transaction Management** - Async session management with scoped sessions

### Infrastructure
- **Redis Integration** - Async Redis client for caching and session management
- **HTTP Client** - Async HTTP client factory using aiohttp for external API calls
- **Database Helper** - Centralized database connection and session management

### API Features
- **FastAPI Framework** - Modern async Python web framework
- **ORJSON Responses** - High-performance JSON serialization
- **Type-Safe** - Full type hints with strict MyPy configuration

### Configuration
- **Pydantic Settings** - Type-safe configuration management
- **Nested Configuration** - Organized settings structure (app, logging, database, redis)
- **Environment Variables** - Support for `.env` files with nested delimiter syntax
- **Flexible Logging** - Configurable logging levels and formats

### Development & Deployment
- **Poetry** - Modern dependency management
- **Docker** - Production-ready Dockerfile with optimized layer caching
- **Code Quality** - Ruff linter and formatter with auto-fix
- **Type Checking** - Strict MyPy configuration for maximum type safety
- **Python 3.13** - Latest Python version support

### Template Structure
- Clean separation of concerns (API, Core, Infrastructure)
- Scalable project structure
- Ready for microservices architecture
- Railway deployment ready

## TODO's
- [x] Migrate from poetry to uv
- [ ] Implement app fabric pattern
- [ ] Add infrastrucutre tests
- [ ] Improve error handling