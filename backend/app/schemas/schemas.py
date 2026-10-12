from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
import datetime

# --- Generic API Envelope ---
class ApiResponse(BaseModel):
    success: bool = True
    data: Any
    meta: Optional[Dict[str, Any]] = None

# --- User & Auth ---
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "operator"

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime.datetime

# --- Appendix A: Telemetry Reading ---
class TelemetryReadingCreate(BaseModel):
    deviceId: str = Field(..., description="Device ID e.g. hvac-01")
    timestamp: Optional[datetime.datetime] = Field(default_factory=datetime.datetime.utcnow)
    powerKw: float = Field(..., ge=0.0, le=2000.0)
    voltage: Optional[float] = Field(230.0, ge=160.0, le=300.0)
    current: Optional[float] = Field(0.0, ge=0.0, le=1000.0)
    powerFactor: Optional[float] = Field(0.95, ge=0.5, le=1.0)
    frequency: Optional[float] = Field(50.0, ge=45.0, le=65.0)
    energyKwh: Optional[float] = Field(0.0, ge=0.0)

class TelemetryReadingOut(BaseModel):
    id: int
    deviceId: str
    timestamp: datetime.datetime
    powerKw: float
    energyKwh: float
    voltage: float
    current: float
    powerFactor: float
    frequency: float
    quality: str

# --- Devices ---
class DeviceCommand(BaseModel):
    command: str = Field(..., description="E.g. SET_POWER, SET_SETPOINT, DISCHARGE, CHARGE, SHIFT")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    actor: Optional[str] = "operator@fluxora.local"

class DeviceOut(BaseModel):
    id: str
    name: str
    device_type: str
    zone_id: Optional[str] = None
    rated_power_kw: float
    current_power_kw: float
    today_energy_kwh: float
    controllable: bool
    status: str
    is_simulated: bool
    last_seen: datetime.datetime
    device_metadata: Dict[str, Any] = {}

# --- Appendix B: Forecast Output ---
class ForecastPoint(BaseModel):
    timestamp: datetime.datetime
    predictedKw: float
    baselineKw: Optional[float] = None
    isPeak: Optional[bool] = False

class ForecastResponse(BaseModel):
    model: str = "xgboost"
    version: str = "forecast-v1"
    horizonHours: int = 24
    generatedAt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    points: List[ForecastPoint]
    peakPredictedKw: float
    peakTimestamp: datetime.datetime
    modelAccuracyMape: float = 4.8  # Labeled model metric

# --- Appendix C: Anomaly Output ---
class AnomalyEvidence(BaseModel):
    baselineKw: float
    observedKw: float
    durationMinutes: int
    deviationPercent: Optional[float] = None

class AnomalyItem(BaseModel):
    id: Optional[str] = None
    deviceId: str
    score: float  # Isolation forest score (0.0 - 1.0)
    severity: str # critical, high, medium, low
    detectedAt: datetime.datetime
    alertType: str = "abnormal_load"
    status: str = "open"
    evidence: AnomalyEvidence
    recommendedAction: Optional[str] = None

# --- Appendix D: Optimization Output ---
class OptimizationAction(BaseModel):
    deviceId: str
    action: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    targetKwh: Optional[float] = None
    energyKwh: Optional[float] = None
    powerKw: Optional[float] = None
    reason: Optional[str] = None

class OptimizationImpact(BaseModel):
    costAvoided: float
    peakReductionKw: float
    kwhShifted: float
    carbonReductionKg: float

class OptimizationRunResponse(BaseModel):
    objective: str = "minimize_cost_and_peak"
    actions: List[OptimizationAction]
    estimatedImpact: OptimizationImpact
    constraints: List[str]
    solver: str = "constrained_lp_scheduler_v1"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# --- Appendix E: Savings Output ---
class SavingsVerificationResponse(BaseModel):
    status: str = Field(..., description="estimated, measured, or verified")
    baselineKwh: float
    actualKwh: float
    savingKwh: float
    costAvoided: float
    peakReductionKw: float
    carbonSavedKg: float
    method: str = "comparable_period_baseline"
    verificationPeriodDays: int = 7
    notes: Optional[str] = None

# --- Alerts & Recommendations ---
class AlertOut(BaseModel):
    id: str
    alert_type: str
    severity: str
    status: str
    source_id: str
    title: str
    message: str
    evidence: Dict[str, Any]
    created_at: datetime.datetime
    updated_at: datetime.datetime

class RecommendationOut(BaseModel):
    id: str
    priority: int
    title: str
    action: str
    reason: str
    target_device_id: Optional[str] = None
    estimated_impact: Dict[str, Any]
    status: str
    model_version: str
    created_at: datetime.datetime

# --- Health ---
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    services: Dict[str, str]
