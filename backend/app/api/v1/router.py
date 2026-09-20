"""v1 路由汇总。"""

from fastapi import APIRouter

from app.api.v1.endpoints import hazards, inspections, meta, overview, reservoirs

api_router = APIRouter()
api_router.include_router(meta.router)
api_router.include_router(overview.router)
api_router.include_router(reservoirs.router)
api_router.include_router(inspections.router)
api_router.include_router(hazards.router)

