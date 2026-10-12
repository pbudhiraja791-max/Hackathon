import React from 'react';

export function MeasuredBadge({ label = 'Measured' }) {
  return (
    <span className="badge badge-measured" title="Physical or sensor-metered telemetry">
      ● {label}
    </span>
  );
}

export function SimulatedBadge({ label = 'Simulated' }) {
  return (
    <span className="badge badge-sim" title="Simulated hardware telemetry for test lab">
      ◎ {label}
    </span>
  );
}

export function PredictedBadge({ label = 'Predicted' }) {
  return (
    <span className="badge badge-predicted" title="ML/XGBoost diurnal forecast model">
      ◆ {label}
    </span>
  );
}

export function EstimatedBadge({ label = 'Estimated' }) {
  return (
    <span className="badge badge-est" title="Model-estimated or calculated metric">
      ≈ {label}
    </span>
  );
}

export function VerifiedBadge({ label = 'Verified' }) {
  return (
    <span className="badge badge-verified" title="IPMVP Option A verified measurement">
      ✓ {label}
    </span>
  );
}

export function QualityBadge({ quality }) {
  const map = {
    GOOD:        { cls: 'badge-verified', icon: '●', text: 'Good' },
    ESTIMATED:   { cls: 'badge-est',      icon: '≈', text: 'Estimated' },
    ANOMALOUS:   { cls: 'badge-anomaly',  icon: '⚠', text: 'Anomalous' },
    OUT_OF_RANGE:{ cls: 'badge-anomaly',  icon: '✕', text: 'Out of Range' },
    STALE:       { cls: 'badge-sim',      icon: '—', text: 'Stale' },
  };
  const m = map[quality] || map['GOOD'];
  return (
    <span className={`badge ${m.cls}`}>
      {m.icon} {m.text}
    </span>
  );
}
