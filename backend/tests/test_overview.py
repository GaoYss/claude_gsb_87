"""总览统计接口测试。"""

from datetime import date, timedelta

from tests.conftest import API


def test_summary_counts_and_distributions(client, make_reservoir):
    reservoir = make_reservoir()
    make_reservoir(status="danger")

    client.post(
        f"{API}/inspections",
        json={
            "reservoir_id": reservoir["id"],
            "inspector": "张三",
            "inspect_type": "flood_season",
            "items": [{"part": "dam_body", "result": "abnormal"}],
        },
    )
    client.post(
        f"{API}/hazards",
        json={
            "reservoir_id": reservoir["id"],
            "title": "逾期隐患",
            "category": "dam_body",
            "severity": "major",
            "deadline": (date.today() - timedelta(days=1)).isoformat(),
        },
    )
    closed = client.post(
        f"{API}/hazards",
        json={
            "reservoir_id": reservoir["id"],
            "title": "已销号隐患",
            "category": "outlet",
            "severity": "general",
        },
    ).json()
    client.post(
        f"{API}/hazards/{closed['id']}/transition",
        json={
            "target_status": "closed",
            "content": "立行立改完成",
            "closed_on": date.today().isoformat(),
        },
    )

    summary = client.get(f"{API}/overview/summary").json()

    assert summary["reservoir_total"] == 2
    assert summary["reservoir_attention"] == 1
    assert summary["inspection_total"] == 1
    assert summary["inspection_last_30_days"] == 1
    assert summary["hazard_total"] == 2
    assert summary["hazard_open"] == 1
    assert summary["hazard_overdue"] == 1

    status_counts = {item["value"]: item["count"] for item in summary["hazard_by_status"]}
    assert status_counts["closed"] == 1
    assert status_counts["registered"] == 1
    assert {item["value"] for item in summary["hazard_by_status"]} == {
        "registered",
        "rectifying",
        "pending_acceptance",
        "closed",
    }

    type_counts = {item["value"]: item["count"] for item in summary["inspection_by_type"]}
    assert type_counts["flood_season"] == 1
    assert type_counts["daily"] == 0

    assert summary["recent_inspections"][0]["reservoir_name"] == reservoir["name"]
    assert summary["urgent_hazards"][0]["title"] == "逾期隐患"

