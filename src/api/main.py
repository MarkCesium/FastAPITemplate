import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.api import api_router
from src.api.exception_handlers import (
    database_exception_handler,
    general_exception_handler,
    sqlalchemy_exception_handler,
)
from src.core.config import BASE_DIR, settings
from src.core.db import db_helper
from src.core.exceptions.database import DatabaseException


def generate_openapi_file(app: FastAPI) -> None:
    if not settings.app.generate_openapi_file:
        return

    try:
        output_path = BASE_DIR / settings.app.openapi_file_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(app.openapi(), f, indent=2)

        print(f"OpenAPI JSON generated at {output_path}")
    except Exception as e:
        print(f"Failed to generate OpenAPI file: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, FastAPI]:
    import logging

    from src.core.config import settings

    logging.basicConfig(
        level=settings.logging.level_value,
        format=settings.logging.format,
        datefmt=settings.logging.date_format,
    )
    generate_openapi_file(app)
    yield

    await db_helper.dispose()


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    docs_url="/docs" if settings.app.debug else None,
    redoc_url="/redoc" if settings.app.debug else None,
    openapi_url="/openapi.json" if settings.app.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
