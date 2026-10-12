import datetime
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    """
    Isolation Forest Anomaly Detection engine conforming to Appendix C specification.
    Detects power spikes, phantom night idle loads, and equipment degradation patterns.
    """

    MODEL_VERSION = "isolation-forest-v1.2"

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        # Train baseline model on standard profile space
        self.model = IsolationForest(
            n_estimators=100, 
            contamination=contamination, 
            random_state=42
        )
        self._fit_synthetic_reference_distribution()

    def _fit_synthetic_reference_distribution(self):
        """Fit reference distribution on normal operating power, power factor, and time-of-day."""
        # Feature vector: [power_ratio, power_factor, hour_norm]
        rng = np.random.RandomState(42)
        normal_samples = []
        for _ in range(500):
            # Normal: power_ratio around 0.6 - 0.9, pf around 0.92 - 0.98, hour 0-23
            hr = rng.uniform(0, 24)
            pf = rng.uniform(0.91, 0.98)
            ratio = rng.uniform(0.4, 0.85)
            normal_samples.append([ratio, pf, hr / 24.0])
        
        self.model.fit(np.array(normal_samples))

    def evaluate_reading(
        self,
        device_id: str,
        observed_kw: float,
        baseline_kw: float,
        power_factor: float = 0.95,
        hour: int = 12,
        duration_minutes: int = 15
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates a device telemetry reading against expected baseline.
        Returns Appendix C compliant anomaly dict if an anomaly is detected.
        """
        baseline_kw = max(0.5, baseline_kw)
        ratio = observed_kw / baseline_kw
        sample = np.array([[ratio, power_factor, hour / 24.0]])
        
        # Isolation Forest score: lower (negative) is more anomalous. 
        # We transform to 0.0 - 1.0 confidence score where 1.0 is highest anomaly.
        raw_score = self.model.decision_function(sample)[0]
        anomaly_score = float(1.0 / (1.0 + np.exp(raw_score * 4.0)))

        # Also apply domain heuristic thresholds to prevent false positives
        is_spike = ratio > 1.35 and (observed_kw - baseline_kw) > 5.0
        is_phantom_night = (hour < 6 or hour > 22) and observed_kw > 15.0 and ratio > 1.8
        is_degradation = ratio > 1.25 and power_factor < 0.82

        is_anomalous = (anomaly_score > 0.65) or is_spike or is_phantom_night or is_degradation

        if not is_anomalous:
            return None

        # Determine severity
        if anomaly_score > 0.88 or ratio > 1.6:
            severity = "critical"
        elif anomaly_score > 0.75 or ratio > 1.35:
            severity = "high"
        elif anomaly_score > 0.60:
            severity = "medium"
        else:
            severity = "low"

        # Categorize specific alert type
        alert_type = "abnormal_load"
        if is_phantom_night:
            alert_type = "phantom_night_load"
        elif is_degradation:
            alert_type = "device_degradation"
        elif is_spike:
            alert_type = "peak_risk"

        now_iso = datetime.datetime.utcnow().isoformat() + "Z"

        return {
            "deviceId": device_id,
            "score": round(min(0.99, max(0.51, anomaly_score)), 2),
            "severity": severity,
            "alertType": alert_type,
            "detectedAt": now_iso,
            "evidence": {
                "baselineKw": round(baseline_kw, 1),
                "observedKw": round(observed_kw, 1),
                "durationMinutes": duration_minutes,
                "deviationPercent": round(((observed_kw - baseline_kw) / baseline_kw) * 100, 1)
            }
        }
