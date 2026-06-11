from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None
