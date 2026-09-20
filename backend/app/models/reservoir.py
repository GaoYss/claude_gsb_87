"""水库台账模型。"""

from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import ReservoirStatus, SafetyClass

if TYPE_CHECKING:
    from app.models.hazard import Hazard
    from app.models.inspection import Inspection


class Reservoir(TimestampMixin, Base):
    """水库基本信息。"""

    __tablename__ = "reservoir"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="水库编码")
    name: Mapped[str] = mapped_column(String(128), index=True, comment="水库名称")
    region: Mapped[str] = mapped_column(String(64), index=True, comment="所在行政区")
    basin: Mapped[str | None] = mapped_column(String(64), comment="所属流域")
    dam_type: Mapped[str | None] = mapped_column(String(32), comment="坝型")
    safety_class: Mapped[str] = mapped_column(
        String(16), default=SafetyClass.CLASS_TWO.value, comment="大坝安全类别"
    )
    status: Mapped[str] = mapped_column(
        String(24), default=ReservoirStatus.NORMAL.value, index=True, comment="运行状态"
    )
    total_capacity: Mapped[float | None] = mapped_column(Float, comment="总库容（万立方米）")
    normal_level: Mapped[float | None] = mapped_column(Float, comment="正常蓄水位（米）")
    flood_limit_level: Mapped[float | None] = mapped_column(Float, comment="汛限水位（米）")
    dam_height: Mapped[float | None] = mapped_column(Float, comment="最大坝高（米）")
    dam_length: Mapped[float | None] = mapped_column(Float, comment="坝顶长度（米）")
    build_year: Mapped[int | None] = mapped_column(Integer, comment="建成年份")
    manager: Mapped[str | None] = mapped_column(String(128), comment="管理单位")
    manager_phone: Mapped[str | None] = mapped_column(String(32), comment="责任人电话")
    location: Mapped[str | None] = mapped_column(String(255), comment="坝址位置")
    remark: Mapped[str | None] = mapped_column(Text, comment="备注")

    inspections: Mapped[list["Inspection"]] = relationship(
        back_populates="reservoir",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    hazards: Mapped[list["Hazard"]] = relationship(
        back_populates="reservoir",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - 调试用
        return f"<Reservoir {self.code} {self.name}>"

