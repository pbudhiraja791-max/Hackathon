from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.telemetry_repo import TelemetryRepository
from app.ml.forecaster import DemandForecaster

router = APIRouter(prefix="/api/forecast", tags=["Forecasting"])

@router.get("")
def get_forecast(
    horizonHours: int = Query(24, ge=12, le=48),
    db: Session = Depends(get_db)
):
    """
    Appendix B Contract:
    { "model": "xgboost", "version": "forecast-v1", "horizonHours": 24, "points": [
      {"timestamp": "2026-10-03T00:00:00Z", "predictedKw": 210.4} ] }
    Forecast values must never be silently mixed into measured telemetry.
    """
    repo = TelemetryRepository(db)
    live_load = repo.get_total_live_load()["totalLoadKw"]

    forecast_data = DemandForecaster.generate_forecast(
        horizon_hours=horizonHours,
        recent_load_kw=live_load
    )

    return {
        "success": True,
        "data": forecast_data,
        "meta": {
            "isSimulated": True,
            "disclaimer": "Forecast is model-generated using XGBoost/diurnal features. Clearly separated from measured historical telemetry."
        }
    }
