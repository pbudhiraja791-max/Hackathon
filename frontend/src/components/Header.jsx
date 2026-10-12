import React, { useState } from 'react';
import { RefreshCw, ChevronDown, Play, Zap } from 'lucide-react';
import { SimulatedBadge } from './Badges';

const SCENARIOS = [
  { value: 'normal',         label: 'Normal Daily Operation' },
  { value: 'peak_spike',     label: 'Electricity Demand Spike' },
  { value: 'degradation',    label: 'Equipment Using Too Much Energy' },
  { value: 'phantom_night',  label: 'Unnecessary Overnight Usage' },
  { value: 'solar_surplus',  label: 'Excess Solar Power' },
  { value: 'sensor_offline', label: 'Sensor Offline' },
];

export default function Header({
  currentScenario,
  onScenarioChange,
  onManualTick,
  isRefreshing,
  onRefreshToggle,
  lastUpdated
}) {
  const [changing, setChanging] = useState(false);

  const handleSelect = async (e) => {
    const sc = e.target.value;
    setChanging(true);
    await onScenarioChange(sc);
    setChanging(false);
  };

  const timeStr = lastUpdated
    ? new Date(lastUpdated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : 'Connecting…';

  return (
    <header style={{
      background: '#FFFFFF',
      borderBottom: '1px solid var(--border)',
      padding: '0 24px',
      height: '56px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 1px 3px rgba(23,43,37,0.06)'
    }}>

      {/* ── Brand ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: 32,
          height: 32,
          background: 'var(--forest)',
          borderRadius: 8,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          <Zap size={16} color="#fff" strokeWidth={2.4} />
        </div>
        <div>
          <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.3px', lineHeight: 1.1 }}>
            FLUXORA
          </div>
          <div style={{ fontSize: 10.5, color: 'var(--text-muted)', fontWeight: 500, lineHeight: 1.1 }}>
            Energy Intelligence Platform
          </div>
        </div>
      </div>

      {/* ── Center: Compact Demo Controller ── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        background: 'var(--surface-2)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '4px 10px'
      }}>
        <span style={{
          fontSize: 10,
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.4px',
          color: 'var(--forest)',
          background: 'var(--green-light)',
          padding: '2px 6px',
          borderRadius: 4,
          border: '1px solid var(--green-mid)'
        }}>
          Demo Mode
        </span>

        <div style={{ width: 1, height: 14, background: 'var(--border)' }} />

        <div style={{ position: 'relative' }}>
          <select
            value={currentScenario}
            onChange={handleSelect}
            disabled={changing}
            style={{
              background: 'transparent',
              color: 'var(--text-primary)',
              border: 'none',
              padding: '2px 22px 2px 4px',
              fontSize: 12.5,
              fontWeight: 600,
              cursor: 'pointer',
              outline: 'none',
              appearance: 'none',
              WebkitAppearance: 'none'
            }}
          >
            {SCENARIOS.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
          <ChevronDown size={12} color="var(--text-muted)" style={{ position: 'absolute', right: 2, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
        </div>

        <button
          onClick={onManualTick}
          title="Simulate 1 step forward (5s)"
          className="btn btn-outline"
          style={{ padding: '3px 8px', fontSize: 11, border: 'none', background: '#FFFFFF' }}
        >
          <Play size={10} /> Step
        </button>
      </div>

      {/* ── Right: Clean Connection Status & Refresh Control ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            background: isRefreshing ? 'var(--green)' : 'var(--amber)'
          }} className={isRefreshing ? 'pulse' : ''} />
          <span style={{ fontSize: 11.5, fontWeight: 500, color: 'var(--text-secondary)' }}>
            {isRefreshing ? 'Connected' : 'Paused'}
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            • {timeStr}
          </span>
        </div>

        <button
          onClick={onRefreshToggle}
          title={isRefreshing ? "Pause live stream" : "Resume live stream"}
          style={{
            background: 'transparent',
            border: '1px solid var(--border)',
            borderRadius: 6,
            padding: '5px 8px',
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            fontSize: 11.5,
            fontWeight: 600,
            color: 'var(--text-secondary)',
            cursor: 'pointer'
          }}
        >
          <RefreshCw size={12} className={isRefreshing ? 'animate-spin' : ''} />
          <span>{isRefreshing ? 'Live' : 'Resume'}</span>
        </button>
      </div>
    </header>
  );
}
