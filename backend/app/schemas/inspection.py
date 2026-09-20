"""巡查记录 Schema。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import InspectionStatus, InspectionType, ItemResult, StructurePart, Weather
from app.schemas.reservoir import ReservoirBrief


class InspectionItemInput(BaseModel):
    """巡查项录入。"""

    part: StructurePart = Field(description="检查部位")
    result: ItemResult = Field(default=ItemResult.NORMAL, description="检查结果")
    description: str | None = Field(default=None, description="异常描述")


class InspectionItemRead(InspectionItemInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


class InspectionCreate(BaseModel):
    reservoir_id: int
    inspect_type: InspectionType = Field(default=InspectionType.DAILY, description="巡查类型")
    inspected_at: datetime | None = Field(default=None, description="巡查时间，缺省为当前时间")
    inspector: str = Field(min_length=1, max_length=64, description="巡查人")
    weather: Weather | None = Field(default=None, description="天气")
    water_level: float | None = Field(default=None, ge=0, description="巡查时水位（m）")
    rainfall: float | None = Field(default=None, ge=0, description="降雨量（mm）")
    route: str | None = Field(default=None, max_length=255, description="巡查路线")
    summary: str | None = Field(default=None, description="巡查情况小结")
    remark: str | None = Field(default=None, description="备注")
    items: list[InspectionItemInput] = Field(default_factory=list, description="巡查项明细")


class InspectionUpdate(BaseModel):
    inspect_type: InspectionType | None = None
    inspected_at: datetime | None = None
    inspector: str | None = Field(default=None, min_length=1, max_length=64)
    weather: Weather | None = None
    water_level: float | None = Field(default=None, ge=0)
    rainfall: float | None = Field(default=None, ge=0)
    route: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    remark: str | None = None
    items: list[InspectionItemInput] | None = Field(
        default=None, description="传入则整体替换巡查项"
    )


class InspectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    reservoir_id: int
    inspect_type: InspectionType
    inspected_at: datetime
    inspector: str
    weather: Weather | None = None
    water_level: float | None = None
    rainfall: float | None = None
    route: str | None = None
    status: InspectionStatus
    summary: str | None = None
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    reservoir: ReservoirBrief | None = None
    items: list[InspectionItemRead] = Field(default_factory=list)


class InspectionBrief(BaseModel):
    """总览页 / 关联列表使用的精简巡查信息。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    inspected_at: datetime
    inspector: str
    inspect_type: InspectionType
    status: InspectionStatus
    reservoir_name: str = ""

