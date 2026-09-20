"""字典、健康检查等辅助接口。"""

from fastapi import APIRouter

from app import APP_VERSION
from app.api.deps import DbSession
from app.core.config import settings
from app.db.base import now_local
from app.models.enums import (
    DamType,
    HazardSeverity,
    HazardSource,
    HazardStatus,
    InspectionStatus,
    InspectionType,
    ItemResult,
    RectificationAction,
    ReservoirStatus,
    SafetyClass,
    StructurePart,
    Weather,
)
from app.schemas.meta import HealthStatus, MetaOptions
from app.services import hazard_service, reservoir_service

router = APIRouter(tags=["系统与字典"])

_ENUMS = {
    "reservoir_status": ReservoirStatus,
    "safety_class": SafetyClass,
    "dam_type": DamType,
    "structure_part": StructurePart,
    "inspection_type": InspectionType,
    "weather": Weather,
    "inspection_status": InspectionStatus,
    "item_result": ItemResult,
    "hazard_severity": HazardSeverity,
    "hazard_source": HazardSource,
    "hazard_status": HazardStatus,
    "rectification_action": RectificationAction,
}


@router.get("/meta/options", response_model=MetaOptions, summary="获取全部下拉字典")
def get_options(db: DbSession) -> MetaOptions:
    return MetaOptions(
        dicts={key: enum_cls.choices() for key, enum_cls in _ENUMS.items()},
        regions=reservoir_service.list_regions(db),
        hazard_transitions={
            status.value: hazard_service.available_transitions(status.value)
            for status in HazardStatus
        },
    )


@router.get("/meta/health", response_model=HealthStatus, summary="健康检查")
def health(db: DbSession) -> HealthStatus:
    from sqlalchemy import text

    database = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - 仅用于健康检查兜底
        database = f"error: {exc}"

    return HealthStatus(
        status="ok" if database == "ok" else "degraded",
        app=settings.app_name,
        version=APP_VERSION,
        database=database,
        time=now_local(),
    )
