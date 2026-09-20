"""字典与健康检查接口测试。"""

from tests.conftest import API


def test_health(client):
    response = client.get(f"{API}/meta/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["version"]


def test_options_contains_all_dicts(client):
    response = client.get(f"{API}/meta/options")
    assert response.status_code == 200
    body = response.json()

    expected = {
        "reservoir_status",
        "safety_class",
        "dam_type",
        "structure_part",
        "inspection_type",
        "weather",
        "inspection_status",
        "item_result",
        "hazard_severity",
        "hazard_source",
        "hazard_status",
        "rectification_action",
    }
    assert expected.issubset(body["dicts"].keys())
    assert {"value", "label"} == set(body["dicts"]["hazard_status"][0].keys())
    assert isinstance(body["regions"], list)


def test_options_exposes_hazard_state_machine(client):
    body = client.get(f"{API}/meta/options").json()
    transitions = body["hazard_transitions"]

    assert set(transitions.keys()) == {
        "registered",
        "rectifying",
        "pending_acceptance",
        "closed",
    }
    assert transitions["closed"] == []
    registered_targets = {item["target_status"] for item in transitions["registered"]}
    assert registered_targets == {"rectifying", "closed"}


def test_root_and_docs(client):
    assert client.get("/").status_code == 200
    assert client.get("/openapi.json").status_code == 200

