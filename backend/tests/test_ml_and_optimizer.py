import datetime
import pytest
from app.ml.features import FeatureEngineer
from app.ml.forecaster import DemandForecaster
from app.ml.anomaly import AnomalyDetector
from app.optimization.optimizer import ConstrainedEnergyOptimizer

def test_feature_engineering():
    ts = datetime.datetime(2026, 10, 12, 14, 30) # Monday 14:30
    feats = FeatureEngineer.extract_time_features(ts)
    assert feats["is_weekend"] == 0.0
    assert feats["occupancy_proxy"] > 0.70
    assert feats["temperature_ambient"] > 25.0

def test_forecasting_appendix_b():
    forecast = DemandForecaster.generate_forecast(horizon_hours=24, recent_load_kw=190.0)
    assert forecast["model"] == "xgboost"
    assert forecast["version"] == "forecast-v1"
    assert len(forecast["points"]) == 24
    assert forecast["peakPredictedKw"] > 0
    assert "predictedKw" in forecast["points"][0]

def test_anomaly_detection_appendix_c():
    detector = AnomalyDetector()
    # Normal operation
    norm = detector.evaluate_reading(device_id="hvac-01", observed_kw=28.5, baseline_kw=28.0, power_factor=0.95, hour=14)
    assert norm is None

    # Degradation/High spike
    anomaly = detector.evaluate_reading(device_id="hvac-01", observed_kw=55.0, baseline_kw=28.0, power_factor=0.78, hour=18)
    assert anomaly is not None
    assert anomaly["deviceId"] == "hvac-01"
    assert anomaly["severity"] in ["high", "critical"]
    assert "evidence" in anomaly
    assert anomaly["evidence"]["observedKw"] == 55.0

def test_constrained_optimizer_appendix_d():
    res = ConstrainedEnergyOptimizer.solve(forecast_peak_kw=215.0, battery_soc_percent=78.0)
    assert res["objective"] == "minimize_cost_and_peak"
    assert len(res["actions"]) > 0
    assert res["estimatedImpact"]["costAvoided"] > 0
    assert res["estimatedImpact"]["peakReductionKw"] > 0
    assert len(res["constraints"]) > 0
