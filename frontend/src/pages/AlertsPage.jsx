import React, { useState } from 'react';
import { BellRing, Check, AlertTriangle, Info } from 'lucide-react';
import { MeasuredBadge } from '../components/Badges';

const MOCK_ALERTS = [
  { id: 1, severity: 'critical', title: 'Main Cooling Chiller Drawing High Power', message: 'The main cooling chiller is drawing 82.1 kW (34% more electricity than normal). This could indicate a clogged air filter or refrigerant issue.', time: '2 min ago', acked: false },
  { id: 2, severity: 'warning',  title: 'High Electricity Demand Expected This Evening', message: 'AI forecast projects electricity usage will reach 231.8 kW at 17:30. Approved limit is 250 kVA. Recommended action: use battery power to offset the peak.', time: '8 min ago', acked: false },
  { id: 3, severity: 'info',     title: 'Battery Fully Charged from Free Solar Energy', message: 'The on-site battery is charged to 82% using clean rooftop solar power. Ready to supply clean electricity during expensive evening hours.', time: '22 min ago', acked: true },
  { id: 4, severity: 'warning',  title: 'EV Fleet Charging During Peak Electricity Rates', message: 'Vehicles are currently charging while power rates are highest (₹12.50/kWh). Consider shifting charging to 23:00 to pay the cheaper ₹5.50/kWh night rate.', time: '45 min ago', acked: true },
  { id: 5, severity: 'info',     title: 'Equipment Running While Building is Closed', message: 'A water pump was found running at 2:15 AM when no operations were scheduled. Review the timer schedule to eliminate waste.', time: '3 hr ago', acked: true },
];

const SEV_META = {
  critical: { color: 'var(--red)',   bg: 'var(--red-light)',   border: '#E8BFBC',                 icon: <AlertTriangle size={15} />, label: 'Action Required' },
  warning:  { color: 'var(--amber)', bg: 'var(--amber-light)', border: 'rgba(217,154,43,0.35)',   icon: <AlertTriangle size={15} />, label: 'Warning' },
  info:     { color: 'var(--blue)',  bg: 'var(--blue-light)',  border: 'rgba(37,99,235,0.25)',    icon: <Info size={15} />,           label: 'Notice' },
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState(MOCK_ALERTS);
  const [filter, setFilter] = useState('all');

  const ack = (id) => setAlerts(prev => prev.map(a => a.id === id ? { ...a, acked: true } : a));

  const filtered = filter === 'all' ? alerts : filter === 'unread' ? alerts.filter(a => !a.acked) : alerts.filter(a => a.severity === filter);
  const unread = alerts.filter(a => !a.acked).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.3px', margin: 0 }}>
              Alerts
            </h1>
            {unread > 0 && (
              <span style={{ background: 'var(--red)', color: '#fff', fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 100 }}>
                {unread} unread
              </span>
            )}
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 3 }}>
            Important notices about unexpected power spikes, peak rate warnings, and equipment health.
          </p>
        </div>
        <button onClick={() => setAlerts(prev => prev.map(a => ({ ...a, acked: true })))} className="btn btn-ghost" style={{ fontSize: 12 }}>
          <Check size={13} /> Mark all as read
        </button>
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 6 }}>
        {[['all','All Alerts'],['unread','Unread'],['critical','High Priority'],['warning','Warnings'],['info','Notices']].map(([v, l]) => (
          <button key={v} onClick={() => setFilter(v)} style={{
            padding: '5px 14px', borderRadius: 100, fontSize: 12, fontWeight: 600, cursor: 'pointer',
            border: '1px solid',
            borderColor: filter === v ? 'var(--green-mid)' : 'var(--border)',
            background: filter === v ? 'var(--green-light)' : '#fff',
            color: filter === v ? 'var(--green)' : 'var(--text-secondary)'
          }}>{l}</button>
        ))}
      </div>

      {/* Alert cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {filtered.map(alert => {
          const meta = SEV_META[alert.severity] || SEV_META.info;
          return (
            <div key={alert.id} style={{
              background: alert.acked ? '#fff' : meta.bg,
              border: `1px solid ${alert.acked ? 'var(--border)' : meta.border}`,
              borderRadius: 10,
              padding: '14px 18px',
              display: 'flex',
              gap: 14,
              opacity: alert.acked ? 0.8 : 1
            }}>
              <div style={{ color: meta.color, marginTop: 2, flexShrink: 0 }}>
                {meta.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                  <div style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text-primary)' }}>{alert.title}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap', marginLeft: 12 }}>{alert.time}</div>
                </div>
                <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{alert.message}</p>
                {!alert.acked && (
                  <button onClick={() => ack(alert.id)} className="btn btn-ghost" style={{ marginTop: 8, padding: '4px 10px', fontSize: 11 }}>
                    <Check size={11} /> Mark as Reviewed
                  </button>
                )}
              </div>
              <span style={{
                fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 100, height: 'fit-content',
                background: meta.bg, color: meta.color, border: `1px solid ${meta.border}`, flexShrink: 0
              }}>
                {meta.label}
              </span>
            </div>
          );
        })}
        {filtered.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
            <BellRing size={28} style={{ marginBottom: 12 }} />
            <div style={{ fontSize: 14, fontWeight: 600 }}>No alerts in this view</div>
          </div>
        )}
      </div>
    </div>
  );
}
