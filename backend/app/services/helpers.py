"""服务层小工具。"""

from datetime import date
from enum import Enum
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import now_local


def enum_to_value(data: dict[str, Any]) -> dict[str, Any]:
    """把 Enum 值转成字符串，方便直接落库。"""
    return {key: (value.value if isinstance(value, Enum) else value) for key, value in data.items()}


def next_code(
    db: Session,
    model: type,
    column: Any,
    prefix: str,
    *,
    on: date | None = None,
    width: int = 3,
) -> str:
    """生成「前缀 + 日期 + 流水号」单据编号，例如 YH20260914001。"""
    day = (on or now_local().date()).strftime("%Y%m%d")
    base = f"{prefix}{day}"
    serial = db.scalar(select(func.count()).select_from(model).where(column.like(f"{base}%"))) or 0
    while True:
        serial += 1
        code = f"{base}{serial:0{width}d}"
        exists = db.scalar(select(func.count()).select_from(model).where(column == code))
        if not exists:
            return code
