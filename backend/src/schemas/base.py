from pydantic import BaseModel


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
