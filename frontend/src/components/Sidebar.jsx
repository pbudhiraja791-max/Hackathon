import React from 'react';
import {
  LayoutDashboard,
  Activity,
  History,
  TrendingUp,
  AlertOctagon,
  Sliders,
  Cpu,
  SunMedium,
  BellRing,
  ShieldCheck,
  FileSpreadsheet,
  FlaskConical
} from 'lucide-react';

const navGroups = [
  {
    label: 'WORKSPACE',
    items: [
      { id: 'dashboard',    label: 'Overview',                 icon: LayoutDashboard },
      { id: 'live',         label: 'Live Energy',              icon: Activity },
      { id: 'forecast',     label: 'Demand Forecast',          icon: TrendingUp },
      { id: 'optimization', label: 'Smart Optimization',       icon: Sliders },
      { id: 'devices',      label: 'Assets & Devices',         icon: Cpu },
      { id: 'alerts',       label: 'Alerts',                   icon: BellRing },
    ]
  },
  {
    label: 'ANALYTICS',
    items: [
      { id: 'savings',      label: 'Impact & Savings',         icon: ShieldCheck },
      { id: 'historical',   label: 'Energy History',           icon: History },
      { id: 'renewable',    label: 'Renewables & Storage',     icon: SunMedium },
      { id: 'anomalies',    label: 'Anomaly Detection',        icon: AlertOctagon },
      { id: 'reports',      label: 'Executive Reports',        icon: FileSpreadsheet },
    ]
  },
  {
    label: 'EXPERIMENT',
    items: [
      { id: 'simulator',    label: 'Scenario Lab',             icon: FlaskConical },
    ]
  }
];

export default function Sidebar({ currentTab, onSelectTab, alertCount = 0, recommendationCount = 0 }) {
  return (
    <aside style={{
      width: 235,
      background: '#FFFFFF',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px 10px',
      flexShrink: 0,
      minHeight: 'calc(100vh - 56px)',
      overflowY: 'auto'
    }}>
      {navGroups.map((group) => (
        <div key={group.label} style={{ marginBottom: 18 }}>
          <div className="section-label" style={{ padding: '0 10px 6px' }}>
            {group.label}
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;

              // Badge count for certain items
              const count =
                item.id === 'alerts'       ? alertCount :
                item.id === 'optimization' ? recommendationCount : 0;

              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '9px 10px',
                    borderRadius: 7,
                    background: isActive ? 'var(--green-light)' : 'transparent',
                    color: isActive ? 'var(--green)' : 'var(--text-secondary)',
                    border: isActive ? '1px solid var(--green-mid)' : '1px solid transparent',
                    fontWeight: isActive ? 700 : 500,
                    fontSize: 13,
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.12s ease',
                    width: '100%'
                  }}
                  onMouseEnter={e => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'var(--surface-2)';
                      e.currentTarget.style.color = 'var(--text-primary)';
                    }
                  }}
                  onMouseLeave={e => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.color = 'var(--text-secondary)';
                    }
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
                    <Icon
                      size={15}
                      color={isActive ? 'var(--green)' : 'var(--text-muted)'}
                      strokeWidth={isActive ? 2.2 : 1.8}
                    />
                    <span>{item.label}</span>
                  </div>

                  {count > 0 && (
                    <span style={{
                      background: item.id === 'alerts' ? 'var(--red)' : 'var(--green)',
                      color: '#fff',
                      fontSize: 10,
                      fontWeight: 700,
                      padding: '1px 6px',
                      borderRadius: 100,
                      lineHeight: '16px'
                    }}>
                      {count}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      ))}

      {/* Facility info footer with plain-English terminology */}
      <div style={{ marginTop: 'auto' }}>
        <div style={{
          padding: '12px 14px',
          background: 'var(--surface-2)',
          borderRadius: 8,
          border: '1px solid var(--border)'
        }}>
          <div className="section-label" style={{ marginBottom: 4 }}>Facility Profile</div>
          <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
            Campus IT Tech Park
          </div>
          <div style={{ fontSize: 11, color: 'var(--green)', fontWeight: 600, marginTop: 4, display: 'flex', alignItems: 'center', gap: 5 }}>
            <span className="dot dot-green" style={{ width: 6, height: 6 }} />
            Approved Power Limit: 250 kVA
          </div>
        </div>
      </div>
    </aside>
  );
}
