from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.app_repo import AppRepository
from app.schemas.schemas import DeviceCommand, DeviceOut
from app.simulator.campus_simulator import simulator_engine
import datetime

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.get("")
def list_devices(db: Session = Depends(get_db)):
    repo = AppRepository(db)
    devices = repo.get_devices()
    return {
        "success": True,
        "data": [
            {
                "id": d.id,
                "name": d.name,
                "deviceType": d.device_type,
                "zoneId": d.zone_id,
                "ratedPowerKw": d.rated_power_kw,
                "currentPowerKw": d.current_power_kw,
                "todayEnergyKwh": d.today_energy_kwh,
                "controllable": d.controllable,
                "status": d.status,
                "isSimulated": d.is_simulated,
                "lastSeen": d.last_seen.isoformat() + "Z",
                "deviceMetadata": d.device_metadata or {}
            }
            for d in devices
        ]
    }

@router.get("/{device_id}")
def get_device_detail(device_id: str, db: Session = Depends(get_db)):
    repo = AppRepository(db)
    device = repo.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        "success": True,
        "data": {
            "id": device.id,
            "name": device.name,
            "deviceType": device.device_type,
            "zoneId": device.zone_id,
            "ratedPowerKw": device.rated_power_kw,
            "currentPowerKw": device.current_power_kw,
            "todayEnergyKwh": device.today_energy_kwh,
            "controllable": device.controllable,
            "status": device.status,
            "isSimulated": device.is_simulated,
            "lastSeen": device.last_seen.isoformat() + "Z",
            "deviceMetadata": device.device_metadata or {}
        }
    }

@router.post("/{device_id}/command")
def send_device_command(device_id: str, cmd: DeviceCommand, db: Session = Depends(get_db)):
    """
    Executes a safe control action on the device.
    Applies change to simulator physics and logs an immutable audit event in the database.
    """
    repo = AppRepository(db)
    device = repo.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if not device.controllable:
        raise HTTPException(status_code=400, detail=f"Device {device_id} is marked non-controllable (sensor only)")

    # 1. Forward to simulator physics engine
    sim_result = simulator_engine.execute_command(device_id, cmd.command, cmd.parameters or {})

    # 2. Update device metadata in DB
    meta = device.device_metadata or {}
    meta["lastCommand"] = cmd.command
    meta["lastCommandTime"] = datetime.datetime.utcnow().isoformat() + "Z"
    repo.update_device(device_id, device_metadata=meta)

    # 3. Log audit event
    action_log = repo.log_action(
        rec_id=cmd.parameters.get("recommendationId"),
        command=cmd.command,
        target_device_id=device_id,
        parameters=cmd.parameters,
        actor=cmd.actor or "operator@fluxora.local"
    )

    return {
        "success": True,
        "data": {
            "actionId": action_log.id,
            "deviceId": device_id,
            "command": cmd.command,
            "result": sim_result.get("status", "executed"),
            "message": sim_result.get("message", "Command executed"),
            "timestamp": action_log.timestamp.isoformat() + "Z"
        },
        "meta": {"isSimulated": True}
    }
