# FLUXORA
### *Smarter Energy for a Sustainable Tomorrow*
**PS08 — ENERGY FOR THE NEXT BILLION**  
*Complete Full-Stack Actionable Energy Management & Optimization System*

---

## 🌟 Executive Overview & PS08 Problem
Traditional meters passively display historical data without telling operators what to do next, allowing unmonitored HVAC, lighting, and empty facilities to cause massive invisible energy waste. Furthermore, rooftop solar, battery storage, and flexible EV charging are operated without coordinated timing.

**Fluxora** transforms energy telemetry into actionable operating decisions. It implements a closed-loop system: **Sense → Stream → Store → Clean → Learn → Optimize → Act → Measure → Feedback**.

> [!NOTE]
> **Zero Artificial Aesthetics & Complete Data Honesty**:
> Designed in strict accordance with the Master Build Specification, Fluxora features an industrial, human-designed interface with restrained colors (slate, emerald, amber, red). All simulated telemetry readings and estimated projections are explicitly labeled to maintain mathematical and engineering integrity.

---

## 🏗️ System Architecture & 10-Stage Operational Workflow

```
[1. SENSE] ESP32 / CT Sensors / Realistic Physics Simulator
    ↓
[2. STREAM] MQTT / HTTP Ingestion (POST /api/telemetry/readings)
    ↓
[3. CLEAN] Range Validation (160-290V, 0-1500kW), Null Handling, Quality Tagging (GOOD, ESTIMATED, ANOMALOUS)
    ↓
[4. STORE] Time-Series Repository + SQLite / PostgreSQL Relational DB (SQLAlchemy)
    ↓
[5. LEARN] Temporal Cylic Regressors, Weather Impact, Occupancy Proxy Feature Engineering
    ↓
[6. DETECT] Scikit-Learn Isolation Forest Anomaly Detection (Spikes, Phantom Loads, Degradation)
    ↓
[7. OPTIMIZE] Constrained Linear Scheduler (BESS Battery Dispatch, Smart EV Load Shift, HVAC Setpoint)
    ↓
[8. RECOMMEND] Prioritized Prescriptive Alerts with Financial & Peak Impact in ₹
    ↓
[9. ACT] Human-in-the-Loop Operator Approval & Real-Time BMS Relay Dispatch to Devices
    ↓
[10. MEASURE & FEEDBACK] Post-Action Telemetry vs Baseline Savings Verification (ASHRAE Guideline 14)
```

---

## 🚀 Quick Start Guide (Windows)

### 1. Automated Launch
Double-click:
```cmd
run_all.bat
```
This automatically starts:
- **FastAPI Backend Server**: `http://127.0.0.1:8000` (Interactive Docs: `http://127.0.0.1:8000/docs`)
- **React Executive Dashboard**: `http://localhost:5173`

---

### 2. Manual Launch (Step-by-Step)

#### Backend Setup
```bash
cd backend
# Virtual environment with Python 3.13 is already configured in backend/venv
venv\Scripts\python.exe run.py
```
*Backend runs on port `8000` with active background simulator worker generating live sensor telemetry every 5 seconds.*

#### Frontend Setup
```bash
cd frontend
cmd /c npm run dev
```
*Frontend runs on port `5173` with automated proxy to the FastAPI backend.*

---

## 🧪 Automated Test Suite

To verify all 17 unit, ML, and integration tests:
```bash
cd backend
venv\Scripts\python.exe -m pytest tests
```
**Test Coverage Includes:**
- `test_cleaner_and_tariff.py`: Range boundary checks, voltage clamp, and TOU tariff calculations.
- `test_ml_and_optimizer.py`: Temporal features, XGBoost forecast format (Appendix B), Isolation Forest anomaly scores (Appendix C), Constrained LP scheduler (Appendix D).
- `test_end_to_end_api.py`: Full FastAPI endpoint contract, telemetry ingestion, recommendation approvals, scenario switching, and savings verification (Appendix E).

---

## 📋 API Contract Adherence (Master Specification Appendices)

