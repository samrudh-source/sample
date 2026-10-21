from fastapi.testclient import TestClient

from app.main import app


def test_health_and_simulation_endpoints(tmp_path, monkeypatch):
    monkeypatch.setenv("ECOVISION_DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        response = client.post("/api/simulate", json={"vehicles": 5000})
        assert response.status_code == 200
        assert response.json()["data_status"] == "simulated"


def test_simulation_rejects_out_of_range_values():
    with TestClient(app) as client:
        response = client.post("/api/simulate", json={"vehicles": 100001})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"


def test_awareness_endpoints():
    with TestClient(app) as client:
        assert len(client.get("/api/awareness/facts").json()["facts"]) >= 4
        result = client.post("/api/awareness/quiz/submit", json={"answers": [1, 0, 1]})
        assert result.json() == {"score": 3, "total": 3, "complete": True}


def test_external_data_failure_keeps_structured_response(monkeypatch):
    import asyncio
    from fastapi import HTTPException

    async def unavailable(*_args, **_kwargs):
        raise HTTPException(status_code=503, detail={"code": "environment_data_unavailable", "message": "Try again later."})

    monkeypatch.setattr("app.main.fetch_environment", unavailable)
    with TestClient(app) as client:
        response = client.get("/api/air-quality?city=New%20Delhi")
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "environment_data_unavailable"