from typing import Union
from uuid import UUID

from fastapi import HTTPException


class DatabaseException(HTTPException):
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)


class EntityNotFoundException(DatabaseException):
    def __init__(self, entity_name: str, entity_id: Union[int, str, UUID]):
        detail = f"{entity_name} with id {entity_id} not found"
        super().__init__(detail=detail, status_code=404)


class ValidationException(DatabaseException):
    def __init__(self, detail: str):
        super().__init__(detail=detail)


class DatabaseOperationException(DatabaseException):
    def __init__(self, operation: str, detail: str = "Database operation failed"):
        detail = f"Failed to {operation}: {detail}"
        super().__init__(detail=detail)