| Specification | Endpoint | Description |
|---|---|---|
| **Appendix A** | `POST /api/telemetry/readings` | Validates device ID, ISO timestamp, voltage, current, active power, PF, and applies quality flags. |
| **Appendix B** | `GET /api/forecast?horizonHours=24` | 24–48h XGBoost trajectory strictly isolated from historical readings. |
| **Appendix C** | `GET /api/anomalies` | Isolation Forest detections with quantitative evidence window (baseline vs observed). |
| **Appendix D** | `POST /api/optimization/run` | Constrained dispatch for BESS battery, EV charging, and HVAC curtailment with financial savings in ₹. |
| **Appendix E** | `GET /api/savings/verified` | Compares measured post-action consumption with counterfactual baseline (Status: `estimated` or `verified`). |

---

## 🏆 Official Hackathon Demo Flow (Winning 10-Step Walkthrough)

1. **Dashboard Introduction**: Open `http://localhost:5173`. Show headline *"Smarter Energy for a Sustainable Tomorrow"* and headline executive cards (Live load, predicted peak, solar generation, projected savings in ₹).
2. **Inspect Live Multi-Meter Stream**: Open **Live Energy** tab to show real-time ESP32/meter readings (kW, voltage, current, power factor, quality flags).
3. **Inject Disturbance Scenario**: Use the top bar dropdown to switch scenario to **"Peak Demand Spike (17:30 Risk)"**.
4. **Inspect Anomaly Evidence**: Navigate to **Anomaly Detection** to see the Isolation Forest trigger with evidence window (e.g. 44.8 kW observed vs 28.1 kW baseline).
5. **Review Prescriptive Action**: Review the top prescriptive recommendation highlighting ₹8,420 avoided peak demand cost.
6. **Solve Constrained Optimization**: Open **Optimization Engine** and click *"Solve Optimal Dispatch"* to view feasible battery discharge and smart EV shift schedules.
7. **Operator Approval Gate**: Click *"Approve & Dispatch BMS"*.
8. **Real-Time Telemetry Reaction**: Return to Dashboard or Live Energy to observe immediate grid draw reduction as BESS discharges 30 kW and HVAC setback takes effect.
9. **Review Verified Savings**: Open **Savings Verification** to see pre-action baseline (1,245 kWh) vs actual post-action (1,078 kWh), verifying 167 kWh saved and ₹1,636 avoided.
10. **Export Executive Report**: Open **Executive Reports** and download the CSV audit log or view the daily summary.

---

## 📁 Repository Structure

```
Hackathon/
├── Fluxora_PROJECT_REQUIREMENTS.txt  # 57-page master build specification
├── FLUXORA_MASTER_PLAN.md            # Architecture & execution blueprint
├── README.md                          # Documentation & demo guide
├── run_backend.bat                   # 1-click backend launcher
├── run_frontend.bat                  # 1-click frontend launcher
├── run_all.bat                       # Full-stack launcher
├── backend/
│   ├── requirements.txt
│   ├── run.py
│   ├── app/
│   │   ├── main.py                   # FastAPI app with background simulator
│   │   ├── core/                     # Config, database, security
│   │   ├── models/                   # SQLAlchemy models (User, Site, Device, Reading, etc.)
│   │   ├── schemas/                  # Pydantic schemas (Appendices A-E)
│   │   ├── repositories/             # Database access layers
│   │   ├── services/                 # Tariff, savings, and report services
│   │   ├── ingestion/                # TelemetryCleaner with range validation & quality flags
│   │   ├── ml/                       # Features, DemandForecaster, IsolationForest AnomalyDetector
│   │   ├── optimization/             # ConstrainedEnergyOptimizer solver
│   │   ├── simulator/                # CampusSimulator with dynamic physics & control feedback
│   │   └── api/                      # Clean REST routers
│   └── tests/                        # 17 automated tests
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css                 # Industrial design system
        ├── api/client.js             # API service client
        ├── components/               # Header, Sidebar, Badges
        └── pages/                    # 11 required operational views
```

---
*Built for PS08 — Energy for the Next Billion.*
