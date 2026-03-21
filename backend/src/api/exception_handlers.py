import logging

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from src.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=404,
            content={"detail": exc.message},
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=400,
            content={"detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception) -> ORJSONResponse:
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return ORJSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
