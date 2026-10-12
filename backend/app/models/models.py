import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="operator")  # admin, operator, viewer
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Site(Base):
    __tablename__ = "sites"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    timezone = Column(String(50), default="Asia/Kolkata")
    tariff_id = Column(String(50), nullable=True)
    site_metadata = Column(JSON, default=dict)

    zones = relationship("Zone", back_populates="site", cascade="all, delete-orphan")

class Zone(Base):
    __tablename__ = "zones"

    id = Column(String(50), primary_key=True)
    site_id = Column(String(50), ForeignKey("sites.id"))
    name = Column(String(100), nullable=False)
    occupancy_schedule = Column(JSON, default=dict)

    site = relationship("Site", back_populates="zones")
    devices = relationship("Device", back_populates="zone", cascade="all, delete-orphan")

class Device(Base):
    __tablename__ = "devices"

    id = Column(String(50), primary_key=True)
    zone_id = Column(String(50), ForeignKey("zones.id"), nullable=True)
    name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)  # hvac, lighting, pump, chiller, ev_charger, solar_inverter, battery, etc.
    rated_power_kw = Column(Float, default=10.0)
    current_power_kw = Column(Float, default=0.0)
    today_energy_kwh = Column(Float, default=0.0)
    controllable = Column(Boolean, default=False)
    status = Column(String(30), default="online")  # online, offline, degraded, standby
    is_simulated = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    device_metadata = Column(JSON, default=dict)

    zone = relationship("Zone", back_populates="devices")
    readings = relationship("Reading", back_populates="device", cascade="all, delete-orphan")

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.id"), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    power_kw = Column(Float, nullable=False)
    energy_kwh = Column(Float, default=0.0)
    voltage = Column(Float, default=230.0)
    current = Column(Float, default=0.0)
    power_factor = Column(Float, default=0.95)
    frequency = Column(Float, default=50.0)
    quality = Column(String(20), default="GOOD")  # GOOD, ESTIMATED, ANOMALOUS, OUT_OF_RANGE

    device = relationship("Device", back_populates="readings")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(50), primary_key=True)
    alert_type = Column(String(50), nullable=False)  # peak_risk, abnormal_load, phantom_night_load, degradation, sensor_offline, renewable_underuse
    severity = Column(String(20), nullable=False)    # critical, high, medium, low
    status = Column(String(20), default="open")       # open, acknowledged, actioned, resolved
    source_id = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(50), primary_key=True)
    priority = Column(Integer, default=1)  # 1 (Highest) to 5
    title = Column(String(200), nullable=False)
    action = Column(String(200), nullable=False)
    reason = Column(Text, nullable=False)
    target_device_id = Column(String(50), nullable=True)
    estimated_impact = Column(JSON, default=dict) # {"costAvoided": 4200, "peakReductionKw": 18, "kwhSaved": 65}
    status = Column(String(30), default="pending") # pending, approved, rejected, executed
    model_version = Column(String(50), default="fluxora-opt-v1")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    actions = relationship("Action", back_populates="recommendation")

class Action(Base):
    __tablename__ = "actions"

    id = Column(String(50), primary_key=True)
    recommendation_id = Column(String(50), ForeignKey("recommendations.id"), nullable=True)
    actor = Column(String(100), default="operator@fluxora.local")
    command = Column(String(100), nullable=False) # e.g. "SET_SETPOINT_25C", "DISCHARGE_BESS_30KW", "SHIFT_EV_2100"
    target_device_id = Column(String(50), nullable=False)
    parameters = Column(JSON, default=dict)
    result = Column(String(50), default="executed") # requested, acknowledged, executed, failed
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    recommendation = relationship("Recommendation", back_populates="actions")

class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    currency = Column(String(10), default="INR")
    rate_normal = Column(Float, default=8.00)
    rate_peak = Column(Float, default=12.50)
    rate_off_peak = Column(Float, default=5.50)
    peak_rules = Column(JSON, default=dict)
    demand_charge = Column(Float, default=350.0)
    effective_period = Column(String(100), default="2026-FY")

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(50), primary_key=True)
    report_type = Column(String(20), nullable=False) # daily, monthly, audit
    title = Column(String(200), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=False)
    data_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
