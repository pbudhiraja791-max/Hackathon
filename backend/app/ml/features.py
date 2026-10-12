import math
import datetime
from typing import Dict, Any, List

class FeatureEngineer:
    """
    Transforms timestamp and historical load profiles into rich feature representations
    for forecasting and Isolation Forest anomaly detection.
    """

    @staticmethod
    def extract_time_features(ts: datetime.datetime) -> Dict[str, float]:
        hour = ts.hour + ts.minute / 60.0
        day_of_week = ts.weekday() # 0 = Monday, 6 = Sunday
        is_weekend = 1.0 if day_of_week >= 5 else 0.0

        # Sinusoidal encodings for smooth periodic behavior
        sin_hour = math.sin(2 * math.pi * hour / 24.0)
        cos_hour = math.cos(2 * math.pi * hour / 24.0)
        sin_day = math.sin(2 * math.pi * day_of_week / 7.0)
        cos_day = math.cos(2 * math.pi * day_of_week / 7.0)

        # Campus occupancy proxy (0.0 to 1.0)
        if is_weekend:
            occupancy = 0.12 + 0.08 * math.sin(math.pi * max(0.0, min(1.0, (hour - 10) / 8.0)))
        else:
            if 8.5 <= hour <= 18.5:
                # Active operating hours
                occupancy = 0.75 + 0.25 * math.sin(math.pi * (hour - 8.5) / 10.0)
            elif 6.0 <= hour < 8.5:
                occupancy = 0.20 + 0.55 * (hour - 6.0) / 2.5
            elif 18.5 < hour <= 21.0:
                occupancy = 0.75 - 0.50 * (hour - 18.5) / 2.5
            else:
                occupancy = 0.10

        # Weather / outdoor ambient temperature proxy (°C)
        # Low at 05:00 ~ 23°C, peak at 14:00 ~ 34°C
        temp_ambient = 28.5 + 5.5 * math.sin(2 * math.pi * (hour - 8.0) / 24.0)

        return {
            "hour": hour,
            "day_of_week": float(day_of_week),
            "is_weekend": is_weekend,
            "sin_hour": sin_hour,
            "cos_hour": cos_hour,
            "sin_day": sin_day,
            "cos_day": cos_day,
            "occupancy_proxy": round(occupancy, 3),
            "temperature_ambient": round(temp_ambient, 2)
        }

    @classmethod
    def create_feature_vector(
        cls, 
        ts: datetime.datetime, 
        lag_1h: float, 
        lag_24h: float, 
        rolling_mean_6h: float, 
        rolling_std_6h: float
    ) -> List[float]:
        t_feats = cls.extract_time_features(ts)
        return [
            t_feats["sin_hour"],
            t_feats["cos_hour"],
            t_feats["sin_day"],
            t_feats["cos_day"],
            t_feats["is_weekend"],
            t_feats["occupancy_proxy"],
            t_feats["temperature_ambient"],
            lag_1h,
            lag_24h,
            rolling_mean_6h,
            rolling_std_6h
        ]
