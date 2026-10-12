from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.app_repo import AppRepository
from app.repositories.telemetry_repo import TelemetryRepository
from app.optimization.optimizer import ConstrainedEnergyOptimizer
from app.simulator.campus_simulator import simulator_engine
import datetime

router = APIRouter(prefix="/api/optimization", tags=["Optimization"])

@router.post("/run")
def run_optimization(db: Session = Depends(get_db)):
    """
    Appendix D Contract:
    POST /api/optimization/run
    { "objective": "minimize_cost_and_peak", "actions": [
        {"deviceId":"ev-01","start":"21:00","end":"23:00","targetKwh":40},
        {"deviceId":"battery-01","action":"discharge","energyKwh":80} ], 
      "estimatedImpact": { "costAvoided": 8420, "peakReductionKw": 32 } }
    """
    telemetry_repo = TelemetryRepository(db)
    load_stats = telemetry_repo.get_total_live_load()
    
    # Solve constrained schedule
    opt_result = ConstrainedEnergyOptimizer.solve(
        forecast_peak_kw=max(180.0, load_stats["totalLoadKw"]),
        solar_capacity_kw=50.0,
        battery_soc_percent=simulator_engine.battery_soc,
        ev_connected=True
    )

    return {
        "success": True,
        "data": opt_result,
        "meta": {
            "isSimulated": True,
            "disclaimer": "Optimization output provides constrained actionable schedules. Requires operator approval before dispatch."
        }
    }

@router.get("/recommendations")
def get_recommendations(db: Session = Depends(get_db)):
    repo = AppRepository(db)
    recs = repo.get_recommendations()
    return {
        "success": True,
        "data": [
            {
                "id": r.id,
                "priority": r.priority,
                "title": r.title,
                "action": r.action,
                "reason": r.reason,
                "targetDeviceId": r.target_device_id,
                "estimatedImpact": r.estimated_impact or {},
                "status": r.status,
                "modelVersion": r.model_version,
                "createdAt": r.created_at.isoformat() + "Z"
            }
            for r in recs
        ],
        "meta": {"isSimulated": True}
    }

@router.post("/recommendations/{rec_id}/approve")
def approve_recommendation(rec_id: str, db: Session = Depends(get_db)):
    """
    Operator approves a prescriptive recommendation.
    Triggers simulated BMS execution and updates telemetry state.
    """
    repo = AppRepository(db)
    rec = repo.update_recommendation_status(rec_id, "approved")
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Execute corresponding control action on simulator
    if rec.target_device_id == "battery-01":
        simulator_engine.execute_command("battery-01", "DISCHARGE", {"powerKw": 30.0})
        # Also adjust HVAC
        simulator_engine.execute_command("hvac-01", "SETPOINT", {"setpoint": 25.0})
    elif rec.target_device_id == "ev-01":
        simulator_engine.execute_command("ev-01", "SHIFT", {})
    elif rec.target_device_id == "hvac-01":
        simulator_engine.execute_command("hvac-01", "SETPOINT", {"setpoint": 25.0})

    # Log action
    action_log = repo.log_action(
        rec_id=rec_id,
        command="APPROVE_AND_DISPATCH",
        target_device_id=rec.target_device_id or "battery-01",
        parameters={"recommendationId": rec_id, "action": rec.action},
        actor="operator@fluxora.local"
    )

    repo.update_recommendation_status(rec_id, "executed")

    return {
        "success": True,
        "data": {
            "recommendationId": rec_id,
            "status": "executed",
            "actionId": action_log.id,
            "message": "Optimization schedule approved. BMS commands dispatched to target devices."
        },
        "meta": {"isSimulated": True}
    }

@router.post("/recommendations/{rec_id}/reject")
def reject_recommendation(rec_id: str, db: Session = Depends(get_db)):
    repo = AppRepository(db)
    rec = repo.update_recommendation_status(rec_id, "rejected")
    return {
        "success": True,
        "data": {"recommendationId": rec_id, "status": "rejected"}
    }
