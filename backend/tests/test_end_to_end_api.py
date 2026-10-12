import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import engine, Base, SessionLocal
from app.repositories.app_repo import AppRepository
from app.repositories.telemetry_repo import TelemetryRepository
from app.simulator.campus_simulator import simulator_engine
from app.ingestion.cleaner import TelemetryCleaner

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        app_repo = AppRepository(db)
        app_repo.seed_initial_data()
        
        telemetry_repo = TelemetryRepository(db)
        readings = simulator_engine.generate_snapshot()
        for r in readings:
            cleaned, quality, _ = TelemetryCleaner.clean_and_tag(r)
            cleaned["quality"] = quality
            telemetry_repo.insert_reading(cleaned)
    finally:
        db.close()
    yield

client = TestClient(app)

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "api" in data["services"]

def test_root_metadata():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["brand"] == "Fluxora"
    assert res.json()["headline"] == "Smarter Energy for a Sustainable Tomorrow"

def test_get_devices():
    res = client.get("/api/devices")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) >= 8

def test_live_telemetry():
    res = client.get("/api/telemetry/live")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "aggregates" in data["data"]
    assert "devices" in data["data"]

def test_post_telemetry_reading():
    payload = {
        "deviceId": "hvac-01",
        "powerKw": 42.5,
        "voltage": 230.0,
        "current": 185.0,
        "powerFactor": 0.94
    }
    res = client.post("/api/telemetry/readings", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["powerKw"] == 42.5

def test_forecast_api():
    res = client.get("/api/forecast?horizonHours=24")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["model"] == "xgboost"
    assert len(data["data"]["points"]) == 24

def test_optimization_run_and_approval():
    res = client.post("/api/optimization/run")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "estimatedImpact" in data["data"]

    # Test recommendation approval lifecycle
    recs_res = client.get("/api/optimization/recommendations")
    assert recs_res.status_code == 200
    recs = recs_res.json()["data"]
    if recs:
        rec_id = recs[0]["id"]
        appr_res = client.post(f"/api/optimization/recommendations/{rec_id}/approve")
        assert appr_res.status_code == 200
        assert appr_res.json()["data"]["status"] == "executed"

def test_savings_verification():
    res = client.get("/api/savings/verified")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["status"] == "verified"
    assert data["data"]["savingKwh"] > 0
    assert data["data"]["costAvoided"] > 0

def test_simulator_scenario_switching():
    res = client.post("/api/simulator/scenario", json={"scenario": "peak_spike"})
    assert res.status_code == 200
    assert res.json()["success"] is True
    
    # Check that hvac-01 power rose
    live = client.get("/api/telemetry/live").json()
    hvac = next(d for d in live["data"]["devices"] if d["deviceId"] == "hvac-01")
    assert hvac["powerKw"] > 35.0
