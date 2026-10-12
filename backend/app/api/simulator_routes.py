from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.simulator.campus_simulator import simulator_engine
from app.repositories.telemetry_repo import TelemetryRepository
from app.ingestion.cleaner import TelemetryCleaner

router = APIRouter(prefix="/api/simulator", tags=["Simulator Controls"])

@router.get("/state")
def get_simulator_state():
    return {
        "success": True,
        "data": {
            "currentScenario": simulator_engine.scenario,
            "batterySocPercent": round(simulator_engine.battery_soc, 1),
            "batteryState": simulator_engine.battery_state,
            "batteryPowerKw": simulator_engine.battery_power_kw,
            "evCharging": simulator_engine.ev_charging,
            "evShifted": simulator_engine.ev_shifted,
            "hvacSetpointC": simulator_engine.hvac_setpoint,
            "hvacCurtailed": simulator_engine.hvac_curtailed,
            "lastTick": simulator_engine.last_tick_time.isoformat() + "Z"
        },
        "meta": {"isSimulated": True, "notice": "DEMO SCENARIO ENGINE ACTIVE"}
    }

@router.post("/scenario")
def set_scenario(scenario_data: dict = Body(...), db: Session = Depends(get_db)):
    sc = scenario_data.get("scenario", "normal")
    success = simulator_engine.set_scenario(sc)
    
    # Tick immediately to reflect changes in database
    readings = simulator_engine.generate_snapshot()
    repo = TelemetryRepository(db)
    for r in readings:
        cleaned, quality, _ = TelemetryCleaner.clean_and_tag(r)
        cleaned["quality"] = quality
        repo.insert_reading(cleaned)

    return {
        "success": success,
        "data": {
            "scenario": sc,
            "message": f"Simulation scenario switched to '{sc}'. Telemetry readings updated."
        },
        "meta": {"isSimulated": True}
    }

@router.post("/tick")
def run_simulation_tick(db: Session = Depends(get_db)):
    readings = simulator_engine.generate_snapshot()
    repo = TelemetryRepository(db)
    for r in readings:
        cleaned, quality, _ = TelemetryCleaner.clean_and_tag(r)
        cleaned["quality"] = quality
        repo.insert_reading(cleaned)
    
    return {
        "success": True,
        "data": {"readingsGenerated": len(readings), "scenario": simulator_engine.scenario},
        "meta": {"isSimulated": True}
    }
