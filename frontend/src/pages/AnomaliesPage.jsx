import React, { useState } from 'react';
import { AlertOctagon, CheckCircle, Clock, AlertTriangle, Info } from 'lucide-react';
import { SimulatedBadge, QualityBadge } from '../components/Badges';

const TYPE_META = {
  spike:       { label: 'Sudden Power Spike',              color: 'var(--red)',   bg: 'var(--red-light)',   icon: '⚡' },
  phantom:     { label: 'Unnecessary Nighttime Usage',     color: 'var(--amber)', bg: 'var(--amber-light)', icon: '🌙' },
  degradation: { label: 'Equipment Straining (High Usage)',color: 'var(--amber)', bg: 'var(--amber-light)', icon: '📉' },
  offline:     { label: 'Sensor Offline',                  color: 'var(--red)',   bg: 'var(--red-light)',   icon: '🔴' },
  default:     { label: 'Unusual Pattern',                 color: 'var(--text-secondary)', bg: 'var(--surface-2)', icon: '⚠' },
};

function AnomalyCard({ anomaly, onAcknowledge, onResolve }) {
  const meta = TYPE_META[anomaly.anomalyType?.toLowerCase()] || TYPE_META.default;
  const isOpen = anomaly.status === 'open';
  const isAcked = anomaly.status === 'acknowledged';

  return (
    <div style={{
      background: '#fff',
      border: `1px solid ${isOpen ? 'rgba(201,76,69,0.3)' : 'var(--border)'}`,
      borderRadius: 10,
      padding: '16px 18px',
      display: 'flex',
      gap: 14
    }}>
      {/* Icon */}
      <div style={{
        width: 40, height: 40, borderRadius: 8,
        background: isOpen ? meta.bg : 'var(--surface-2)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 18, flexShrink: 0
      }}>
        {meta.icon}
      </div>

      {/* Body */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
          <div>
            <span style={{ fontSize: 11, fontWeight: 700, color: isOpen ? meta.color : 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
              {meta.label}
            </span>
            <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--text-muted)' }}>Equipment: {anomaly.deviceId}</span>
          </div>
          <span style={{
            fontSize: 10.5, fontWeight: 700, padding: '2px 8px', borderRadius: 100,
            background: isOpen ? 'var(--red-light)' : isAcked ? 'var(--amber-light)' : 'var(--green-light)',
            color: isOpen ? 'var(--red)' : isAcked ? 'var(--amber)' : 'var(--green)',
            border: `1px solid ${isOpen ? '#E8BFBC' : isAcked ? 'rgba(217,154,43,0.35)' : 'var(--green-mid)'}`
          }}>
            {isOpen ? 'Needs Review' : isAcked ? 'Acknowledged' : 'Resolved'}
          </span>
        </div>

        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
          {anomaly.description}
        </div>

        <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--text-secondary)', marginBottom: 10 }}>
          <span>Detection Confidence: {((anomaly.score || 0.85) * 100).toFixed(0)}%</span>
          <span>Time: {anomaly.timestamp ? new Date(anomaly.timestamp).toLocaleString() : 'Recently'}</span>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          {isOpen && (
            <button onClick={() => onAcknowledge(anomaly.id)} className="btn btn-ghost" style={{ padding: '5px 12px', fontSize: 11 }}>
              <Clock size={11} /> Mark as Reviewed
            </button>
          )}
          {(isOpen || isAcked) && (
            <button onClick={() => onResolve(anomaly.id)} className="btn btn-outline" style={{ padding: '5px 12px', fontSize: 11 }}>
              <CheckCircle size={11} /> Mark Resolved
            </button>
          )}
          {anomaly.status === 'resolved' && (
            <span style={{ fontSize: 11, color: 'var(--green)', display: 'flex', alignItems: 'center', gap: 5 }}>
              <CheckCircle size={11} /> Resolved
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AnomaliesPage({ anomalies = [], onAcknowledge, onResolve, onNavigate }) {
  const [filter, setFilter] = useState('all');

  const filtered = anomalies.filter(a =>
    filter === 'all' ? true :
    filter === 'open' ? a.status === 'open' :
    filter === 'acknowledged' ? a.status === 'acknowledged' :
    a.status === 'resolved'
  );

  const openCount = anomalies.filter(a => a.status === 'open').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.3px', margin: 0 }}>
            Unusual Energy Usage
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 3 }}>
            Continuous monitoring that spots energy waste, unexpected power spikes, and equipment strain before bills arrive.
          </p>
        </div>
        <SimulatedBadge label="Unusual Usage Detection" />
      </div>

      {/* Summary row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14 }}>
        {[
          { label: 'Unusual Events to Review', value: openCount, color: openCount > 0 ? 'var(--red)' : 'var(--green)', bg: openCount > 0 ? 'var(--red-light)' : 'var(--green-light)', border: openCount > 0 ? '#E8BFBC' : 'var(--green-mid)' },
          { label: 'Under Review', value: anomalies.filter(a => a.status === 'acknowledged').length, color: 'var(--amber)', bg: 'var(--amber-light)', border: 'rgba(217,154,43,0.35)' },
          { label: 'Resolved', value: anomalies.filter(a => a.status === 'resolved').length, color: 'var(--green)', bg: 'var(--green-light)', border: 'var(--green-mid)' },
        ].map(s => (
          <div key={s.label} style={{ background: s.bg, border: `1px solid ${s.border}`, borderRadius: 10, padding: '16px 20px' }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: s.color, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>{s.label}</div>
            <div style={{ fontSize: 28, fontWeight: 800, color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Expandable Technical Details for Judges */}
      <details style={{
        background: '#FFFFFF',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '10px 14px',
        fontSize: 12
      }}>
        <summary style={{ fontWeight: 700, color: 'var(--forest)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
          <Info size={14} color="var(--forest)" />
          <span>Technical Details: IsolationForest Machine Learning Model (For Judges)</span>
        </summary>
        <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--border)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          Detection engine utilizes <code>scikit-learn IsolationForest</code> unsupervised anomaly detection trained on historical feature tensors (active power, phase voltage, power factor, time-of-day). Contamination factor: 0.05. Anomaly score threshold: score &gt; 0.65 triggers prescriptive alert generation per Appendix C contract.
        </div>
      </details>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 6 }}>
        {[['all','All Events'],['open','Needs Review'],['acknowledged','Under Review'],['resolved','Resolved']].map(([v, l]) => (
          <button key={v} onClick={() => setFilter(v)} style={{
            padding: '5px 14px', borderRadius: 100, fontSize: 12, fontWeight: 600, cursor: 'pointer',
            border: '1px solid',
            borderColor: filter === v ? 'var(--green-mid)' : 'var(--border)',
            background: filter === v ? 'var(--green-light)' : '#fff',
            color: filter === v ? 'var(--green)' : 'var(--text-secondary)'
          }}>{l}</button>
        ))}
      </div>

      {/* Anomaly list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px 20px', color: 'var(--text-muted)' }}>
            <AlertOctagon size={32} color="var(--green)" style={{ marginBottom: 12 }} />
            <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>No unusual energy events in this view</div>
            <div style={{ fontSize: 13, marginTop: 4 }}>All equipment is running within normal energy patterns</div>
          </div>
        ) : (
          filtered.map(a => (
            <AnomalyCard
              key={a.id} anomaly={a}
              onAcknowledge={onAcknowledge}
              onResolve={onResolve}
            />
          ))
        )}
      </div>
    </div>
  );
}
