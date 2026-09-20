"""测试夹具：内存 SQLite + 依赖覆盖，不触碰真实数据库。"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SEED_DEMO_DATA", "false")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  注册所有表
from app.api.deps import get_db
from app.db.base import Base
from app.main import create_app

API = "/api/v1"


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    """不用 with，避免触发 lifespan 里的建表与演示数据灌入。"""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


@pytest.fixture()
def make_reservoir(client: TestClient):
    """快速造一座水库，返回响应体。"""
    counter = {"n": 0}

    def _make(**overrides):
        counter["n"] += 1
        payload = {
            "code": f"SK-TEST-{counter['n']:03d}",
            "name": f"测试水库{counter['n']}号",
            "region": "测试区",
            "dam_type": "homogeneous_earth",
            "safety_class": "class_two",
            "total_capacity": 120.0,
            "normal_level": 60.0,
            "dam_height": 12.0,
        }
        payload.update(overrides)
        response = client.post(f"{API}/reservoirs", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make

