"""巡查记录业务逻辑。"""

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import InvalidOperationError, NotFoundError
from app.db.base import now_local
from app.models import Hazard, Inspection, InspectionItem, Reservoir
from app.models.enums import InspectionStatus, ItemResult
from app.schemas.inspection import InspectionCreate, InspectionUpdate
from app.services import reservoir_service
from app.services.helpers import enum_to_value, next_code


def _resolve_status(items: list[InspectionItem]) -> str:
    """只要有一个巡查项异常，整条记录结论即为「发现异常」。"""
    if any(item.result == ItemResult.ABNORMAL.value for item in items):
        return InspectionStatus.ABNORMAL.value
    return InspectionStatus.NORMAL.value


def _build_items(items) -> list[InspectionItem]:
    return [InspectionItem(**enum_to_value(item.model_dump())) for item in items]


def get_inspection(db: Session, inspection_id: int) -> Inspection:
    stmt = (
        select(Inspection)
        .options(selectinload(Inspection.items), selectinload(Inspection.reservoir))
        .where(Inspection.id == inspection_id)
    )
    inspection = db.scalar(stmt)
    if inspection is None:
        raise NotFoundError(f"巡查记录不存在：id={inspection_id}")
    return inspection


def list_inspections(
    db: Session,
    *,
    reservoir_id: int | None = None,
    inspect_type: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Inspection], int]:
    conditions = []
    if reservoir_id:
        conditions.append(Inspection.reservoir_id == reservoir_id)
    if inspect_type:
        conditions.append(Inspection.inspect_type == inspect_type)
    if status:
        conditions.append(Inspection.status == status)
    if date_from:
        conditions.append(Inspection.inspected_at >= date_from)
    if date_to:
        conditions.append(Inspection.inspected_at <= date_to)

    stmt = select(Inspection)
    count_stmt = select(func.count()).select_from(Inspection)
    if keyword:
        like = f"%{keyword.strip()}%"
        condition = or_(
            Inspection.code.like(like),
            Inspection.inspector.like(like),
            Inspection.route.like(like),
            Inspection.summary.like(like),
            Inspection.reservoir_id.in_(select(Reservoir.id).where(Reservoir.name.like(like))),
        )
        conditions.append(condition)

    total = db.scalar(count_stmt.where(*conditions)) or 0
    rows = db.scalars(
        stmt.options(selectinload(Inspection.reservoir), selectinload(Inspection.items))
        .where(*conditions)
        .order_by(Inspection.inspected_at.desc(), Inspection.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(rows), total


def create_inspection(db: Session, payload: InspectionCreate) -> Inspection:
    reservoir_service.get_reservoir(db, payload.reservoir_id)
    data = enum_to_value(payload.model_dump(exclude={"items"}))
    if data.get("inspected_at") is None:
        data["inspected_at"] = now_local()

    items = _build_items(payload.items)
    inspection = Inspection(
        code=next_code(db, Inspection, Inspection.code, prefix="XC", on=data["inspected_at"].date()),
        items=items,
        status=_resolve_status(items),
        **data,
    )
    db.add(inspection)
    db.commit()
    return get_inspection(db, inspection.id)


def update_inspection(db: Session, inspection_id: int, payload: InspectionUpdate) -> Inspection:
    inspection = get_inspection(db, inspection_id)
    data = enum_to_value(payload.model_dump(exclude_unset=True, exclude={"items"}))
    for key, value in data.items():
        setattr(inspection, key, value)

    if payload.items is not None:
        inspection.items = _build_items(payload.items)
        inspection.status = _resolve_status(inspection.items)

    db.commit()
    return get_inspection(db, inspection_id)


def delete_inspection(db: Session, inspection_id: int) -> None:
    inspection = get_inspection(db, inspection_id)
    hazard_count = (
        db.scalar(
            select(func.count()).select_from(Hazard).where(Hazard.inspection_id == inspection_id)
        )
        or 0
    )
    if hazard_count:
        raise InvalidOperationError(
            f"该巡查记录已关联 {hazard_count} 条隐患，请先处理隐患台账后再删除"
        )

    db.delete(inspection)
    db.commit()
