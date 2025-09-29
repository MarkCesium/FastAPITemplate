import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.core.exceptions.database import DatabaseException

logger = logging.getLogger(__name__)


async def database_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик для кастомных ошибок работы с БД"""
    if isinstance(exc, DatabaseException):
        logger.warning(f"Database exception on {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=getattr(exc, "status_code", 500),
            content={
                "detail": str(exc),
                "type": "database_error",
                "path": str(request.url.path),
            },
        )
    # Если ошибка не относится к DatabaseException, пробрасываем дальше
    raise exc


async def sqlalchemy_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Обработчик для необработанных ошибок SQLAlchemy"""
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"Unhandled SQLAlchemy error on {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal database error occurred",
                "type": "internal_error",
                "path": str(request.url.path),
            },
        )
    raise exc


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Глобальный обработчик для всех необработанных исключений"""
    logger.error(f"Unhandled exception on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error",
            "path": str(request.url.path),
        },
    )
