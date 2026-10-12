import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import User, Site, Zone, Device, Alert, Recommendation, Action, Tariff, Report
from app.core.security import hash_password

class AppRepository:
    def __init__(self, db: Session):
        self.db = db

    def seed_initial_data(self):
        """Initializes database with required site, zone, devices, tariffs, and initial recommendations."""
        # 1. Default User
        if not self.db.query(User).filter_by(email="operator@fluxora.local").first():
            admin_user = User(
                name="Energy Director",
                email="operator@fluxora.local",
                password_hash=hash_password("fluxora2026"),
                role="operator"
            )
            self.db.add(admin_user)

        # 2. Site
        if not self.db.query(Site).filter_by(id="site-campus-01").first():
            site = Site(
                id="site-campus-01",
                name="Fluxora Innovation Tech Park",
                timezone="Asia/Kolkata",
                tariff_id="tariff-tou-2026",
                site_metadata={"areaSqFt": 150000, "contractDemandKva": 500}
            )
            self.db.add(site)

        # 3. Tariff
        if not self.db.query(Tariff).filter_by(id="tariff-tou-2026").first():
            tariff = Tariff(
                id="tariff-tou-2026",
                name="FY-2026 Commercial Time-of-Use Grid Tariff",
                currency="INR",
                rate_normal=8.00,
                rate_peak=12.50,
                rate_off_peak=5.50,
                peak_rules={"peak_hours": [17, 18, 19, 20], "off_peak_hours": [22, 23, 0, 1, 2, 3, 4, 5]},
                demand_charge=350.0,
                effective_period="2026-FY"
            )
            self.db.add(tariff)

        # 4. Zones
        zones = [
            {"id": "zone-central-plant", "name": "Central Utility Plant", "site_id": "site-campus-01"},
            {"id": "zone-datacenter", "name": "Data Center & IT Wing", "site_id": "site-campus-01"},
            {"id": "zone-office-floors", "name": "Workspaces & Floors 1-4", "site_id": "site-campus-01"},
            {"id": "zone-rooftop-parking", "name": "Rooftop PV & EV Bay", "site_id": "site-campus-01"}
        ]
        for z in zones:
            if not self.db.query(Zone).filter_by(id=z["id"]).first():
                self.db.add(Zone(id=z["id"], name=z["name"], site_id=z["site_id"]))

        # 5. Devices
        initial_devices = [
            {
                "id": "hvac-01", "name": "Main Chiller Plant HVAC", "device_type": "hvac",
                "zone_id": "zone-central-plant", "rated_power_kw": 60.0, "current_power_kw": 38.5,
                "controllable": True, "status": "online", "is_simulated": True
            },
            {
                "id": "hvac-02", "name": "Server Room Precision AC", "device_type": "hvac",
                "zone_id": "zone-datacenter", "rated_power_kw": 25.0, "current_power_kw": 16.5,
                "controllable": True, "status": "online", "is_simulated": True
            },
            {
                "id": "solar-01", "name": "Rooftop Solar PV Array 50kW", "device_type": "solar_inverter",
                "zone_id": "zone-rooftop-parking", "rated_power_kw": 50.0, "current_power_kw": 32.0,
                "controllable": False, "status": "online", "is_simulated": True
            },
            {
                "id": "battery-01", "name": "BESS Battery Storage (100kWh)", "device_type": "battery",
                "zone_id": "zone-central-plant", "rated_power_kw": 35.0, "current_power_kw": 0.0,
                "controllable": True, "status": "online", "is_simulated": True,
                "device_metadata": {"capacityKwh": 100.0, "socPercent": 76.5, "state": "idle"}
            },
            {
                "id": "ev-01", "name": "EV Fleet Fast Charger (Station 1)", "device_type": "ev_charger",
                "zone_id": "zone-rooftop-parking", "rated_power_kw": 22.0, "current_power_kw": 0.0,
                "controllable": True, "status": "online", "is_simulated": True
            },
            {
                "id": "light-01", "name": "Campus LED Lighting Grid", "device_type": "lighting",
                "zone_id": "zone-office-floors", "rated_power_kw": 25.0, "current_power_kw": 14.2,
                "controllable": True, "status": "online", "is_simulated": True
            },
            {
                "id": "pump-01", "name": "Chilled Water Primary Pump", "device_type": "pump",
                "zone_id": "zone-central-plant", "rated_power_kw": 15.0, "current_power_kw": 8.8,
                "controllable": False, "status": "online", "is_simulated": True
            },
            {
                "id": "ref-01", "name": "Cafeteria Cold Storage Unit", "device_type": "refrigerator",
                "zone_id": "zone-office-floors", "rated_power_kw": 6.0, "current_power_kw": 3.4,
                "controllable": False, "status": "online", "is_simulated": True
            }
        ]
        for d in initial_devices:
            if not self.db.query(Device).filter_by(id=d["id"]).first():
                meta = d.get("device_metadata", {})
                self.db.add(Device(
                    id=d["id"], name=d["name"], device_type=d["device_type"],
                    zone_id=d["zone_id"], rated_power_kw=d["rated_power_kw"],
                    current_power_kw=d["current_power_kw"], controllable=d["controllable"],
                    status=d["status"], is_simulated=d["is_simulated"],
                    device_metadata=meta
                ))

        # 6. Initial Alert (Prescriptive Anomaly Detection)
        if not self.db.query(Alert).filter_by(id="alert-init-01").first():
            alert = Alert(
                id="alert-init-01",
                alert_type="peak_risk",
                severity="high",
                status="open",
                source_id="hvac-01",
                title="Predicted Peak Demand Exceedance at 17:30",
                message="XGBoost model forecasts total site demand reaching 218.4 kW during peak tariff window (₹12.50/kWh). Contract demand penalty threshold is 220 kW.",
                evidence={"baselineKw": 182.0, "observedKw": 218.4, "durationMinutes": 45, "model": "xgboost"}
            )
            self.db.add(alert)

        # 7. Initial High-Priority Prescriptive Recommendation
        if not self.db.query(Recommendation).filter_by(id="rec-init-01").first():
            rec = Recommendation(
                id="rec-init-01",
                priority=1,
                title="Peak Shaving: Discharge BESS Battery & Pre-cool Chiller",
                action="Discharge BESS 30 kW between 17:30-20:00 and adjust HVAC thermostat to 25°C",
                reason="Reduces peak grid demand by 32 kW during highest tariff rate, avoiding ₹8,420 in peak and demand penalties.",
                target_device_id="battery-01",
                estimated_impact={"costAvoided": 8420.0, "peakReductionKw": 32.0, "kwhShifted": 80.0, "carbonSavedKg": 44.5},
                status="pending",
                model_version="fluxora-opt-v1.4"
            )
            self.db.add(rec)

        self.db.commit()

    def get_devices(self) -> List[Device]:
        return self.db.query(Device).all()

    def get_device(self, device_id: str) -> Optional[Device]:
        return self.db.query(Device).filter_by(id=device_id).first()

    def update_device(self, device_id: str, **kwargs) -> Optional[Device]:
        device = self.get_device(device_id)
        if device:
            for k, v in kwargs.items():
                setattr(device, k, v)
            self.db.commit()
            self.db.refresh(device)
        return device

    def get_alerts(self, status: Optional[str] = None) -> List[Alert]:
        query = self.db.query(Alert)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Alert.created_at.desc()).all()

    def update_alert_status(self, alert_id: str, new_status: str) -> Optional[Alert]:
        alert = self.db.query(Alert).filter_by(id=alert_id).first()
        if alert:
            alert.status = new_status
            alert.updated_at = datetime.datetime.utcnow()
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def get_recommendations(self, status: Optional[str] = None) -> List[Recommendation]:
        query = self.db.query(Recommendation)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Recommendation.priority.asc(), Recommendation.created_at.desc()).all()

    def update_recommendation_status(self, rec_id: str, new_status: str) -> Optional[Recommendation]:
        rec = self.db.query(Recommendation).filter_by(id=rec_id).first()
        if rec:
            rec.status = new_status
            self.db.commit()
            self.db.refresh(rec)
        return rec

    def log_action(self, rec_id: Optional[str], command: str, target_device_id: str, parameters: Dict[str, Any], actor: str = "operator@fluxora.local") -> Action:
        act = Action(
            id=f"act-{int(datetime.datetime.utcnow().timestamp()*1000)}",
            recommendation_id=rec_id,
            actor=actor,
            command=command,
            target_device_id=target_device_id,
            parameters=parameters,
            result="executed",
            timestamp=datetime.datetime.utcnow()
        )
        self.db.add(act)
        self.db.commit()
        self.db.refresh(act)
        return act

    def get_actions(self, limit: int = 50) -> List[Action]:
        return self.db.query(Action).order_by(Action.timestamp.desc()).limit(limit).all()
