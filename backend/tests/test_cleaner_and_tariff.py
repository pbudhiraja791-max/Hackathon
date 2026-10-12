import datetime
import pytest
from app.ingestion.cleaner import TelemetryCleaner
from app.services.tariff_service import TariffService

def test_telemetry_cleaner_valid():
    sample = {
        "deviceId": "hvac-01",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "powerKw": 42.5,
        "voltage": 230.0,
        "current": 185.0,
        "powerFactor": 0.94
    }
    cleaned, quality, note = TelemetryCleaner.clean_and_tag(sample)
    assert quality == "GOOD"
    assert cleaned["powerKw"] == 42.5
    assert cleaned["voltage"] == 230.0

def test_telemetry_cleaner_out_of_range_voltage():
    sample = {
        "deviceId": "pump-01",
        "powerKw": 10.0,
        "voltage": 320.0, # Impossible grid voltage
        "current": 45.0,
        "powerFactor": 0.95
    }
    cleaned, quality, note = TelemetryCleaner.clean_and_tag(sample)
    assert quality == "OUT_OF_RANGE"
    assert cleaned["voltage"] == TelemetryCleaner.VOLTAGE_MAX

def test_telemetry_energy_accumulation():
    t0 = datetime.datetime.utcnow()
    t1 = t0 + datetime.timedelta(hours=1)
    
    r0 = {"deviceId": "hvac-01", "timestamp": t0, "powerKw": 50.0, "energyKwh": 100.0}
    r1 = {"deviceId": "hvac-01", "timestamp": t1, "powerKw": 50.0}

    cleaned1, quality, _ = TelemetryCleaner.clean_and_tag(r1, prev_reading=r0)
    # Energy increment = 50kW * 1h = 50kWh => 100 + 50 = 150 kWh
    assert cleaned1["energyKwh"] == 150.0

def test_tariff_tou_calculation():
    peak_rate, period = TariffService.get_rate_for_hour(18)
    assert period == "PEAK"
    assert peak_rate == 12.50

    off_peak_rate, period_off = TariffService.get_rate_for_hour(23)
    assert period_off == "OFF_PEAK"
    assert off_peak_rate == 5.50
