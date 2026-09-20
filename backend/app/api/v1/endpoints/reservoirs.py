"""水库台账接口。"""

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession, PageParams
from app.models.enums import ReservoirStatus, SafetyClass
from app.schemas.common import Message, Page
from app.schemas.reservoir import (
    ReservoirCreate,
    ReservoirListItem,
    ReservoirRead,
    ReservoirStats,
    ReservoirUpdate,
)
from app.services import reservoir_service

router = APIRouter(prefix="/reservoirs", tags=["水库台账"])


@router.get("", response_model=Page[ReservoirListItem], summary="分页查询水库台账")
def list_reservoirs(
    db: DbSession,
    pagination: PageParams,
    keyword: str | None = Query(default=None, description="按名称 / 编码 / 位置 / 管理单位模糊搜索"),
    region: str | None = Query(default=None, description="所在行政区"),
    reservoir_status: ReservoirStatus | None = Query(default=None, alias="status", description="运行状态"),
    safety_class: SafetyClass | None = Query(default=None, description="大坝安全类别"),
) -> Page[ReservoirListItem]:
    items, total = reservoir_service.list_reservoirs(
        db,
        keyword=keyword,
        region=region,
        status=reservoir_status.value if reservoir_status else None,
        safety_class=safety_class.value if safety_class else None,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return Page.build(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.post(
    "",
    response_model=ReservoirRead,
    status_code=status.HTTP_201_CREATED,
    summary="新增水库",
    responses={409: {"description": "编码重复"}},
)
def create_reservoir(payload: ReservoirCreate, db: DbSession) -> ReservoirRead:
    return reservoir_service.create_reservoir(db, payload)


@router.get("/{reservoir_id}", response_model=ReservoirRead, summary="水库详情")
def get_reservoir(reservoir_id: int, db: DbSession) -> ReservoirRead:
    return reservoir_service.get_reservoir(db, reservoir_id)


@router.put("/{reservoir_id}", response_model=ReservoirRead, summary="更新水库")
def update_reservoir(reservoir_id: int, payload: ReservoirUpdate, db: DbSession) -> ReservoirRead:
    return reservoir_service.update_reservoir(db, reservoir_id, payload)


@router.get("/{reservoir_id}/stats", response_model=ReservoirStats, summary="水库巡查/隐患统计")
def get_reservoir_stats(reservoir_id: int, db: DbSession) -> ReservoirStats:
    return reservoir_service.reservoir_stats(db, reservoir_id)


@router.delete("/{reservoir_id}", response_model=Message, summary="删除水库（有历史记录时拒绝）")
def delete_reservoir(reservoir_id: int, db: DbSession) -> Message:
    reservoir_service.delete_reservoir(db, reservoir_id)
    return Message(detail="水库已删除", code="deleted")
