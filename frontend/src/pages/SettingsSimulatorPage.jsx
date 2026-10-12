import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { SimulatedBadge } from '../components/Badges';
import { FlaskConical, Play, CheckCircle, AlertTriangle, Clock, Info, ArrowRight } from 'lucide-react';

const SCENARIOS = [
  {
    id: 'normal',
    label: 'Normal Daily Operation',
    description: 'All equipment operates on standard schedules with expected solar and grid power. Establishes the normal baseline benchmark.',
    problem: 'Routine operations within standard limits.',
    aiAction: 'Maintains optimal temperature baselines and normal solar self-consumption.',
    simulatedImpact: 'Estimated ~₹8,420 monthly cost savings vs unmanaged grid baseline.',
    tags: ['Standard Baseline', 'All Devices Online'],
    severity: 'info'
  },
  {
    id: 'peak_spike',
    label: 'Electricity Demand Spike',
    description: 'Building cooling and EV chargers draw high power simultaneously during peak evening rates. AI identifies risk of expensive peak surcharges.',
    problem: 'Simultaneous EV charging and HVAC cooling risks exceeding the 235 kW active cap during ₹12.50/kWh peak hours.',
    aiAction: 'Pre-cools thermal envelope and discharges 30 kW from battery storage during peak tariff window.',
    simulatedImpact: 'Shaves ~32 kW peak spike, avoiding ₹4,200 in demand charge penalties.',
    tags: ['High Cost Risk', 'Peak Rate Window', 'Peak Shaving'],
    severity: 'critical'
  },
  {
    id: 'degradation',
    label: 'Equipment Using Too Much Energy',
    description: 'A cooling chiller compressor is straining and consuming 34% more electricity than normal. AI flags the abnormal power draw for maintenance.',
    problem: 'Compressor mechanical friction causes 34% above-normal draw and lowered power factor (0.78).',
    aiAction: 'Flags maintenance ticket for chiller inspection and shifts secondary loop duty to pump-02.',
    simulatedImpact: 'Prevents ~45 kWh/day in mechanical energy waste and equipment failure.',
    tags: ['Abnormal Usage', 'Maintenance Alert', 'Chiller Strain'],
    severity: 'warning'
  },
  {
    id: 'phantom_night',
    label: 'Unnecessary Overnight Usage',
    description: 'Lighting or equipment was accidentally left running at 2:00 AM when the building is empty. AI detects after-hours waste.',
    problem: '35 kW non-essential floor lighting and display banks remain energized at 2:00 AM in an empty building.',
    aiAction: 'Flags phantom night load alert and schedules automated sleep mode.',
    simulatedImpact: 'Saves ~140 kWh per night, reducing monthly bills by ₹23,000.',
    tags: ['Overnight Waste', 'Empty Building', 'Automated Detection'],
    severity: 'warning'
  },
  {
    id: 'solar_surplus',
    label: 'Excess Solar Power',
    description: 'Midday sunshine produces more clean electricity than the facility needs. AI diverts free green power to fill the battery and charge EVs.',
    problem: 'Rooftop solar generates 48 kW during low midday building occupancy, creating excess clean energy.',
    aiAction: 'Charges 100 kWh battery storage and starts fleet EV charging to absorb 100% of solar generation.',
    simulatedImpact: '100% solar self-consumption, 0 kWh wasted curtailment, 34 kg CO₂ saved today.',
    tags: ['Clean Solar', 'Battery Charging', 'Zero Carbon'],
    severity: 'success'
  },
  {
    id: 'sensor_offline',
    label: 'Sensor Offline',
    description: 'A water pump sensor stops reporting data. AI marks the reading as stale rather than guessing, alerting technicians to check connectivity.',
    problem: 'Submeter telemetry stream for pump-01 goes silent during active duty cycle.',
    aiAction: 'Marks telemetry quality as STALE and isolates device from automated dispatch to prevent blind control.',
    simulatedImpact: 'Protects system reliability; flags diagnostic alert within 15 seconds.',
    tags: ['Data Reliability', 'Stale Reading Flagged', 'Sensor Health'],
    severity: 'warning'
  },
];

// The 6 simplified, approachable stages
const WORKFLOW_STAGES = [
  { id: 'DETECT',   label: 'Problem Detected',  desc: 'Sensors flag unusual electricity draw or high rate' },
  { id: 'ANALYZE',  label: 'AI Investigates',   desc: 'Forecast model analyzes historical baseline' },
  { id: 'PROPOSE',  label: 'Solution Proposed', desc: 'Smart algorithm calculates best energy fix' },
  { id: 'REVIEW',   label: 'Operator Reviews',  desc: 'Facility manager reviews proposed recommendation' },
  { id: 'ACTION',   label: 'Simulated Action',  desc: 'Settings sent to battery, cooling, or chargers' },
  { id: 'MEASURE',  label: 'Result Measured',   desc: 'Actual savings verified against baseline' },
];

