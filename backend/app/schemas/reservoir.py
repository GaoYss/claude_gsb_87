"""水库台账 Schema。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DamType, ReservoirStatus, SafetyClass


class ReservoirBrief(BaseModel):
    """列表/关联处使用的水库摘要。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    region: str
    status: ReservoirStatus


class ReservoirBase(BaseModel):
    name: str = Field(min_length=1, max_length=128, description="水库名称")
    region: str = Field(min_length=1, max_length=64, description="所在行政区")
    basin: str | None = Field(default=None, max_length=64, description="所属流域")
    dam_type: DamType | None = Field(default=None, description="坝型")
    safety_class: SafetyClass = Field(default=SafetyClass.CLASS_TWO, description="大坝安全类别")
    status: ReservoirStatus = Field(default=ReservoirStatus.NORMAL, description="运行状态")
    total_capacity: float | None = Field(default=None, ge=0, description="总库容（万 m³）")
    normal_level: float | None = Field(default=None, ge=0, description="正常蓄水位（m）")
    flood_limit_level: float | None = Field(default=None, ge=0, description="汛限水位（m）")
    dam_height: float | None = Field(default=None, ge=0, description="最大坝高（m）")
    dam_length: float | None = Field(default=None, ge=0, description="坝顶长度（m）")
    build_year: int | None = Field(default=None, ge=1900, le=2100, description="建成年份")
    manager: str | None = Field(default=None, max_length=128, description="管理单位")
    manager_phone: str | None = Field(default=None, max_length=32, description="责任人电话")
    location: str | None = Field(default=None, max_length=255, description="坝址位置")
    remark: str | None = Field(default=None, description="备注")


class ReservoirCreate(ReservoirBase):
    code: str = Field(
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{1,31}$",
        description="水库编码，全局唯一",
        examples=["SK-3301001"],
    )


class ReservoirUpdate(BaseModel):
    """局部更新，仅提交需要修改的字段。"""

    name: str | None = Field(default=None, min_length=1, max_length=128)
    region: str | None = Field(default=None, min_length=1, max_length=64)
    basin: str | None = Field(default=None, max_length=64)
    dam_type: DamType | None = None
    safety_class: SafetyClass | None = None
    status: ReservoirStatus | None = None
    total_capacity: float | None = Field(default=None, ge=0)
    normal_level: float | None = Field(default=None, ge=0)
    flood_limit_level: float | None = Field(default=None, ge=0)
    dam_height: float | None = Field(default=None, ge=0)
    dam_length: float | None = Field(default=None, ge=0)
    build_year: int | None = Field(default=None, ge=1900, le=2100)
    manager: str | None = Field(default=None, max_length=128)
    manager_phone: str | None = Field(default=None, max_length=32)
    location: str | None = Field(default=None, max_length=255)
    remark: str | None = None


class ReservoirRead(ReservoirBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    created_at: datetime
    updated_at: datetime


class ReservoirListItem(ReservoirRead):
    """列表页附带巡查/隐患统计，避免前端二次请求。"""

    inspection_count: int = 0
    last_inspected_at: datetime | None = None
    open_hazard_count: int = 0


class ReservoirStats(BaseModel):
    """水库详情页的统计卡片。"""

    inspection_total: int = 0
    inspection_last_30_days: int = 0
    last_inspected_at: datetime | None = None
    hazard_total: int = 0
    hazard_open: int = 0
    hazard_overdue: int = 0
    hazard_closed: int = 0

