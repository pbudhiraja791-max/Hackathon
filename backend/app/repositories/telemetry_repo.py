import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.models import Reading, Device

class TelemetryRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert_reading(self, reading_dict: Dict[str, Any]) -> Reading:
        reading = Reading(
            device_id=reading_dict["deviceId"],
            timestamp=reading_dict["timestamp"],
            power_kw=reading_dict["powerKw"],
            energy_kwh=reading_dict.get("energyKwh", 0.0),
            voltage=reading_dict.get("voltage", 230.0),
            current=reading_dict.get("current", 0.0),
            power_factor=reading_dict.get("powerFactor", 0.95),
            frequency=reading_dict.get("frequency", 50.0),
            quality=reading_dict.get("quality", "GOOD")
        )
        self.db.add(reading)
        
        # Also update current device power and last_seen
        device = self.db.query(Device).filter_by(id=reading_dict["deviceId"]).first()
        if device:
            device.current_power_kw = reading_dict["powerKw"]
            device.last_seen = reading_dict["timestamp"]
            device.today_energy_kwh = reading_dict.get("energyKwh", device.today_energy_kwh)

        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_latest_readings_all_devices(self) -> List[Dict[str, Any]]:
        devices = self.db.query(Device).all()
        result = []
        for dev in devices:
            latest = (
                self.db.query(Reading)
                .filter_by(device_id=dev.id)
                .order_by(desc(Reading.timestamp))
                .first()
            )
            if latest:
                result.append({
                    "deviceId": dev.id,
                    "name": dev.name,
                    "deviceType": dev.device_type,
                    "powerKw": latest.power_kw,
                    "energyKwh": latest.energy_kwh,
                    "voltage": latest.voltage,
                    "current": latest.current,
                    "powerFactor": latest.power_factor,
                    "frequency": latest.frequency,
                    "quality": latest.quality,
                    "timestamp": latest.timestamp.isoformat() + "Z",
                    "status": dev.status,
                    "controllable": dev.controllable,
                    "isSimulated": dev.is_simulated
                })
            else:
                result.append({
                    "deviceId": dev.id,
                    "name": dev.name,
                    "deviceType": dev.device_type,
                    "powerKw": dev.current_power_kw,
                    "energyKwh": dev.today_energy_kwh,
                    "voltage": 230.0,
                    "current": 0.0,
                    "powerFactor": 0.95,
                    "frequency": 50.0,
                    "quality": "GOOD",
                    "timestamp": dev.last_seen.isoformat() + "Z",
                    "status": dev.status,
                    "controllable": dev.controllable,
                    "isSimulated": dev.is_simulated
                })
        return result

    def get_recent_history(self, device_id: Optional[str] = None, limit: int = 100) -> List[Reading]:
        query = self.db.query(Reading)
        if device_id:
            query = query.filter_by(device_id=device_id)
        return query.order_by(desc(Reading.timestamp)).limit(limit).all()

    def get_total_live_load(self) -> Dict[str, float]:
        """Calculates total grid draw, solar generation, and net power."""
        devices = self.db.query(Device).all()
        total_load = 0.0
        solar_gen = 0.0
        battery_discharge = 0.0

        for dev in devices:
            if dev.device_type == "solar_inverter":
                solar_gen += dev.current_power_kw
            elif dev.device_type == "battery":
                # If battery power is active and state is discharging
                if dev.device_metadata and dev.device_metadata.get("state") == "discharging":
                    battery_discharge += dev.current_power_kw
            else:
                total_load += dev.current_power_kw

        grid_draw = max(0.0, total_load - solar_gen - battery_discharge)
        return {
            "totalLoadKw": round(total_load, 2),
            "solarGenerationKw": round(solar_gen, 2),
            "batteryDischargeKw": round(battery_discharge, 2),
            "gridImportKw": round(grid_draw, 2)
        }
