"""巡查记录模型：一次巡查一张主表 + 若干巡查项明细。"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, now_local
from app.models.enums import InspectionStatus, ItemResult

if TYPE_CHECKING:
    from app.models.hazard import Hazard
    from app.models.reservoir import Reservoir


class Inspection(TimestampMixin, Base):
    """巡查记录主表。"""

    __tablename__ = "inspection"
    __table_args__ = (Index("ix_inspection_reservoir_date", "reservoir_id", "inspected_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="巡查编号")
    reservoir_id: Mapped[int] = mapped_column(
        ForeignKey("reservoir.id", ondelete="CASCADE"), index=True
    )
    inspect_type: Mapped[str] = mapped_column(String(24), default="daily", comment="巡查类型")
    inspected_at: Mapped[datetime] = mapped_column(
        DateTime, default=now_local, index=True, comment="巡查时间"
    )
    inspector: Mapped[str] = mapped_column(String(64), comment="巡查人")
    weather: Mapped[str | None] = mapped_column(String(24), comment="天气")
    water_level: Mapped[float | None] = mapped_column(Float, comment="巡查时水位（米）")
    rainfall: Mapped[float | None] = mapped_column(Float, comment="降雨量（毫米）")
    route: Mapped[str | None] = mapped_column(String(255), comment="巡查路线")
    status: Mapped[str] = mapped_column(
        String(16), default=InspectionStatus.NORMAL.value, index=True, comment="巡查结论"
    )
    summary: Mapped[str | None] = mapped_column(Text, comment="巡查情况小结")
    remark: Mapped[str | None] = mapped_column(Text, comment="备注")

    reservoir: Mapped["Reservoir"] = relationship(back_populates="inspections")
    items: Mapped[list["InspectionItem"]] = relationship(
        back_populates="inspection",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="InspectionItem.id",
    )
    hazards: Mapped[list["Hazard"]] = relationship(back_populates="inspection")

    def __repr__(self) -> str:  # pragma: no cover - 调试用
        return f"<Inspection {self.code} reservoir={self.reservoir_id}>"


class InspectionItem(TimestampMixin, Base):
    """巡查项明细（按部位逐项记录）。"""

    __tablename__ = "inspection_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspection.id", ondelete="CASCADE"), index=True
    )
    part: Mapped[str] = mapped_column(String(24), comment="检查部位")
    result: Mapped[str] = mapped_column(
        String(16), default=ItemResult.NORMAL.value, comment="检查结果"
    )
    description: Mapped[str | None] = mapped_column(Text, comment="异常描述 / 处理说明")

    inspection: Mapped["Inspection"] = relationship(back_populates="items")
