"""总览页接口。"""

from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas.overview import OverviewSummary
from app.services import overview_service

router = APIRouter(prefix="/overview", tags=["总览"])


@router.get("/summary", response_model=OverviewSummary, summary="首页统计与待办")
def get_summary(db: DbSession) -> OverviewSummary:
    return overview_service.build_summary(db)

