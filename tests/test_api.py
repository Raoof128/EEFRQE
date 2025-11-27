"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from backend.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_fair_endpoint_respects_settings() -> None:
    client = TestClient(create_app())
    payload = {
        "threat_event_frequency": [1, 2, 3],
        "vulnerability": [0.2, 0.5, 0.8],
        "primary_loss": [1000, 2000, 3000],
        "secondary_loss": [500, 1000, 2000],
        "secondary_event_frequency": [0.1, 0.2, 0.5],
    }

    response = client.post("/fair/calc", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "monte_carlo" in data
    assert data["monte_carlo"]["mean"] >= 0


def test_scenario_missing_controls_returns_400() -> None:
    client = TestClient(create_app())
    payload = {"scenario_key": "ransomware", "controls": []}
    response = client.post("/scenario/run", json=payload)
    assert response.status_code == 422  # validation error
