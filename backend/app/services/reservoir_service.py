"""水库台账业务逻辑。"""

from datetime import date, timedelta

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, InvalidOperationError, NotFoundError
from app.db.base import now_local
from app.models import Hazard, Inspection, Reservoir
from app.models.enums import HazardStatus
from app.schemas.reservoir import (
    ReservoirCreate,
    ReservoirListItem,
    ReservoirRead,
    ReservoirStats,
    ReservoirUpdate,
)
from app.services.helpers import enum_to_value

def get_reservoir(db: Session, reservoir_id: int) -> Reservoir:
    reservoir = db.get(Reservoir, reservoir_id)
    if reservoir is None:
        raise NotFoundError(f"水库不存在：id={reservoir_id}")
    return reservoir


def _code_exists(db: Session, code: str) -> bool:
    stmt = select(func.count()).select_from(Reservoir).where(
        func.lower(Reservoir.code) == code.lower()
    )
    return bool(db.scalar(stmt))


def list_reservoirs(
    db: Session,
    *,
    keyword: str | None = None,
    region: str | None = None,
    status: str | None = None,
    safety_class: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ReservoirListItem], int]:
    """按条件分页查询水库，附带巡查次数 / 最近巡查时间 / 未销号隐患数。"""
    conditions = []
    if keyword:
        like = f"%{keyword.strip()}%"
        conditions.append(
            or_(
                Reservoir.name.like(like),
                Reservoir.code.like(like),
                Reservoir.location.like(like),
                Reservoir.manager.like(like),
            )
        )
    if region:
        conditions.append(Reservoir.region == region)
    if status:
        conditions.append(Reservoir.status == status)
    if safety_class:
        conditions.append(Reservoir.safety_class == safety_class)

    total = db.scalar(select(func.count()).select_from(Reservoir).where(*conditions)) or 0

    inspection_agg = (
        select(
            Inspection.reservoir_id.label("reservoir_id"),
            func.count(Inspection.id).label("inspection_count"),
            func.max(Inspection.inspected_at).label("last_inspected_at"),
        )
        .group_by(Inspection.reservoir_id)
        .subquery()
    )
    hazard_agg = (
        select(
            Hazard.reservoir_id.label("reservoir_id"),
            func.count(Hazard.id).label("open_hazard_count"),
        )
        .where(Hazard.status != HazardStatus.CLOSED.value)
        .group_by(Hazard.reservoir_id)
        .subquery()
    )

    stmt = (
        select(
            Reservoir,
            inspection_agg.c.inspection_count,
            inspection_agg.c.last_inspected_at,
            hazard_agg.c.open_hazard_count,
        )
        .outerjoin(inspection_agg, inspection_agg.c.reservoir_id == Reservoir.id)
        .outerjoin(hazard_agg, hazard_agg.c.reservoir_id == Reservoir.id)
        .where(*conditions)
        .order_by(Reservoir.code)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    items = [
        ReservoirListItem(
            **ReservoirRead.model_validate(row[0]).model_dump(),
            inspection_count=row[1] or 0,
            last_inspected_at=row[2],
            open_hazard_count=row[3] or 0,
        )
        for row in db.execute(stmt).all()
    ]
    return items, total


def list_regions(db: Session) -> list[str]:
    """行政区下拉选项。"""
    stmt = select(Reservoir.region).distinct().order_by(Reservoir.region)
    return [region for region in db.scalars(stmt).all() if region]


def create_reservoir(db: Session, payload: ReservoirCreate) -> Reservoir:
    data = enum_to_value(payload.model_dump())
    code = str(data.pop("code")).strip()
    if _code_exists(db, code):
        raise ConflictError(f"水库编码已存在：{code}")

    reservoir = Reservoir(code=code, **data)
    db.add(reservoir)
    db.commit()
    db.refresh(reservoir)
    return reservoir


def update_reservoir(db: Session, reservoir_id: int, payload: ReservoirUpdate) -> Reservoir:
    reservoir = get_reservoir(db, reservoir_id)
    data = enum_to_value(payload.model_dump(exclude_unset=True))
    for key, value in data.items():
        setattr(reservoir, key, value)
    db.commit()
    db.refresh(reservoir)
    return reservoir


def delete_reservoir(db: Session, reservoir_id: int) -> None:
    """有历史记录的水库不允许直接删除，避免误删台账。"""
    reservoir = get_reservoir(db, reservoir_id)
    inspection_count = (
        db.scalar(
            select(func.count()).select_from(Inspection).where(
                Inspection.reservoir_id == reservoir_id
            )
        )
        or 0
    )
    hazard_count = (
        db.scalar(
            select(func.count()).select_from(Hazard).where(Hazard.reservoir_id == reservoir_id)
        )
        or 0
    )
    if inspection_count or hazard_count:
        raise InvalidOperationError(
            f"该水库已有 {inspection_count} 条巡查记录、{hazard_count} 条隐患记录，"
            "请先清理关联数据后再删除"
        )

    db.delete(reservoir)
    db.commit()


def reservoir_stats(db: Session, reservoir_id: int) -> ReservoirStats:
    """详情页统计。"""
    get_reservoir(db, reservoir_id)
    since = now_local() - timedelta(days=30)

    inspection_row = db.execute(
        select(
            func.count(Inspection.id),
            func.max(Inspection.inspected_at),
            func.sum(case((Inspection.inspected_at >= since, 1), else_=0)),
        ).where(Inspection.reservoir_id == reservoir_id)
    ).one()

    hazard_row = db.execute(
        select(
            func.count(Hazard.id),
            func.sum(case((Hazard.status != HazardStatus.CLOSED.value, 1), else_=0)),
            func.sum(
                case(
                    (
                        and_(
                            Hazard.status != HazardStatus.CLOSED.value,
                            Hazard.deadline.is_not(None),
                            Hazard.deadline < date.today(),
                        ),
                        1,
                    ),
                    else_=0,
                )
            ),
            func.sum(case((Hazard.status == HazardStatus.CLOSED.value, 1), else_=0)),
        ).where(Hazard.reservoir_id == reservoir_id)
    ).one()

    return ReservoirStats(
        inspection_total=inspection_row[0] or 0,
        last_inspected_at=inspection_row[1],
        inspection_last_30_days=inspection_row[2] or 0,
        hazard_total=hazard_row[0] or 0,
        hazard_open=hazard_row[1] or 0,
        hazard_overdue=hazard_row[2] or 0,
        hazard_closed=hazard_row[3] or 0,
    )
