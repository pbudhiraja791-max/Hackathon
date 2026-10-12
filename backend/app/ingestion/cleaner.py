from typing import Tuple, Dict, Any, Optional
import datetime

class TelemetryCleaner:
    """
    Validates, smooths, and tags telemetry packets entering the Fluxora ingestion pipeline.
    Ensures impossible physics/sensor faults are caught before persistence.
    """

    VOLTAGE_MIN = 160.0
    VOLTAGE_MAX = 290.0
    POWER_KW_MAX = 1500.0
    CURRENT_MAX = 800.0
    PF_MIN = 0.50
    PF_MAX = 1.00

    @classmethod
    def clean_and_tag(
        cls, 
        reading_dict: Dict[str, Any], 
        prev_reading: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], str, Optional[str]]:
        """
        Returns:
            (cleaned_reading, quality_flag, error_or_warning_message)
        """
        cleaned = reading_dict.copy()
        quality = "GOOD"
        note = None

        # 1. Parse / normalize timestamp
        ts = cleaned.get("timestamp")
        if not ts:
            cleaned["timestamp"] = datetime.datetime.utcnow()
        elif isinstance(ts, str):
            try:
                cleaned["timestamp"] = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                cleaned["timestamp"] = datetime.datetime.utcnow()
                quality = "ESTIMATED"
                note = "Invalid timestamp parsed; defaulted to UTC now"

        # 2. Voltage range check
        voltage = float(cleaned.get("voltage", 230.0))
        if voltage < cls.VOLTAGE_MIN or voltage > cls.VOLTAGE_MAX:
            quality = "OUT_OF_RANGE"
            note = f"Voltage {voltage}V outside safe limits ({cls.VOLTAGE_MIN}-{cls.VOLTAGE_MAX}V)"
            voltage = max(cls.VOLTAGE_MIN, min(cls.VOLTAGE_MAX, voltage))
        cleaned["voltage"] = voltage

        # 3. Power Kw check
        power_kw = float(cleaned.get("powerKw", 0.0))
        if power_kw < 0.0:
            power_kw = 0.0
            quality = "ANOMALOUS"
            note = "Negative power encountered; clamped to 0"
        elif power_kw > cls.POWER_KW_MAX:
            power_kw = cls.POWER_KW_MAX
            quality = "OUT_OF_RANGE"
            note = f"Power {power_kw}kW exceeded upper sensor boundary"
        cleaned["powerKw"] = power_kw

        # 4. Power Factor validation
        pf = float(cleaned.get("powerFactor", 0.95))
        if pf < cls.PF_MIN or pf > cls.PF_MAX:
            pf = 0.95
            quality = "ESTIMATED" if quality == "GOOD" else quality
            note = f"Power factor {pf} abnormal; fallback to 0.95 applied"
        cleaned["powerFactor"] = pf

        # 5. Current validation or calculation (I ~ P / (V * PF))
        current = float(cleaned.get("current", 0.0))
        if current <= 0.0 and cleaned["powerKw"] > 0:
            denom = max(1.0, cleaned["voltage"] * cleaned["powerFactor"])
            current = round((cleaned["powerKw"] * 1000.0) / denom, 2)
            quality = "ESTIMATED" if quality == "GOOD" else quality
        cleaned["current"] = current

        # 6. Energy Accumulation (kWh = P * dt)
        if prev_reading and prev_reading.get("timestamp"):
            dt_seconds = (cleaned["timestamp"] - prev_reading["timestamp"]).total_seconds()
            if 0 < dt_seconds <= 86400:
                hours = dt_seconds / 3600.0
                incremental_kwh = cleaned["powerKw"] * hours
                cleaned["energyKwh"] = round(prev_reading.get("energyKwh", 0.0) + incremental_kwh, 4)
            else:
                cleaned["energyKwh"] = prev_reading.get("energyKwh", 0.0)
        elif "energyKwh" not in cleaned or cleaned["energyKwh"] is None:
            cleaned["energyKwh"] = 0.0

        return cleaned, quality, note
