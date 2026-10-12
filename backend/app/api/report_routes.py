from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.telemetry_repo import TelemetryRepository
from app.repositories.app_repo import AppRepository
from app.services.savings_service import SavingsVerificationService
from app.core.config import settings
import datetime

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/daily")
def get_daily_executive_report(db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    readings = repo.get_latest_readings_all_devices()
    savings = SavingsVerificationService.get_savings_summary(verified=True)

    total_kwh = sum(r["energyKwh"] for r in readings if r["deviceType"] not in ["solar_inverter", "battery"])
    solar_kwh = next((r["energyKwh"] for r in readings if r["deviceId"] == "solar-01"), 184.5)

    return {
        "success": True,
        "data": {
            "reportTitle": "Fluxora Daily Facility Energy & Carbon Performance",
            "date": datetime.date.today().isoformat(),
            "site": "Fluxora Innovation Tech Park",
            "totalConsumptionKwh": round(total_kwh, 1),
            "solarGenerationKwh": round(solar_kwh, 1),
            "renewableSharePercent": round((solar_kwh / max(1.0, total_kwh)) * 100, 1),
            "peakDemandKw": 218.4,
            "costTodayInr": round(total_kwh * 8.20, 2),
            "costAvoidedInr": savings["costAvoided"],
            "carbonAvoidedKg": savings["carbonSavedKg"],
            "alertsHandled": 4,
            "actionsExecuted": 3
        },
        "meta": {"status": "verified_daily_summary", "isSimulated": True}
    }

@router.get("/monthly")
def get_monthly_executive_report(db: Session = Depends(get_db)):
    return {
        "success": True,
        "data": {
            "reportTitle": "Fluxora Monthly Energy & Decarbonization Audit",
            "month": "October 2026",
            "totalEnergyMwh": 38.4,
            "solarGeneratedMwh": 6.8,
            "totalCostInr": 314880.0,
            "totalSavingsVerifiedInr": 48250.0,
            "carbonOffsetTonnes": 4.87,
            "topConsumingDevices": [
                {"name": "Main Chiller Plant HVAC", "share": "46.2%", "energyKwh": 17740},
                {"name": "Server Room Precision AC", "share": "28.5%", "energyKwh": 10940},
                {"name": "Campus LED Lighting", "share": "14.1%", "energyKwh": 5410},
                {"name": "Primary Water Pump", "share": "7.2%", "energyKwh": 2760}
            ]
        },
        "meta": {"status": "monthly_audit", "isSimulated": True}
    }

@router.get("/export/csv")
def export_csv_report(db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    readings = repo.get_latest_readings_all_devices()
    
    csv_lines = ["DeviceId,DeviceName,DeviceType,PowerKw,EnergyKwh,Voltage,Current,PowerFactor,Quality,Status,DataMode\n"]
    for r in readings:
        csv_lines.append(f"{r['deviceId']},{r['name']},{r['deviceType']},{r['powerKw']},{r['energyKwh']},{r['voltage']},{r['current']},{r['powerFactor']},{r['quality']},{r['status']},SIMULATED\n")
    
    csv_content = "".join(csv_lines)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fluxora_telemetry_report.csv"}
    )
