"""通用 Schema 与公共小工具。"""

import math
from datetime import date
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


def is_overdue(deadline: date | None, status: str, closed_status: str = "closed") -> bool:
    """整改期限已过且未销号，视为逾期。"""
    if deadline is None or status == closed_status:
        return False
    return deadline < date.today()


class Page(BaseModel, Generic[T]):
    """分页响应。"""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def build(cls, items: list[T], total: int, page: int, page_size: int) -> "Page[T]":
        pages = math.ceil(total / page_size) if total else 0
        return cls(items=items, total=total, page=page, page_size=page_size, pages=pages)


class Message(BaseModel):
    """简单操作结果。"""

    detail: str
    code: str = "ok"


class NamedCount(BaseModel):
    """统计分布中的一项。"""

    value: str
    label: str
    count: int
