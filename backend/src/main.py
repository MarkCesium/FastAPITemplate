import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.api import router
from src.api.exception_handlers import register_exception_handlers
from src.api.utils import generate_openapi_file
from src.core.config import settings
from src.dependencies import ConfigProvider, DBProvider

container = make_async_container(
    ConfigProvider(),
    DBProvider(),
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logging.basicConfig(
        level=settings.logging.level_value,
        format=settings.logging.format,
        datefmt=settings.logging.date_format,
    )
    generate_openapi_file(app)

    try:
        yield
    finally:
        await container.close()


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    debug=settings.app.debug,
    docs_url="/docs" if settings.app.debug else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.app.debug else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(router)
setup_dishka(container=container, app=app)
