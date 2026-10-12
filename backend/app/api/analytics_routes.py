from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.repositories.telemetry_repo import TelemetryRepository
from app.services.tariff_service import TariffService
import datetime

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/load")
def get_load_breakdown(db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    agg = repo.get_total_live_load()
    return {
        "success": True,
        "data": agg,
        "meta": {"unit": "kW", "isSimulated": True}
    }

@router.get("/cost")
def get_cost_analytics(db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    devices = repo.get_latest_readings_all_devices()
    total_kwh_today = sum(d["energyKwh"] for d in devices if d["deviceType"] not in ["solar_inverter", "battery"])
    
    # Blended commercial tariff rate
    now = datetime.datetime.utcnow()
    current_rate, period = TariffService.get_rate_for_hour(now.hour)
    estimated_cost_today = total_kwh_today * 8.20 # Blended average rate

    return {
        "success": True,
        "data": {
            "totalEnergyTodayKwh": round(total_kwh_today, 2),
            "estimatedCostTodayInr": round(estimated_cost_today, 2),
            "currentRateInr": current_rate,
            "currentPeriod": period,
            "currency": settings.DEFAULT_CURRENCY,
            "tariffVersion": TariffService.TARIFF_VERSION
        },
        "meta": {"isSimulated": True, "note": "Estimated cost calculated from TOU rate schedule"}
    }

@router.get("/sources")
def get_energy_sources(db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    readings = repo.get_latest_readings_all_devices()
    
    solar_kw = next((d["powerKw"] for d in readings if d["deviceId"] == "solar-01"), 0.0)
    battery_kw = next((d["powerKw"] for d in readings if d["deviceId"] == "battery-01"), 0.0)
    grid_kw = repo.get_total_live_load()["gridImportKw"]
    total = max(0.1, solar_kw + battery_kw + grid_kw)

    return {
        "success": True,
        "data": {
            "gridImportKw": grid_kw,
            "solarGenerationKw": solar_kw,
            "batteryDischargeKw": battery_kw,
            "gridSharePercent": round((grid_kw / total) * 100, 1),
            "solarSharePercent": round((solar_kw / total) * 100, 1),
            "batterySharePercent": round((battery_kw / total) * 100, 1)
        },
        "meta": {"unit": "kW", "isSimulated": True}
    }

@router.get("/peak")
def get_peak_demand_analytics(db: Session = Depends(get_db)):
    return {
        "success": True,
        "data": {
            "contractDemandKva": 250.0,
            "todayPeakKw": 218.4,
            "peakTimestamp": "2026-10-12T17:45:00Z",
            "thresholdWarningKw": 210.0,
            "demandChargeRateInr": settings.DEMAND_CHARGE_PER_KW,
            "projectedMonthlyDemandChargeInr": round(218.4 * settings.DEMAND_CHARGE_PER_KW, 2)
        },
        "meta": {"isSimulated": True}
    }

@router.get("/carbon")
def get_carbon_analytics(db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    readings = repo.get_latest_readings_all_devices()
    solar_today_kwh = next((d["energyKwh"] for d in readings if d["deviceId"] == "solar-01"), 184.5)
    
    co2_avoided_kg = round(solar_today_kwh * settings.CO2_KG_PER_KWH, 2)
    trees_equivalent = round(co2_avoided_kg / 21.0, 1) # ~21 kg CO2 absorbed per tree per year

    return {
        "success": True,
        "data": {
            "gridEmissionFactor": settings.CO2_KG_PER_KWH,
            "solarCleanEnergyTodayKwh": round(solar_today_kwh, 2),
            "co2AvoidedTodayKg": co2_avoided_kg,
            "treesEquivalentAnnual": trees_equivalent
        },
        "meta": {"isSimulated": True}
    }
