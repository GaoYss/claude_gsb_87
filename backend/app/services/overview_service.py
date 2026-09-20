"""总览页统计。"""

from datetime import date, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.base import now_local
from app.models import Hazard, Inspection, Reservoir
from app.models.enums import (
    HazardSeverity,
    HazardStatus,
    InspectionType,
    ReservoirStatus,
)
from app.schemas.common import NamedCount
from app.schemas.hazard import HazardRead
from app.schemas.inspection import InspectionBrief
from app.schemas.overview import OverviewSummary


def _distribution(db: Session, model, column, enum_cls) -> list[NamedCount]:
    """按枚举顺序输出分布统计，没有数据的项补 0。"""
    rows = db.execute(select(column, func.count()).select_from(model).group_by(column)).all()
    counts = {value: count for value, count in rows}
    return [
        NamedCount(value=value, label=label, count=counts.get(value, 0))
        for value, label in enum_cls.labels().items()
    ]


def build_summary(db: Session, recent_limit: int = 5) -> OverviewSummary:
    today = date.today()
    since = now_local() - timedelta(days=30)

    reservoir_total = db.scalar(select(func.count()).select_from(Reservoir)) or 0
    reservoir_attention = (
        db.scalar(
            select(func.count())
            .select_from(Reservoir)
            .where(Reservoir.status != ReservoirStatus.NORMAL.value)
        )
        or 0
    )

    inspection_total = db.scalar(select(func.count()).select_from(Inspection)) or 0
    inspection_last_30_days = (
        db.scalar(
            select(func.count()).select_from(Inspection).where(Inspection.inspected_at >= since)
        )
        or 0
    )

    hazard_total = db.scalar(select(func.count()).select_from(Hazard)) or 0
    hazard_open = (
        db.scalar(
            select(func.count())
            .select_from(Hazard)
            .where(Hazard.status != HazardStatus.CLOSED.value)
        )
        or 0
    )
    hazard_overdue = (
        db.scalar(
            select(func.count())
            .select_from(Hazard)
            .where(
                Hazard.status != HazardStatus.CLOSED.value,
                Hazard.deadline.is_not(None),
                Hazard.deadline < today,
            )
        )
        or 0
    )

    recent_inspections = []
    for inspection in db.scalars(
        select(Inspection)
        .options(selectinload(Inspection.reservoir))
        .order_by(Inspection.inspected_at.desc(), Inspection.id.desc())
        .limit(recent_limit)
    ).all():
        brief = InspectionBrief.model_validate(inspection)
        brief.reservoir_name = inspection.reservoir.name if inspection.reservoir else ""
        recent_inspections.append(brief)

    urgent_hazards = [
        HazardRead.model_validate(hazard)
        for hazard in db.scalars(
            select(Hazard)
            .options(selectinload(Hazard.reservoir))
            .where(Hazard.status != HazardStatus.CLOSED.value)
            .order_by(
                or_(
                    Hazard.deadline.is_(None),
                    Hazard.deadline >= today,
                ).asc(),
                Hazard.deadline.asc(),
                Hazard.severity.desc(),
                Hazard.id.desc(),
            )
            .limit(recent_limit)
        ).all()
    ]

    return OverviewSummary(
        reservoir_total=reservoir_total,
        reservoir_attention=reservoir_attention,
        reservoir_by_status=_distribution(db, Reservoir, Reservoir.status, ReservoirStatus),
        inspection_total=inspection_total,
        inspection_last_30_days=inspection_last_30_days,
        inspection_by_type=_distribution(db, Inspection, Inspection.inspect_type, InspectionType),
        hazard_total=hazard_total,
        hazard_open=hazard_open,
        hazard_overdue=hazard_overdue,
        hazard_by_status=_distribution(db, Hazard, Hazard.status, HazardStatus),
        hazard_by_severity=_distribution(db, Hazard, Hazard.severity, HazardSeverity),
        recent_inspections=recent_inspections,
        urgent_hazards=urgent_hazards,
    )
