"""水库台账接口测试。"""

from tests.conftest import API


def test_create_and_get_reservoir(client, make_reservoir):
    created = make_reservoir(code="SK-0001", name="示范水库")

    assert created["code"] == "SK-0001"
    assert created["name"] == "示范水库"
    assert created["status"] == "normal"
    assert created["safety_class"] == "class_two"

    detail = client.get(f"{API}/reservoirs/{created['id']}").json()
    assert detail["code"] == "SK-0001"
    assert detail["created_at"]


def test_duplicate_code_returns_conflict(client, make_reservoir):
    make_reservoir(code="SK-DUP")
    response = client.post(
        f"{API}/reservoirs",
        json={"code": "sk-dup", "name": "重复编码水库", "region": "测试区"},
    )
    assert response.status_code == 409
    assert "已存在" in response.json()["detail"]


def test_invalid_enum_returns_422(client, make_reservoir):
    response = client.post(
        f"{API}/reservoirs",
        json={"code": "SK-BAD", "name": "非法状态", "region": "测试区", "status": "unknown"},
    )
    assert response.status_code == 422


def test_missing_reservoir_returns_404(client):
    response = client.get(f"{API}/reservoirs/999999")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_update_reservoir_partially(client, make_reservoir):
    created = make_reservoir()
    response = client.put(
        f"{API}/reservoirs/{created['id']}",
        json={"status": "attention", "remark": "汛期加密巡查"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "attention"
    assert body["remark"] == "汛期加密巡查"
    assert body["name"] == created["name"]


def test_list_filters_and_pagination(client, make_reservoir):
    make_reservoir(name="甲水库", region="东区")
    make_reservoir(name="乙水库", region="西区", status="danger")

    page = client.get(f"{API}/reservoirs", params={"page_size": 1}).json()
    assert page["total"] == 2
    assert page["pages"] == 2
    assert len(page["items"]) == 1

    filtered = client.get(f"{API}/reservoirs", params={"keyword": "乙"}).json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["name"] == "乙水库"

    by_region = client.get(f"{API}/reservoirs", params={"region": "东区"}).json()
    assert by_region["total"] == 1

    by_status = client.get(f"{API}/reservoirs", params={"status": "danger"}).json()
    assert by_status["total"] == 1
    assert by_status["items"][0]["status"] == "danger"


def test_delete_reservoir_with_history_is_rejected(client, make_reservoir):
    reservoir = make_reservoir()
    inspection = client.post(
        f"{API}/inspections",
        json={"reservoir_id": reservoir["id"], "inspector": "张三"},
    )
    assert inspection.status_code == 201

    response = client.delete(f"{API}/reservoirs/{reservoir['id']}")
    assert response.status_code == 422
    assert "巡查记录" in response.json()["detail"]


def test_delete_empty_reservoir(client, make_reservoir):
    reservoir = make_reservoir()
    response = client.delete(f"{API}/reservoirs/{reservoir['id']}")
    assert response.status_code == 200
    assert client.get(f"{API}/reservoirs/{reservoir['id']}").status_code == 404


def test_reservoir_list_aggregates_and_stats(client, make_reservoir):
    reservoir = make_reservoir()
    client.post(
        f"{API}/inspections",
        json={
            "reservoir_id": reservoir["id"],
            "inspector": "张三",
            "items": [{"part": "dam_body", "result": "abnormal", "description": "坝体裂缝"}],
        },
    )
    hazard = client.post(
        f"{API}/hazards",
        json={
            "reservoir_id": reservoir["id"],
            "title": "坝体裂缝",
            "category": "dam_body",
            "severity": "serious",
        },
    )
    assert hazard.status_code == 201

    item = client.get(f"{API}/reservoirs", params={"keyword": reservoir["code"]}).json()["items"][0]
    assert item["inspection_count"] == 1
    assert item["open_hazard_count"] == 1
    assert item["last_inspected_at"] is not None

    stats = client.get(f"{API}/reservoirs/{reservoir['id']}/stats").json()
    assert stats["inspection_total"] == 1
    assert stats["hazard_total"] == 1
    assert stats["hazard_open"] == 1
    assert stats["hazard_closed"] == 0
