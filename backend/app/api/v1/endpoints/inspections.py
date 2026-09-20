"""巡查记录接口。"""

from datetime import datetime

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession, PageParams
from app.models.enums import InspectionStatus, InspectionType
from app.schemas.common import Message, Page
from app.schemas.inspection import (
    InspectionCreate,
    InspectionRead,
    InspectionUpdate,
)
from app.services import inspection_service

router = APIRouter(prefix="/inspections", tags=["巡查记录"])


@router.get("", response_model=Page[InspectionRead], summary="分页查询巡查记录")
def list_inspections(
    db: DbSession,
    pagination: PageParams,
    reservoir_id: int | None = Query(default=None, description="按水库过滤"),
    inspect_type: InspectionType | None = Query(default=None, description="巡查类型"),
    inspection_status: InspectionStatus | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None, description="按编号 / 巡查人 / 路线 / 小结搜索"),
    date_from: datetime | None = Query(default=None, description="巡查时间起（含）"),
    date_to: datetime | None = Query(default=None, description="巡查时间止（含）"),
) -> Page[InspectionRead]:
    items, total = inspection_service.list_inspections(
        db,
        reservoir_id=reservoir_id,
        inspect_type=inspect_type.value if inspect_type else None,
        status=inspection_status.value if inspection_status else None,
        keyword=keyword,
        date_from=date_from,
        date_to=date_to,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return Page.build(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.post(
    "",
    response_model=InspectionRead,
    status_code=status.HTTP_201_CREATED,
    summary="新增巡查记录",
)
def create_inspection(payload: InspectionCreate, db: DbSession) -> InspectionRead:
    return inspection_service.create_inspection(db, payload)


@router.get("/{inspection_id}", response_model=InspectionRead, summary="巡查记录详情")
def get_inspection(inspection_id: int, db: DbSession) -> InspectionRead:
    return inspection_service.get_inspection(db, inspection_id)


@router.put("/{inspection_id}", response_model=InspectionRead, summary="更新巡查记录")
def update_inspection(
    inspection_id: int, payload: InspectionUpdate, db: DbSession
) -> InspectionRead:
    return inspection_service.update_inspection(db, inspection_id, payload)


@router.delete("/{inspection_id}", response_model=Message, summary="删除巡查记录")
def delete_inspection(inspection_id: int, db: DbSession) -> Message:
    inspection_service.delete_inspection(db, inspection_id)
    return Message(detail="巡查记录已删除", code="deleted")

