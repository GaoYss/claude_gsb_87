"""隐患登记与整改跟踪接口测试。"""

from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.models.enums import HazardStatus
from app.schemas.hazard import HazardTransitionRequest
from app.services import hazard_service
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
    closed = client.post(
        url,
        json={
            "target_status": "closed",
            "operator": "验收组",
            "acceptance_opinion": "现场复核整改到位，同意销号",
            "closed_on": date.today().isoformat(),
        },
    )
    assert closed.status_code == 200
    body = closed.json()
    assert body["status"] == "closed"
    assert body["closed_on"] == date.today().isoformat()
    close_record = body["rectifications"][-1]
    assert close_record["status_to"] == "closed"
    assert close_record["acceptance_opinion"] == "现场复核整改到位，同意销号"
    assert close_record["closed_on"] == date.today().isoformat()

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


# ---------- 销号前置校验：验收意见 + 销号日期缺一不可，失败不留半成品 ----------


def test_close_missing_fields_is_rejected_and_leaves_no_halfwork(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])
    url = f"{API}/hazards/{hazard['id']}/transition"
    today = date.today().isoformat()

    def assert_unchanged():
        fresh = client.get(f"{API}/hazards/{hazard['id']}").json()
        assert fresh["status"] == "registered"
        assert fresh["closed_on"] is None
        # 只有登记一条流水，失败的销号尝试不得写入半成品流水
        assert [r["action"] for r in fresh["rectifications"]] == ["register"]

    # 只填验收意见，缺销号日期
    missing_date = client.post(
        url,
        json={"target_status": "closed", "acceptance_opinion": "整改到位，同意销号"},
    )
    assert missing_date.status_code == 422
    assert "销号日期" in missing_date.json()["detail"]
    assert_unchanged()

    # 只填销号日期，缺验收意见
    missing_opinion = client.post(
        url, json={"target_status": "closed", "closed_on": today}
    )
    assert missing_opinion.status_code == 422
    assert "验收意见" in missing_opinion.json()["detail"]
    assert_unchanged()

    # 两项都缺：一次性提示全部缺项
    missing_both = client.post(url, json={"target_status": "closed"})
    assert missing_both.status_code == 422
    detail = missing_both.json()["detail"]
    assert "验收意见" in detail and "销号日期" in detail
    assert_unchanged()


def test_close_date_must_be_reasonable(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])  # 发现日期默认为今天
    url = f"{API}/hazards/{hazard['id']}/transition"

    future = client.post(
        url,
        json={
            "target_status": "closed",
            "acceptance_opinion": "同意销号",
            "closed_on": (date.today() + timedelta(days=1)).isoformat(),
        },
    )
    assert future.status_code == 422
    assert "晚于今天" in future.json()["detail"]

    past = client.post(
        url,
        json={
            "target_status": "closed",
            "acceptance_opinion": "同意销号",
            "closed_on": (date.today() - timedelta(days=1)).isoformat(),
        },
    )
    assert past.status_code == 422
    assert "早于隐患发现日期" in past.json()["detail"]

    # 校验失败同样不得改动状态
    fresh = client.get(f"{API}/hazards/{hazard['id']}").json()
    assert fresh["status"] == "registered"
    assert fresh["closed_on"] is None


