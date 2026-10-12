import datetime
from typing import Dict, Any, Tuple
from app.core.config import settings

class TariffService:
    """
    Computes Time-of-Use (TOU) energy costs and demand charges.
    Rates defined per FY-2026 Commercial Grid Tariff:
    - Peak: 17:00 - 21:00 (₹12.50/kWh)
    - Off-Peak: 22:00 - 06:00 (₹5.50/kWh)
    - Normal: 06:00 - 17:00 & 21:00 - 22:00 (₹8.00/kWh)
    """

    TARIFF_VERSION = "TOU-COMMERCIAL-V2026.1"

    @classmethod
    def get_rate_for_hour(cls, hour: int) -> Tuple[float, str]:
        if 17 <= hour < 21:
            return settings.TARIFF_PEAK, "PEAK"
        elif hour >= 22 or hour < 6:
            return settings.TARIFF_OFF_PEAK, "OFF_PEAK"
        else:
            return settings.TARIFF_NORMAL, "NORMAL"

    @classmethod
    def calculate_cost_for_reading(cls, power_kw: float, duration_hours: float, timestamp: datetime.datetime) -> Dict[str, Any]:
        kwh = power_kw * duration_hours
        rate, period_type = cls.get_rate_for_hour(timestamp.hour)
        cost_inr = kwh * rate
        co2_kg = kwh * settings.CO2_KG_PER_KWH

        return {
            "kwh": round(kwh, 4),
            "rateInr": rate,
            "periodType": period_type,
            "costInr": round(cost_inr, 2),
            "co2Kg": round(co2_kg, 3),
            "tariffVersion": cls.TARIFF_VERSION
        }

    @classmethod
    def calculate_peak_demand_charge(cls, peak_kw: float) -> float:
        return round(peak_kw * settings.DEMAND_CHARGE_PER_KW, 2)
