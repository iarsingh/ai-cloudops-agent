from fastapi.testclient import TestClient

from cloudops.main import app

client = TestClient(app)


def test_investigation_calls_three_tools_and_does_not_page():
    body = client.post("/agent/run", json={"goal": "investigate the billing memory alert"}).json()
    assert [step["tool"] for step in body["trace"]] == ["list_alerts", "read_logs", "check_manifest"]
    assert body["paged"] is False
    assert body["confirmed_root_cause"] is False
