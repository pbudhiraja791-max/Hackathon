from fastapi import APIRouter
from app.schemas.schemas import HealthResponse
import datetime

router = APIRouter(prefix="/api/health", tags=["Health & Observability"])

@router.get("", response_model=HealthResponse)
def get_health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.datetime.utcnow(),
        "services": {
            "api": "online",
            "database": "online",
            "telemetryIngestion": "online",
            "mlForecaster": "online",
            "isolationForest": "online",
            "constrainedOptimizer": "online",
            "simulator": "online"
        }
    }
