"""隐患登记与整改跟踪接口测试。"""

from datetime import date, timedelta

from tests.conftest import API


def _create_hazard(client, reservoir_id: int, **overrides) -> dict:
    payload = {
        "reservoir_id": reservoir_id,
        "title": "坝体局部裂缝",
        "category": "dam_body",
        "severity": "general",
        "source": "inspection",
        "discoverer": "张三",
        "description": "坝顶发现横向裂缝",
        "plan": "灌浆处理",
    }
    payload.update(overrides)
    response = client.post(f"{API}/hazards", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_hazard_writes_register_record(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])

    assert hazard["code"].startswith("YH" + date.today().strftime("%Y%m%d"))
    assert hazard["status"] == "registered"
    assert hazard["is_overdue"] is False
    assert hazard["closed_on"] is None
    assert [record["action"] for record in hazard["rectifications"]] == ["register"]
    assert hazard["reservoir"]["name"] == reservoir["name"]


def test_create_hazard_rejects_inspection_of_other_reservoir(client, make_reservoir):
    first = make_reservoir()
    second = make_reservoir()
    inspection = client.post(
        f"{API}/inspections", json={"reservoir_id": first["id"], "inspector": "张三"}
    ).json()

    response = client.post(
        f"{API}/hazards",
        json={
            "reservoir_id": second["id"],
            "inspection_id": inspection["id"],
            "title": "跨水库引用",
            "category": "dam_body",
        },
    )
    assert response.status_code == 422


def test_measure_record_moves_hazard_to_rectifying(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])

    response = client.post(
        f"{API}/hazards/{hazard['id']}/rectifications",
        json={"action": "measure", "content": "安排施工队进场灌浆", "operator": "李四"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "rectifying"

    records = body["rectifications"]
    assert records[-1]["status_from"] == "registered"
    assert records[-1]["status_to"] == "rectifying"


def test_progress_record_does_not_change_status(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])

    response = client.post(
        f"{API}/hazards/{hazard['id']}/rectifications",
        json={"action": "progress", "content": "已联系施工队"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "registered"


def test_full_rectification_flow(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])
    url = f"{API}/hazards/{hazard['id']}/transition"

    invalid = client.post(url, json={"target_status": "pending_acceptance"})
    assert invalid.status_code == 409
    assert "不允许" in invalid.json()["detail"]

    started = client.post(
        url, json={"target_status": "rectifying", "operator": "李四"}
    )
    assert started.status_code == 200
    assert started.json()["status"] == "rectifying"

    missing_content = client.post(url, json={"target_status": "pending_acceptance"})
    assert missing_content.status_code == 422
    assert "处理说明" in missing_content.json()["detail"]

    submitted = client.post(
        url,
        json={"target_status": "pending_acceptance", "content": "裂缝已灌浆处理", "operator": "李四"},
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "pending_acceptance"

    rejected = client.post(
        url,
        json={"target_status": "rectifying", "content": "现场复核仍有渗水，退回整改"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rectifying"

    client.post(url, json={"target_status": "pending_acceptance", "content": "已重新处理"})
    closed = client.post(url, json={"target_status": "closed", "operator": "验收组"})
    assert closed.status_code == 200
    body = closed.json()
    assert body["status"] == "closed"
    assert body["closed_on"] == date.today().isoformat()
    assert body["rectifications"][-1]["status_to"] == "closed"

    # 已销号为终态：既不能再流转，也不能追加记录
    assert client.post(url, json={"target_status": "rectifying"}).status_code == 409
    blocked = client.post(
        f"{API}/hazards/{hazard['id']}/rectifications",
        json={"action": "progress", "content": "补充记录"},
    )
    assert blocked.status_code == 409


def test_status_cannot_be_changed_through_update(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])

    response = client.put(
        f"{API}/hazards/{hazard['id']}", json={"status": "closed", "severity": "major"}
    )
    assert response.status_code == 422
    assert "transition" in response.json()["detail"]

    ok = client.put(f"{API}/hazards/{hazard['id']}", json={"severity": "major"})
    assert ok.status_code == 200
    assert ok.json()["severity"] == "major"


def test_overdue_flag_and_filter(client, make_reservoir):
    reservoir = make_reservoir()
    overdue = _create_hazard(
        client,
        reservoir["id"],
        title="逾期隐患",
        deadline=(date.today() - timedelta(days=2)).isoformat(),
    )
    future = _create_hazard(
        client,
        reservoir["id"],
        title="未到期隐患",
        deadline=(date.today() + timedelta(days=5)).isoformat(),
    )
    assert overdue["is_overdue"] is True
    assert future["is_overdue"] is False

    page = client.get(f"{API}/hazards", params={"overdue_only": True}).json()
    assert page["total"] == 1
    assert page["items"][0]["title"] == "逾期隐患"

    open_page = client.get(f"{API}/hazards", params={"open_only": True}).json()
    assert open_page["total"] == 2


def test_hazard_filters_and_delete(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"], severity="major", category="spillway")

    by_severity = client.get(f"{API}/hazards", params={"severity": "major"}).json()
    assert by_severity["total"] == 1

    by_category = client.get(f"{API}/hazards", params={"category": "outlet"}).json()
    assert by_category["total"] == 0

    by_keyword = client.get(f"{API}/hazards", params={"keyword": "坝体局部"}).json()
    assert by_keyword["total"] == 1

    assert client.delete(f"{API}/hazards/{hazard['id']}").status_code == 200
    assert client.get(f"{API}/hazards/{hazard['id']}").status_code == 404


def test_missing_hazard_returns_404(client):
    assert client.get(f"{API}/hazards/123456").status_code == 404

