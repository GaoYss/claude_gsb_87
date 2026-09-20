"""字典与系统信息 Schema。"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.hazard import HazardTransitionOption


class DictOption(BaseModel):
    """下拉选项。"""

    value: str
    label: str


class MetaOptions(BaseModel):
    """前端下拉字典集合。

    dicts 的 key 与后端枚举一一对应：reservoir_status / safety_class / dam_type /
    structure_part / inspection_type / weather / inspection_status / item_result /
    hazard_severity / hazard_source / hazard_status / rectification_action。
    """

    dicts: dict[str, list[DictOption]]
    regions: list[str] = Field(default_factory=list, description="已有水库的行政区，用于筛选")
    hazard_transitions: dict[str, list[HazardTransitionOption]] = Field(
        default_factory=dict, description="隐患状态机：当前状态 -> 可执行的流转"
    )


class HealthStatus(BaseModel):
    """健康检查。"""

    status: str = "ok"
    app: str
    version: str
    database: str = "ok"
    time: datetime

