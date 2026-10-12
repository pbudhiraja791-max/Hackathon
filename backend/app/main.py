import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.repositories.app_repo import AppRepository
from app.repositories.telemetry_repo import TelemetryRepository
from app.ingestion.cleaner import TelemetryCleaner
from app.simulator.campus_simulator import simulator_engine

# Import routers
from app.api.auth_routes import router as auth_router
from app.api.telemetry_routes import router as telemetry_router
from app.api.device_routes import router as device_router
from app.api.analytics_routes import router as analytics_router
from app.api.forecast_routes import router as forecast_router
from app.api.anomaly_routes import router as anomaly_router
from app.api.optimization_routes import router as optimization_router
from app.api.savings_routes import router as savings_router
from app.api.report_routes import router as report_router
from app.api.simulator_routes import router as simulator_router
from app.api.health_routes import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fluxora")

# Simulator background worker
async def background_simulator_worker():
    """Background task generating periodic campus sensor telemetry."""
    while True:
        try:
            db = SessionLocal()
            try:
                repo = TelemetryRepository(db)
                readings = simulator_engine.generate_snapshot()
                for r in readings:
                    cleaned, quality, _ = TelemetryCleaner.clean_and_tag(r)
                    cleaned["quality"] = quality
                    repo.insert_reading(cleaned)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Simulator worker exception: {e}")
        await asyncio.sleep(settings.SIMULATION_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed initial data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        app_repo = AppRepository(db)
        app_repo.seed_initial_data()
        
        # Initial simulation snapshot seed
        telemetry_repo = TelemetryRepository(db)
        initial_readings = simulator_engine.generate_snapshot()
        for r in initial_readings:
            cleaned, quality, _ = TelemetryCleaner.clean_and_tag(r)
            cleaned["quality"] = quality
            telemetry_repo.insert_reading(cleaned)
    finally:
        db.close()

    # Start simulator task
    worker_task = asyncio.create_task(background_simulator_worker())
    yield
    # Shutdown
    worker_task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Fluxora — Smarter Energy for a Sustainable Tomorrow. PS08 Full-Stack Energy Management System.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(telemetry_router)
app.include_router(device_router)
app.include_router(analytics_router)
app.include_router(forecast_router)
app.include_router(anomaly_router)
app.include_router(optimization_router)
app.include_router(savings_router)
app.include_router(report_router)
app.include_router(simulator_router)
app.include_router(health_router)

@app.get("/")
def get_root():
    return {
        "brand": settings.PROJECT_NAME,
        "headline": settings.HEADLINE,
        "problemStatement": "PS08 — Energy for the Next Billion",
        "status": "operational",
        "apiDocs": "/docs",
        "tenStageWorkflow": [
            "1. Sense (ESP32/CT Meters)",
            "2. Stream (MQTT/HTTP)",
            "3. Store (Time Series)",
            "4. Clean (Range Validation & Quality Tagging)",
            "5. Learn (Feature Engineering & Diurnal Baselines)",
            "6. Optimize (Constrained LP & Battery/EV Dispatch)",
            "7. Recommend (Prescriptive Alerts with Financial Impact)",
            "8. Act (Human-in-the-Loop Operator Approval & BMS)",
            "9. Measure (Savings Verification vs Baseline)",
            "10. Feedback (Audit Ground Truth & Model Tuning)"
        ]
    }
