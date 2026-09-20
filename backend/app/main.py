"""应用入口：创建 FastAPI 实例、装配中间件与路由。"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import APP_VERSION
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import DomainError
from app.db.seed import seed_demo_data
from app.db.session import init_db

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """启动时建表并按需灌入演示数据。"""
    init_db()
    if settings.seed_demo_data:
        seed_demo_data()
    logger.info("%s 启动完成", settings.app_name)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=APP_VERSION,
        description="水库台账、日常巡查记录、隐患登记与整改跟踪的一体化轻量后端。",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=settings.cors_origin_list != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/", tags=["系统"], summary="服务信息")
    def read_root() -> dict[str, str]:
        return {
            "app": settings.app_name,
            "version": APP_VERSION,
            "api_prefix": settings.api_prefix,
            "docs": "/docs",
        }

    return app


app = create_app()

