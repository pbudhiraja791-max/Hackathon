from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import TelemetryReadingCreate, ApiResponse
from app.ingestion.cleaner import TelemetryCleaner
from app.repositories.telemetry_repo import TelemetryRepository
import datetime

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

@router.post("/readings")
def post_telemetry_reading(reading_in: TelemetryReadingCreate, db: Session = Depends(get_db)):
    """
    Appendix A Contract:
    POST /api/telemetry/readings { "deviceId": "hvac-01", "timestamp": "...", "powerKw": 42.5, "voltage": 230, "current": 185, "powerFactor": 0.94 }
    Validates range limits, quality tags, and persists to time-series storage.
    """
    raw_dict = reading_in.model_dump()
    cleaned_dict, quality, note = TelemetryCleaner.clean_and_tag(raw_dict)
    cleaned_dict["quality"] = quality

    repo = TelemetryRepository(db)
    reading = repo.insert_reading(cleaned_dict)

    return {
        "success": True,
        "data": {
            "id": reading.id,
            "deviceId": reading.device_id,
            "timestamp": reading.timestamp.isoformat() + "Z",
            "powerKw": reading.power_kw,
            "energyKwh": reading.energy_kwh,
            "voltage": reading.voltage,
            "current": reading.current,
            "powerFactor": reading.power_factor,
            "quality": reading.quality
        },
        "meta": {
            "isSimulated": True,
            "note": note
        }
    }

@router.get("/live")
def get_live_telemetry(db: Session = Depends(get_db)):
    """Returns the latest live telemetry reading for all active campus devices."""
    repo = TelemetryRepository(db)
    readings = repo.get_latest_readings_all_devices()
    site_aggregates = repo.get_total_live_load()

    return {
        "success": True,
        "data": {
            "devices": readings,
            "aggregates": site_aggregates
        },
        "meta": {
            "dataSource": "ESP32_MQTT_OR_SIMULATOR",
            "isSimulated": True,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
    }

@router.get("/history")
def get_telemetry_history(
    deviceId: str = Query(None, description="Optional filter by device ID"),
    limit: int = Query(60, ge=5, le=500),
    db: Session = Depends(get_db)
):
    repo = TelemetryRepository(db)
    records = repo.get_recent_history(deviceId, limit=limit)
    
    return {
        "success": True,
        "data": [
            {
                "id": r.id,
                "deviceId": r.device_id,
                "timestamp": r.timestamp.isoformat() + "Z",
                "powerKw": r.power_kw,
                "energyKwh": r.energy_kwh,
                "voltage": r.voltage,
                "current": r.current,
                "powerFactor": r.power_factor,
                "quality": r.quality
            }
            for r in reversed(records)
        ],
        "meta": {"count": len(records), "isSimulated": True}
    }
