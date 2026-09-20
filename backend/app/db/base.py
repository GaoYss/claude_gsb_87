"""ORM 基类与公共字段。"""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def now_local() -> datetime:
    """统一取服务器本地时间（不带时区）。

    本系统面向单一时区的水利管理单位部署，巡查日期、单据编号、逾期判断都以
    本地时间为准，因此时间统一按本地时间存储，避免 0 点到 8 点之间出现「编号
    日期与操作日期不一致」。需要跨时区部署时，把这里换成 UTC 即可。
    """
    return datetime.now()


class Base(DeclarativeBase):
    """所有模型的基类。"""


class TimestampMixin:
    """创建 / 更新时间。"""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_local, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=now_local, onupdate=now_local, nullable=False
    )
