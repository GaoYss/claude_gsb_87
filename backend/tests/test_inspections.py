"""巡查记录接口测试。"""

from datetime import date

from tests.conftest import API


def _payload(reservoir_id: int, **overrides) -> dict:
    payload = {
        "reservoir_id": reservoir_id,
        "inspector": "张三",
        "inspect_type": "daily",
        "weather": "sunny",
        "water_level": 61.2,
        "rainfall": 0,
        "route": "坝顶→溢洪道",
        "summary": "巡查完成",
        "items": [{"part": "dam_body", "result": "normal", "description": ""}],
    }
    payload.update(overrides)
    return payload


def test_create_inspection_generates_code_and_normal_status(client, make_reservoir):
    reservoir = make_reservoir()
    response = client.post(f"{API}/inspections", json=_payload(reservoir["id"]))

    assert response.status_code == 201
    body = response.json()
    assert body["code"].startswith("XC" + date.today().strftime("%Y%m%d"))
    assert body["status"] == "normal"
    assert len(body["items"]) == 1
    assert body["reservoir"]["id"] == reservoir["id"]
    assert body["reservoir"]["name"] == reservoir["name"]


def test_abnormal_item_marks_inspection_abnormal(client, make_reservoir):
    reservoir = make_reservoir()
    response = client.post(
        f"{API}/inspections",
        json=_payload(
            reservoir["id"],
            items=[
                {"part": "dam_body", "result": "normal"},
                {"part": "seepage", "result": "abnormal", "description": "坝脚渗水"},
            ],
        ),
    )
    assert response.status_code == 201
    assert response.json()["status"] == "abnormal"


def test_create_requires_existing_reservoir_and_inspector(client, make_reservoir):
    reservoir = make_reservoir()
    missing_inspector = client.post(
        f"{API}/inspections", json={"reservoir_id": reservoir["id"]}
    )
    assert missing_inspector.status_code == 422

    unknown_reservoir = client.post(
        f"{API}/inspections", json={"reservoir_id": 999999, "inspector": "张三"}
    )
    assert unknown_reservoir.status_code == 404


def test_update_replaces_items_and_recomputes_status(client, make_reservoir):
    reservoir = make_reservoir()
    created = client.post(
        f"{API}/inspections",
        json=_payload(
            reservoir["id"], items=[{"part": "dam_body", "result": "abnormal"}]
        ),
    ).json()
    assert created["status"] == "abnormal"

    response = client.put(
        f"{API}/inspections/{created['id']}",
        json={
            "summary": "已完成处理",
            "items": [{"part": "dam_body", "result": "normal", "description": "已修补"}],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "normal"
    assert len(body["items"]) == 1
    assert body["items"][0]["description"] == "已修补"
    assert body["summary"] == "已完成处理"


def test_list_inspections_by_reservoir_and_status(client, make_reservoir):
    first = make_reservoir()
    second = make_reservoir()
    client.post(f"{API}/inspections", json=_payload(first["id"]))
    client.post(
        f"{API}/inspections",
        json=_payload(second["id"], items=[{"part": "outlet", "result": "abnormal"}]),
    )

    all_items = client.get(f"{API}/inspections").json()
    assert all_items["total"] == 2

    by_reservoir = client.get(
        f"{API}/inspections", params={"reservoir_id": first["id"]}
    ).json()
    assert by_reservoir["total"] == 1
    assert by_reservoir["items"][0]["reservoir_id"] == first["id"]

    abnormal = client.get(f"{API}/inspections", params={"status": "abnormal"}).json()
    assert abnormal["total"] == 1
    assert abnormal["items"][0]["status"] == "abnormal"

    by_keyword = client.get(f"{API}/inspections", params={"keyword": second["name"]}).json()
    assert by_keyword["total"] == 1


def test_delete_inspection_blocked_when_has_hazard(client, make_reservoir):
    reservoir = make_reservoir()
    inspection = client.post(f"{API}/inspections", json=_payload(reservoir["id"])).json()
    client.post(
        f"{API}/hazards",
        json={
            "reservoir_id": reservoir["id"],
            "inspection_id": inspection["id"],
            "title": "来源巡查的隐患",
            "category": "dam_body",
        },
    )

    blocked = client.delete(f"{API}/inspections/{inspection['id']}")
    assert blocked.status_code == 422
    assert "隐患" in blocked.json()["detail"]

    hazard = client.get(f"{API}/hazards", params={"inspection_id": inspection["id"]}).json()
    client.delete(f"{API}/hazards/{hazard['items'][0]['id']}")
    assert client.delete(f"{API}/inspections/{inspection['id']}").status_code == 200


def test_get_missing_inspection_returns_404(client):
    assert client.get(f"{API}/inspections/424242").status_code == 404

