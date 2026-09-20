"""隐患登记与整改跟踪模型。"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, now_local
from app.models.enums import HazardSeverity, HazardStatus

if TYPE_CHECKING:
    from app.models.inspection import Inspection
    from app.models.reservoir import Reservoir


class Hazard(TimestampMixin, Base):
    """隐患（问题）台账。"""

    __tablename__ = "hazard"
    __table_args__ = (
        Index("ix_hazard_reservoir_status", "reservoir_id", "status"),
        Index("ix_hazard_deadline", "deadline"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="隐患编号")
    reservoir_id: Mapped[int] = mapped_column(
        ForeignKey("reservoir.id", ondelete="CASCADE"), index=True
    )
    inspection_id: Mapped[int | None] = mapped_column(
        ForeignKey("inspection.id", ondelete="SET NULL"), index=True, comment="来源巡查记录"
    )
    title: Mapped[str] = mapped_column(String(160), comment="隐患标题")
    category: Mapped[str] = mapped_column(String(24), index=True, comment="隐患类别（部位）")
    severity: Mapped[str] = mapped_column(
        String(16), default=HazardSeverity.GENERAL.value, index=True, comment="隐患等级"
    )
    status: Mapped[str] = mapped_column(
        String(24), default=HazardStatus.REGISTERED.value, index=True, comment="整改状态"
    )
    source: Mapped[str] = mapped_column(String(24), default="inspection", comment="隐患来源")
    discovered_on: Mapped[date] = mapped_column(Date, index=True, comment="发现日期")
    discoverer: Mapped[str | None] = mapped_column(String(64), comment="发现人")
    deadline: Mapped[date | None] = mapped_column(Date, comment="整改期限")
    assignee: Mapped[str | None] = mapped_column(String(64), comment="整改责任人")
    description: Mapped[str | None] = mapped_column(Text, comment="隐患描述")
    plan: Mapped[str | None] = mapped_column(Text, comment="整改方案 / 要求")
    closed_on: Mapped[date | None] = mapped_column(Date, comment="销号日期")

    reservoir: Mapped["Reservoir"] = relationship(back_populates="hazards")
    inspection: Mapped["Inspection | None"] = relationship(back_populates="hazards")
    rectifications: Mapped[list["HazardRectification"]] = relationship(
        back_populates="hazard",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="HazardRectification.recorded_at",
    )

    def __repr__(self) -> str:  # pragma: no cover - 调试用
        return f"<Hazard {self.code} status={self.status}>"


class HazardRectification(TimestampMixin, Base):
    """整改跟踪流水（措施、进展、验收、销号）。"""

    __tablename__ = "hazard_rectification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hazard_id: Mapped[int] = mapped_column(
        ForeignKey("hazard.id", ondelete="CASCADE"), index=True
    )
    action: Mapped[str] = mapped_column(String(24), comment="记录类型")
    content: Mapped[str] = mapped_column(Text, comment="记录内容")
    operator: Mapped[str | None] = mapped_column(String(64), comment="记录人")
    status_from: Mapped[str | None] = mapped_column(String(24), comment="变更前状态")
    status_to: Mapped[str | None] = mapped_column(String(24), comment="变更后状态")
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, default=now_local, index=True, comment="记录时间"
    )

    hazard: Mapped["Hazard"] = relationship(back_populates="rectifications")
