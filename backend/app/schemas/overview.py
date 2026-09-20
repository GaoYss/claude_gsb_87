"""总览页 Schema。"""

from pydantic import BaseModel, Field

from app.schemas.common import NamedCount
from app.schemas.hazard import HazardRead
from app.schemas.inspection import InspectionBrief


class OverviewSummary(BaseModel):
    """首页统计 + 待办提醒。"""

    reservoir_total: int = 0
    reservoir_attention: int = Field(default=0, description="需关注 / 存在险情的水库数")
    reservoir_by_status: list[NamedCount] = Field(default_factory=list)

    inspection_total: int = 0
    inspection_last_30_days: int = 0
    inspection_by_type: list[NamedCount] = Field(default_factory=list)

    hazard_total: int = 0
    hazard_open: int = Field(default=0, description="未销号隐患数")
    hazard_overdue: int = Field(default=0, description="逾期未整改隐患数")
    hazard_by_status: list[NamedCount] = Field(default_factory=list)
    hazard_by_severity: list[NamedCount] = Field(default_factory=list)

    recent_inspections: list[InspectionBrief] = Field(default_factory=list)
    urgent_hazards: list[HazardRead] = Field(default_factory=list)

