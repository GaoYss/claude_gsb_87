"""ORM 模型集中导出，确保 Base.metadata 能注册全部表。"""

from app.db.base import Base
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
from app.models.hazard import Hazard, HazardRectification
from app.models.inspection import Inspection, InspectionItem
from app.models.reservoir import Reservoir

__all__ = [
    "Base",
    "DamType",
    "Hazard",
    "HazardRectification",
    "HazardSeverity",
    "HazardSource",
    "HazardStatus",
    "Inspection",
    "InspectionItem",
    "InspectionStatus",
    "InspectionType",
    "ItemResult",
    "RectificationAction",
    "Reservoir",
    "ReservoirStatus",
    "SafetyClass",
    "StructurePart",
    "Weather",
]