def test_close_records_audit_trail(client, make_reservoir):
    """谁、什么时点、依据哪份验收意见、销号日期，销号后随时可回看。"""
    reservoir = make_reservoir()
    hazard = _create_hazard(
        client,
        reservoir["id"],
        discovered_on=(date.today() - timedelta(days=5)).isoformat(),
    )
    url = f"{API}/hazards/{hazard['id']}/transition"
    client.post(url, json={"target_status": "rectifying", "operator": "李四"})
    client.post(
        url,
        json={"target_status": "pending_acceptance", "content": "已处理完成，申请验收", "operator": "李四"},
    )

    closed_on = date.today() - timedelta(days=1)  # 支持补录销号日期
    response = client.post(
        url,
        json={
            "target_status": "closed",
            "operator": "验收组赵工",
            "acceptance_opinion": "现场复核处理到位、无残留问题，同意销号",
            "closed_on": closed_on.isoformat(),
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "closed"
    assert body["closed_on"] == closed_on.isoformat()

    record = body["rectifications"][-1]
    assert record["status_from"] == "pending_acceptance"
    assert record["status_to"] == "closed"
    assert record["acceptance_opinion"] == "现场复核处理到位、无残留问题，同意销号"
    assert record["closed_on"] == closed_on.isoformat()
    assert record["operator"] == "验收组赵工"
    assert record["recorded_at"]  # 系统时点始终留痕


def test_close_links_latest_standalone_verify_opinion(client, make_reservoir):
    """直接销号（待验收 -> 已销号之外的路径）关联此前单独登记的验收意见。"""
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])

    # 整改中单独登记一条验收意见（不驱动状态流转）
    client.post(
        f"{API}/hazards/{hazard['id']}/rectifications",
        json={"action": "measure", "content": "进场处理", "operator": "李四"},
    )
    client.post(
        f"{API}/hazards/{hazard['id']}/rectifications",
        json={"action": "verify", "content": "复核合格，具备销号条件", "operator": "验收组赵工"},
    )

    response = client.post(
        f"{API}/hazards/{hazard['id']}/transition",
        json={
            "target_status": "closed",
            "operator": "验收组赵工",
            "acceptance_opinion": "复核合格，同意销号",
            "closed_on": date.today().isoformat(),
        },
    )
    assert response.status_code == 200, response.text
    records = response.json()["rectifications"]
    verify_ids = {r["id"] for r in records if r["action"] == "verify"}
    close_record = records[-1]
    assert close_record["acceptance_record_id"] in verify_ids


# ---------- 并发销号：同一隐患两人同时销号，只能生效一次 ----------


def test_concurrent_close_only_one_takes_effect(client, make_reservoir, db_session: Session):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])

    engine = db_session.bind
    session_a = Session(engine)
    session_b = Session(engine)
    try:
        # 两个经办人在各自会话中几乎同时读到「待整改」，各自发起销号
        get_a = hazard_service.get_hazard(session_a, hazard["id"])
        get_b = hazard_service.get_hazard(session_b, hazard["id"])
        assert get_a.status == HazardStatus.REGISTERED.value
        assert get_b.status == HazardStatus.REGISTERED.value

        payload_a = HazardTransitionRequest(
            target_status=HazardStatus.CLOSED,
            operator="经办人甲",
            acceptance_opinion="验收合格，甲办理销号",
            closed_on=date.today(),
        )
        payload_b = HazardTransitionRequest(
            target_status=HazardStatus.CLOSED,
            operator="经办人乙",
            acceptance_opinion="验收合格，乙办理销号",
            closed_on=date.today(),
        )

        hazard_service.transition_hazard(session_a, hazard["id"], payload_a)

        # 乙持有的是旧状态，条件 UPDATE 命中 0 行：不得覆盖、不得再写流水
        with pytest.raises(ConflictError) as exc_info:
            hazard_service.transition_hazard(session_b, hazard["id"], payload_b)
        message = str(exc_info.value)
        assert "经办人甲" in message
        assert "本次操作未生效" in message
    finally:
        session_a.close()
        session_b.close()

    db_session.expire_all()
    fresh = client.get(f"{API}/hazards/{hazard['id']}").json()
    assert fresh["status"] == "closed"
    assert fresh["closed_on"] == date.today().isoformat()

    close_records = [r for r in fresh["rectifications"] if r["status_to"] == "closed"]
    assert len(close_records) == 1
    assert close_records[0]["operator"] == "经办人甲"
    assert close_records[0]["acceptance_opinion"] == "验收合格，甲办理销号"


def test_close_twice_second_side_gets_conflict_message(client, make_reservoir):
    reservoir = make_reservoir()
    hazard = _create_hazard(client, reservoir["id"])
    url = f"{API}/hazards/{hazard['id']}/transition"
    payload = {
        "target_status": "closed",
        "operator": "经办人甲",
        "acceptance_opinion": "同意销号",
        "closed_on": date.today().isoformat(),
    }

    assert client.post(url, json=payload).status_code == 200
    second = client.post(url, json=payload)
    assert second.status_code == 409
    assert "经办人甲" in second.json()["detail"]
    assert "已" in second.json()["detail"] and "销号" in second.json()["detail"]

