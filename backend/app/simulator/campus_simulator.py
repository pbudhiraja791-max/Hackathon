import math
import random
import datetime
from typing import Dict, Any, List, Optional
from app.ingestion.cleaner import TelemetryCleaner

class CampusSimulator:
    """
    High-fidelity campus energy simulator.
    Simulates:
    - Main Chiller HVAC (hvac-01)
    - Server Room Precision AC (hvac-02)
    - Campus LED Lighting Grid (light-01)
    - Primary HVAC Chilled Water Pump (pump-01)
    - Rooftop Solar PV Inverter 50kW (solar-01)
    - Battery Energy Storage System 100kWh BESS (battery-01)
    - EV Fleet Charging Station (ev-01)
    - Cafeteria Cold Storage Unit (ref-01)

    Supports interactive scenario injection:
    - 'normal': Standard daily profile
    - 'peak_spike': Major cooling demand spike
    - 'phantom_night': Wasteful overnight lighting and equipment active
    - 'degradation': Equipment compressor fault (high power, poor power factor)
    - 'solar_surplus': High solar generation, zero grid export penalty

    Dynamically responds to BMS / Operator control commands:
    - Setpoint adjustment reduces HVAC power
    - Battery discharge command pushes negative net power to grid
    - EV shift suspends charging during peak hours
    """

    def __init__(self):
        self.scenario = "normal"
        self.battery_soc = 76.5       # Percent (0-100)
        self.battery_state = "idle"   # idle, charging, discharging
        self.battery_power_kw = 0.0   # Positive = discharging, negative = charging
        
        self.ev_charging = False
        self.ev_power_kw = 0.0
        self.ev_shifted = False

        self.hvac_setpoint = 23.0     # °C
        self.hvac_curtailed = False

        self.device_energy_counters = {
            "hvac-01": 218.4,
            "hvac-02": 142.1,
            "light-01": 56.8,
            "pump-01": 38.2,
            "solar-01": 184.5,
            "battery-01": 42.0,
            "ev-01": 34.0,
            "ref-01": 19.5
        }
        self.last_tick_time = datetime.datetime.utcnow()

    def set_scenario(self, scenario: str):
        valid = ["normal", "peak_spike", "phantom_night", "degradation", "solar_surplus", "sensor_offline"]
        if scenario in valid:
            self.scenario = scenario
            if scenario == "peak_spike":
                self.hvac_setpoint = 20.0
                self.hvac_curtailed = False
            elif scenario == "degradation":
                self.hvac_curtailed = False
            elif scenario == "solar_surplus":
                self.battery_state = "charging"
            return True
        return False

    def execute_command(self, device_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes operator control commands and updates simulator physics state.
        """
        command_upper = command.upper()

        if device_id == "battery-01":
            if "DISCHARGE" in command_upper:
                discharge_kw = float(params.get("powerKw", 30.0))
                self.battery_state = "discharging"
                self.battery_power_kw = discharge_kw
                return {"status": "executed", "message": f"BESS discharging at {discharge_kw} kW to shave grid peak"}
            elif "CHARGE" in command_upper:
                charge_kw = float(params.get("powerKw", 25.0))
                self.battery_state = "charging"
                self.battery_power_kw = -charge_kw
                return {"status": "executed", "message": f"BESS charging at {charge_kw} kW from solar/off-peak"}
            else:
                self.battery_state = "idle"
                self.battery_power_kw = 0.0
                return {"status": "executed", "message": "BESS set to idle standby"}

        elif device_id == "ev-01":
            if "SHIFT" in command_upper or "STOP" in command_upper or "SUSPEND" in command_upper:
                self.ev_charging = False
                self.ev_power_kw = 0.0
                self.ev_shifted = True
                return {"status": "executed", "message": "EV charging paused and shifted to off-peak 22:00 window"}
            elif "START" in command_upper or "RESUME" in command_upper:
                self.ev_charging = True
                self.ev_power_kw = 11.0
                self.ev_shifted = False
                return {"status": "executed", "message": "EV charging active at 11 kW"}

        elif device_id in ["hvac-01", "hvac-02"]:
            if "SETPOINT" in command_upper:
                new_sp = float(params.get("setpoint", 25.0))
                self.hvac_setpoint = new_sp
                self.hvac_curtailed = True
                return {"status": "executed", "message": f"HVAC setpoint adjusted to {new_sp}°C (power reduced)"}
            elif "CURTAIL" in command_upper:
                self.hvac_curtailed = True
                return {"status": "executed", "message": "HVAC chilled water supply curtailed by 20%"}
            elif "RESET" in command_upper:
                self.hvac_setpoint = 23.0
                self.hvac_curtailed = False
                return {"status": "executed", "message": "HVAC reset to standard automatic schedule"}

        elif device_id == "light-01":
            if "DIM" in command_upper or "OFF" in command_upper:
                return {"status": "executed", "message": "Campus lighting dimmed to 40% daylight harvest level"}

        return {"status": "executed", "message": f"Command {command} executed successfully"}

    def generate_snapshot(self) -> List[Dict[str, Any]]:
        """
        Produces clean, physics-sound telemetry readings for all 8 campus devices.
        """
        now = datetime.datetime.utcnow()
        dt_seconds = (now - self.last_tick_time).total_seconds()
        dt_seconds = max(1.0, min(60.0, dt_seconds))
        self.last_tick_time = now
        dt_hours = dt_seconds / 3600.0

        hour = now.hour + now.minute / 60.0
        readings = []

        # --- 1. Solar PV Inverter (solar-01) ---
        # Sunlight curve between 06:00 and 18:30, peak at 12:30
        if 6.0 <= hour <= 18.5:
            solar_norm = math.sin(math.pi * (hour - 6.0) / 12.5)
            cloud_noise = random.uniform(0.92, 1.05)
            solar_kw = round(max(0.0, 48.0 * solar_norm * cloud_noise), 2)
            if self.scenario == "solar_surplus":
                solar_kw = round(solar_kw * 1.25, 2)
        else:
            solar_kw = 0.0

        self.device_energy_counters["solar-01"] += solar_kw * dt_hours
        readings.append({
            "deviceId": "solar-01",
            "timestamp": now,
            "powerKw": solar_kw,
            "energyKwh": round(self.device_energy_counters["solar-01"], 2),
            "voltage": round(231.0 + random.uniform(-1.5, 1.5), 1),
            "current": round((solar_kw * 1000.0) / (230.0 * 0.98), 1) if solar_kw > 0 else 0.0,
            "powerFactor": 0.98,
            "frequency": round(50.0 + random.uniform(-0.04, 0.04), 2),
            "quality": "GOOD"
        })

        # --- 2. BESS Battery Storage (battery-01) ---
        if self.battery_state == "discharging":
            b_kw = self.battery_power_kw
            self.battery_soc = max(18.0, self.battery_soc - (b_kw * dt_hours / 1.0))
        elif self.battery_state == "charging":
            b_kw = -25.0
            self.battery_soc = min(98.0, self.battery_soc + (25.0 * dt_hours / 1.0))
        else:
            b_kw = 0.0

        self.device_energy_counters["battery-01"] += abs(b_kw) * dt_hours
        readings.append({
            "deviceId": "battery-01",
            "timestamp": now,
            "powerKw": round(abs(b_kw), 2),
            "energyKwh": round(self.device_energy_counters["battery-01"], 2),
            "voltage": 230.0,
            "current": round((abs(b_kw) * 1000.0) / (230.0 * 0.99), 1) if abs(b_kw) > 0 else 0.0,
            "powerFactor": 0.99,
            "frequency": 50.0,
            "quality": "GOOD"
        })

        # --- 3. Main Chiller HVAC (hvac-01) ---
        base_hvac = 28.0 + 14.0 * math.sin(math.pi * max(0.0, min(1.0, (hour - 8.0) / 11.0)))
        if self.scenario == "peak_spike":
            base_hvac = 54.5 # High spike
        elif self.scenario == "degradation":
            base_hvac = 44.8 # Running degraded, extra strain
        
        if self.hvac_curtailed:
            base_hvac *= 0.72 # Reduced by 28% after action approval

        hvac_kw = round(base_hvac + random.uniform(-1.0, 1.0), 2)
        hvac_pf = 0.78 if self.scenario == "degradation" else 0.94

        self.device_energy_counters["hvac-01"] += hvac_kw * dt_hours
        readings.append({
            "deviceId": "hvac-01",
            "timestamp": now,
            "powerKw": hvac_kw,
            "energyKwh": round(self.device_energy_counters["hvac-01"], 2),
            "voltage": 230.0 if self.scenario != "degradation" else 222.0,
            "current": round((hvac_kw * 1000.0) / (230.0 * hvac_pf), 1),
            "powerFactor": hvac_pf,
            "frequency": 50.0,
            "quality": "ANOMALOUS" if self.scenario in ["peak_spike", "degradation"] else "GOOD"
        })

        # --- 4. Server Room Precision AC (hvac-02) ---
        hvac2_kw = round(16.5 + random.uniform(-0.5, 0.5), 2)
        self.device_energy_counters["hvac-02"] += hvac2_kw * dt_hours
        readings.append({
            "deviceId": "hvac-02",
            "timestamp": now,
            "powerKw": hvac2_kw,
            "energyKwh": round(self.device_energy_counters["hvac-02"], 2),
            "voltage": 230.0,
            "current": round((hvac2_kw * 1000.0) / (230.0 * 0.96), 1),
            "powerFactor": 0.96,
            "frequency": 50.0,
            "quality": "GOOD"
        })

        # --- 5. Campus LED Lighting (light-01) ---
        if self.scenario == "phantom_night" and (hour < 6 or hour > 21):
            light_kw = 24.0 # Left fully turned on overnight!
        elif 8.0 <= hour <= 19.0:
            light_kw = 18.5
        elif 19.0 < hour <= 22.0:
            light_kw = 11.0
        else:
            light_kw = 3.2 # Minimal night emergency lighting

        self.device_energy_counters["light-01"] += light_kw * dt_hours
        readings.append({
            "deviceId": "light-01",
            "timestamp": now,
            "powerKw": round(light_kw, 2),
            "energyKwh": round(self.device_energy_counters["light-01"], 2),
            "voltage": 230.0,
            "current": round((light_kw * 1000.0) / (230.0 * 0.97), 1),
            "powerFactor": 0.97,
            "frequency": 50.0,
            "quality": "ANOMALOUS" if (self.scenario == "phantom_night" and (hour < 6 or hour > 21)) else "GOOD"
        })

        # --- 6. Chilled Water Pump (pump-01) ---
        if self.scenario == "sensor_offline":
            pump_kw = 0.0
            pump_quality = "STALE"
        else:
            pump_kw = round(8.8 + random.uniform(-0.3, 0.3), 2)
            pump_quality = "GOOD"

        self.device_energy_counters["pump-01"] += pump_kw * dt_hours
        readings.append({
            "deviceId": "pump-01",
            "timestamp": now,
            "powerKw": pump_kw,
            "energyKwh": round(self.device_energy_counters["pump-01"], 2),
            "voltage": 230.0 if self.scenario != "sensor_offline" else 0.0,
            "current": round((pump_kw * 1000.0) / (230.0 * 0.91), 1) if pump_kw > 0 else 0.0,
            "powerFactor": 0.91,
            "frequency": 50.0,
            "quality": pump_quality
        })

        # --- 7. EV Fast Charger (ev-01) ---
        if self.ev_shifted:
            ev_kw = 0.0 # Charging paused/shifted
        elif 17.0 <= hour <= 21.0:
            ev_kw = 11.0 # Peak charging
        elif 22.0 <= hour or hour <= 4.0:
            ev_kw = 11.0 # Off-peak night charging
        else:
            ev_kw = 0.0

        self.device_energy_counters["ev-01"] += ev_kw * dt_hours
        readings.append({
            "deviceId": "ev-01",
            "timestamp": now,
            "powerKw": round(ev_kw, 2),
            "energyKwh": round(self.device_energy_counters["ev-01"], 2),
            "voltage": 230.0,
            "current": round((ev_kw * 1000.0) / (230.0 * 0.98), 1) if ev_kw > 0 else 0.0,
            "powerFactor": 0.98,
            "frequency": 50.0,
            "quality": "GOOD"
        })

        # --- 8. Cold Storage Refrigerator (ref-01) ---
        ref_kw = round(3.4 + random.uniform(-0.2, 0.4), 2)
        self.device_energy_counters["ref-01"] += ref_kw * dt_hours
        readings.append({
            "deviceId": "ref-01",
            "timestamp": now,
            "powerKw": ref_kw,
            "energyKwh": round(self.device_energy_counters["ref-01"], 2),
            "voltage": 230.0,
            "current": round((ref_kw * 1000.0) / (230.0 * 0.90), 1),
            "powerFactor": 0.90,
            "frequency": 50.0,
            "quality": "GOOD"
        })

        return readings

# Global singleton simulator instance
simulator_engine = CampusSimulator()
