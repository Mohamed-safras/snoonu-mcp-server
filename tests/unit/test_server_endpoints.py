from starlette.testclient import TestClient

import src.server as server_module
from src.server import app

client = TestClient(app)


def test_health_returns_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_returns_ready_when_db_reachable():
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_ready_returns_503_when_db_unreachable(monkeypatch):
    class BrokenEngine:
        def connect(self):
            raise RuntimeError("db down")

    monkeypatch.setattr(server_module, "engine", BrokenEngine())
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json()["status"] == "unavailable"


def test_metrics_endpoint_exposes_prometheus_format():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    assert b"snoonu_mcp_db_pool_size" in r.content


def test_request_logging_middleware_adds_request_id_header():
    r = client.get("/health")
    assert "x-request-id" in r.headers