const SEV_STYLES = {
  info:     { border: 'var(--border)', bg: '#fff', dot: '#2563EB' },
  warning:  { border: 'rgba(217,154,43,0.4)', bg: 'var(--amber-light)', dot: 'var(--amber)' },
  critical: { border: 'rgba(201,76,69,0.4)',  bg: 'var(--red-light)',   dot: 'var(--red)' },
  success:  { border: 'var(--green-mid)',      bg: 'var(--green-light)', dot: 'var(--green)' },
};

export default function SettingsSimulatorPage({ currentScenario, onScenarioChange, onManualTick, onNavigate }) {
  const [simState, setSimState] = useState(null);
  const [switching, setSwitching] = useState(null);
  const [ticked, setTicked] = useState(false);
  const [workflowActive, setWorkflowActive] = useState(false);
  const [workflowStep, setWorkflowStep] = useState(-1);

  useEffect(() => { loadState(); }, [currentScenario]);

  const loadState = async () => {
    try {
      const res = await api.getSimulatorState();
      if (res.success) setSimState(res.data);
    } catch(e) {}
  };

  const handleSwitch = async (id) => {
    setSwitching(id);
    await onScenarioChange(id);
    setSwitching(null);
    // Trigger workflow demonstration
    setWorkflowActive(true);
    setWorkflowStep(0);
  };

  // Step through workflow stages
  useEffect(() => {
    if (!workflowActive) return;
    if (workflowStep >= WORKFLOW_STAGES.length) {
      const t = setTimeout(() => {
        setWorkflowActive(false);
        setWorkflowStep(-1);
      }, 2500);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setWorkflowStep(s => s + 1), 600);
    return () => clearTimeout(t);
  }, [workflowActive, workflowStep]);

  const handleTick = async () => {
    await onManualTick();
    setTicked(true);
    setTimeout(() => setTicked(false), 1500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Page Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.3px', margin: 0 }}>
            Try Energy Scenarios
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 3 }}>
            Test how Fluxora responds to real-world challenges like peak demand spikes, equipment waste, and excess solar power.
          </p>
        </div>
        <SimulatedBadge label="Interactive Testing Lab" />
      </div>

      {/* Quick Simulation Controller */}
      <div style={{
        background: '#fff', border: '1px solid var(--border)', borderRadius: 10,
        padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12
      }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
            Simulate Next Reading
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
            Readings update automatically every 5 seconds. Click to immediately advance the clock by 1 step.
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {simState && (
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Active Scenario: <strong style={{ color: 'var(--green)' }}>{SCENARIOS.find(s => s.id === simState.currentScenario)?.label || simState.currentScenario}</strong>
            </div>
          )}
          <button onClick={handleTick} className="btn btn-primary" style={{ padding: '8px 18px', fontSize: 12.5 }}>
            <Play size={13} /> {ticked ? <><CheckCircle size={13} /> Generated!</> : 'Advance 1 Step (5s)'}
          </button>
        </div>
      </div>

      {/* 6-Stage Clear Workflow Visualizer */}
      <div className="card card-pad">
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            How Fluxora Resolves Energy Problems (6-Stage Pipeline)
          </h3>
          <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', marginTop: 3 }}>
            When you select any scenario below, watch the system detect, analyze, and solve the problem in real time.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10 }}>
          {WORKFLOW_STAGES.map((stage, idx) => {
            const done    = workflowStep > idx || (!workflowActive && workflowStep === -1);
            const active  = workflowActive && workflowStep === idx;
            const pending = workflowActive && workflowStep < idx;

            return (
              <div key={stage.id} style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: '12px 10px',
                borderRadius: 8,
                background: active ? 'var(--amber-light)' : done ? 'var(--green-light)' : 'var(--surface-2)',
                border: `1px solid ${active ? 'var(--amber)' : done ? 'var(--green-mid)' : 'var(--border)'}`,
                transition: 'all 0.25s ease'
              }}>
                <div style={{
                  width: 28, height: 28, borderRadius: '50%',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: active ? 'var(--amber)' : done ? 'var(--green)' : '#FFFFFF',
                  color: active || done ? '#FFFFFF' : 'var(--text-muted)',
                  fontSize: 12, fontWeight: 700, marginBottom: 8
                }}>
                  {done ? '✓' : idx + 1}
                </div>
                <div style={{ fontSize: 11.5, fontWeight: 700, color: active ? 'var(--amber)' : done ? 'var(--forest)' : 'var(--text-secondary)', textAlign: 'center' }}>
                  {stage.label}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', textAlign: 'center', marginTop: 4, lineHeight: 1.3 }}>
                  {stage.desc}
                </div>
              </div>
            );
          })}
        </div>

        {/* Expandable Technical Details for Judges */}
        <details style={{
          marginTop: 14,
          background: '#FFFFFF',
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '10px 14px',
          fontSize: 12
        }}>
          <summary style={{ fontWeight: 700, color: 'var(--forest)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Info size={14} color="var(--forest)" />
            <span>Technical Details: Under-The-Hood 10-Stage Architecture (For Judges)</span>
          </summary>
          <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--border)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Full pipeline stages executed in backend:
            <br /><strong>1. SENSE</strong> (5s hardware polling) ➔ <strong>2. CLEAN</strong> (range & quality filter) ➔ <strong>3. DETECT</strong> (IsolationForest anomaly scoring) ➔ <strong>4. PREDICT</strong> (XGBoost 24–48h horizon) ➔ <strong>5. OPTIMIZE</strong> (Constrained LP scheduler) ➔ <strong>6. RECOMMEND</strong> (Prescriptive evidence assembly) ➔ <strong>7. APPROVE</strong> (Human-in-the-loop authorization) ➔ <strong>8. EXECUTE</strong> (BACnet / Modbus dispatch) ➔ <strong>9. MEASURE</strong> (Post-action telemetry) ➔ <strong>10. VERIFY</strong> (IPMVP Option A baseline savings).
          </div>
        </details>
      </div>

      {/* Understandable Scenario Cards Grid */}
      <div>
        <div className="section-label" style={{ marginBottom: 12 }}>Choose a Scenario to Try</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
          {SCENARIOS.map(sc => {
            const sty = SEV_STYLES[sc.severity] || SEV_STYLES.info;
            const isActive = currentScenario === sc.id;
            const isLoading = switching === sc.id;

            return (
              <div key={sc.id} style={{
                background: isActive ? sty.bg : '#fff',
                border: `1px solid ${isActive ? sty.border : 'var(--border)'}`,
                borderRadius: 10,
                padding: '16px 18px',
                transition: 'all 0.15s ease',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: sty.dot, flexShrink: 0 }} />
                      <span style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text-primary)' }}>{sc.label}</span>
                    </div>
                    {isActive && (
                      <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 100, background: 'var(--green)', color: '#fff' }}>
                        ACTIVE NOW
                      </span>
                    )}
                  </div>

                  <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 12 }}>
                    {sc.description}
                  </p>

                  {/* Problem & Impact Breakdown */}
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 6,
                    padding: '10px 12px',
                    borderRadius: 8,
                    background: 'var(--surface-2)',
                    border: '1px solid var(--border)',
                    fontSize: 11.5,
                    marginBottom: 12
                  }}>
                    <div>
                      <strong style={{ color: 'var(--text-primary)' }}>Problem: </strong>
                      <span style={{ color: 'var(--text-secondary)' }}>{sc.problem}</span>
                    </div>
                    <div>
                      <strong style={{ color: 'var(--forest)' }}>AI Action: </strong>
                      <span style={{ color: 'var(--text-secondary)' }}>{sc.aiAction}</span>
                    </div>
                    <div>
                      <strong style={{ color: 'var(--green)' }}>Simulated Impact: </strong>
                      <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{sc.simulatedImpact}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 14 }}>
                    {sc.tags.map(t => (
                      <span key={t} style={{
                        fontSize: 10.5, fontWeight: 600, padding: '2px 8px', borderRadius: 100,
                        background: '#FFFFFF', color: 'var(--text-secondary)', border: '1px solid var(--border)'
                      }}>{t}</span>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => handleSwitch(sc.id)}
                  disabled={isActive || !!switching}
                  className={`btn ${isActive ? 'btn-primary' : 'btn-outline'}`}
                  style={{ width: '100%', justifyContent: 'center', fontSize: 12.5 }}
                >
                  {isLoading ? <><Clock size={13} /> Activating…</> :
                   isActive  ? <><CheckCircle size={13} /> Currently Active</> :
                               <><Play size={13} /> Activate This Scenario</>}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
