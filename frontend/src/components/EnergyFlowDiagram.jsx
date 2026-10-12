import React, { useState } from 'react';
import { X, Zap, Sun, Battery, Car, Building2, Activity, Info, ShieldCheck } from 'lucide-react';
import { QualityBadge, SimulatedBadge, MeasuredBadge } from './Badges';

/**
 * EnergyFlowDiagram — Industrial-grade SVG energy flow visualization
 * Displays live power flows between Grid, Solar PV, BESS, Campus Main Bus, and Sub-Loads.
 */

const NODE_RADIUS = 34;

const NODES = [
  { id: 'grid',    x: 85,  y: 200, label: 'Utility Grid',     sub: '33kV Substation',   icon: '⚡', color: '#1E3A5F', bg: '#EFF4FF', deviceId: null },
  { id: 'solar',   x: 230, y: 85,  label: 'Rooftop Solar PV', sub: '50 kW Array',       icon: '☀', color: '#D97706', bg: '#FEF3C7', deviceId: 'solar-01' },
  { id: 'battery', x: 230, y: 315, label: 'BESS Storage',     sub: '100 kWh LiFePO4',   icon: '🔋', color: '#7C3AED', bg: '#F5F3FF', deviceId: 'battery-01' },
  { id: 'campus',  x: 430, y: 200, label: 'Main Switchgear',  sub: '415V Campus Bus',   icon: '🏢', color: '#16845B', bg: '#E8F5EE', deviceId: null, isMain: true },
  { id: 'hvac',    x: 645, y: 85,  label: 'HVAC Chillers',    sub: 'Units 01 & 02',     icon: '❄', color: '#0891B2', bg: '#ECFEFF', deviceId: 'hvac-01' },
  { id: 'lights',  x: 645, y: 200, label: 'Smart Lighting',   sub: 'Campus LED Bus',    icon: '💡', color: '#D99A2B', bg: '#FFFBEB', deviceId: 'light-01' },
  { id: 'ev',      x: 645, y: 315, label: 'EV Fleet Chargers',sub: 'Bay 01 (Type 2)',   icon: '🚗', color: '#059669', bg: '#ECFDF5', deviceId: 'ev-01' },
];

const EDGES = [
  { from: 'grid',    to: 'campus',  dataKey: 'gridImportKw',      color: '#1E3A5F', label: 'Grid Import' },
  { from: 'solar',   to: 'campus',  dataKey: 'solarGenerationKw', color: '#D97706', label: 'Solar Generation' },
  { from: 'battery', to: 'campus',  dataKey: 'batteryDischargeKw',color: '#7C3AED', label: 'BESS Dispatch' },
  { from: 'campus',  to: 'hvac',    dataKey: 'hvacKw',            color: '#0891B2', label: 'HVAC Cooling Load' },
  { from: 'campus',  to: 'lights',  dataKey: 'lightsKw',          color: '#D99A2B', label: 'Facility Lighting' },
  { from: 'campus',  to: 'ev',      dataKey: 'evKw',              color: '#059669', label: 'EV Charging Load' },
];

function getNodeById(id) {
  return NODES.find(n => n.id === id);
}

function EdgeLine({ edge, values, isSelected, onClick }) {
  const from = getNodeById(edge.from);
  const to   = getNodeById(edge.to);
  const val  = values[edge.dataKey] ?? 0;
  const active = val > 0.3;

  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const len = Math.sqrt(dx*dx + dy*dy);
  const ux = dx/len; const uy = dy/len;
  const x1 = from.x + ux * NODE_RADIUS;
  const y1 = from.y + uy * NODE_RADIUS;
  const x2 = to.x   - ux * (NODE_RADIUS + 4);
  const y2 = to.y   - uy * (NODE_RADIUS + 4);

  const mx = (x1+x2)/2;
  const my = (y1+y2)/2;

  // Stroke width proportional to active power (min 1.8, max 6.5)
  const sw = active ? Math.max(2, Math.min(6.5, val / 25)) : 1.5;

  return (
    <g onClick={() => onClick(edge)} style={{ cursor: 'pointer' }}>
      {/* Invisible wider hit region */}
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="transparent" strokeWidth={20} />
      {/* Background track line */}
      <line
        x1={x1} y1={y1} x2={x2} y2={y2}
        stroke="#E2E8F0"
        strokeWidth={1.5}
      />
      {/* Active power line */}
      <line
        x1={x1} y1={y1} x2={x2} y2={y2}
        stroke={active ? edge.color : '#CBD5E1'}
        strokeWidth={sw}
        strokeDasharray={active ? 'none' : '4 4'}
        opacity={active ? (isSelected ? 1.0 : 0.85) : 0.4}
      />
      {/* Direction arrowhead */}
      {active && (
        <polygon
          points={`${x2},${y2} ${x2 - ux*9 - uy*5.5},${y2 - uy*9 + ux*5.5} ${x2 - ux*9 + uy*5.5},${y2 - uy*9 - ux*5.5}`}
          fill={edge.color}
          opacity={0.95}
        />
      )}
      {/* Power badge on line */}
      {active && (
        <g>
          <rect
            x={mx - 28}
            y={my - 11}
            width={56}
            height={18}
            rx={4}
            fill="#FFFFFF"
            stroke={isSelected ? edge.color : '#CBD5E1'}
            strokeWidth={1}
            filter="drop-shadow(0 1px 2px rgba(0,0,0,0.08))"
          />
          <text
            x={mx}
            y={my + 2}
            textAnchor="middle"
            fontSize={9.5}
            fontWeight={700}
            fill={edge.color}
            fontFamily="Inter, sans-serif"
          >
            {val.toFixed(1)} kW
          </text>
        </g>
      )}
    </g>
  );
}

function NodeCircle({ node, isSelected, onClick, telemetryData }) {
  const isMain = node.isMain;

  return (
    <g onClick={() => onClick(node)} style={{ cursor: 'pointer' }}>
      {/* Outer focus halo if selected */}
      {isSelected && (
        <circle
          cx={node.x}
          cy={node.y}
          r={NODE_RADIUS + 7}
          fill="none"
          stroke={node.color}
          strokeWidth={2.5}
          strokeDasharray="4 3"
          opacity={0.7}
        />
      )}
      {/* Node circle */}
      <circle
        cx={node.x}
        cy={node.y}
        r={isMain ? NODE_RADIUS + 5 : NODE_RADIUS}
        fill={node.bg}
        stroke={isSelected ? node.color : '#D1D5DB'}
        strokeWidth={isSelected ? 2.5 : 1.5}
      />
      {/* Icon */}
      <text
        x={node.x}
        y={node.y + 1}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={isMain ? 22 : 18}
        fontFamily="sans-serif"
      >
        {node.icon}
      </text>
      {/* Label and power below */}
      <text
        x={node.x}
        y={node.y + (isMain ? 48 : 44)}
        textAnchor="middle"
        fontSize={11}
        fontWeight={700}
        fill="var(--text-primary)"
        fontFamily="Inter, sans-serif"
      >
        {node.label}
      </text>
      <text
        x={node.x}
        y={node.y + (isMain ? 61 : 57)}
        textAnchor="middle"
        fontSize={9.5}
        fontWeight={600}
        fill={node.color}
        fontFamily="Inter, sans-serif"
      >
        {telemetryData ? `${telemetryData.power.toFixed(1)} kW` : node.sub}
      </text>
    </g>
  );
}

export default function EnergyFlowDiagram({ telemetry }) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);

  const agg  = telemetry?.aggregates || {};
  const devs = telemetry?.devices || [];

  const findDev = (id) => devs.find(d => d.deviceId === id) || {};

  const hvac1 = findDev('hvac-01');
  const hvac2 = findDev('hvac-02');
  const solar = findDev('solar-01');
  const batt  = findDev('battery-01');
  const light = findDev('light-01');
  const ev    = findDev('ev-01');

  const values = {
    gridImportKw: agg.gridImportKw ?? 0,
    solarGenerationKw: agg.solarGenerationKw ?? (solar.powerKw ?? 0),
    batteryDischargeKw: agg.batteryDischargeKw ?? Math.max(0, batt.powerKw ?? 0),
    hvacKw: (hvac1.powerKw ?? 0) + (hvac2.powerKw ?? 0),
    lightsKw: light.powerKw ?? 0,
    evKw: ev.powerKw ?? 0,
    totalLoadKw: agg.totalLoadKw ?? 0,
  };

  // Node telemetry power lookup
  const getNodePower = (nodeId) => {
    switch(nodeId) {
      case 'grid':    return { power: values.gridImportKw };
      case 'solar':   return { power: values.solarGenerationKw };
      case 'battery': return { power: Math.abs(batt.powerKw ?? 0) };
      case 'campus':  return { power: values.totalLoadKw };
      case 'hvac':    return { power: values.hvacKw };
      case 'lights':  return { power: values.lightsKw };
      case 'ev':      return { power: values.evKw };
      default: return null;
    }
  };

  // Detailed telemetry view for selection
  const getDetail = () => {
    if (selectedNode) {
      switch(selectedNode.id) {
        case 'grid':
          return {
            title: 'Utility Grid Incomer',
            sub: 'Primary Interconnection Feed (33kV / 415V)',
            color: '#1E3A5F',
            badge: <MeasuredBadge label="Utility Meter" />,
            rows: [
              ['Active Power (kW)', `${values.gridImportKw.toFixed(1)} kW`],
              ['Apparent Power (kVA)', `${(values.gridImportKw / 0.94).toFixed(1)} kVA @ 0.94 PF`],
              ['Contract Demand', '250 kVA Sanctioned'],
              ['Active Tariff Period', 'Normal (₹8.00/kWh)'],
              ['Phase Voltage (V)', '415 V / 240 V line-to-neutral'],
              ['Interconnection State', 'Synchronized (50.0 Hz)']
            ]
          };
        case 'solar':
          return {
            title: 'Rooftop Solar PV Array',
            sub: 'Inverter: solar-01 (Building B Roof)',
            color: '#D97706',
            badge: <SimulatedBadge label="PV Telemetry" />,
            rows: [
              ['Current Generation', `${values.solarGenerationKw.toFixed(1)} kW`],
              ['Rated Capacity', '50.0 kW Peak DC'],
              ['Output Voltage', `${(solar.voltage || 230.0).toFixed(1)} V AC`],
              ['Power Factor', `${(solar.powerFactor || 0.99).toFixed(2)} Unity`],
              ['Self-Consumption', '100% On-Campus Usage'],
              ['Telemetry Quality', <QualityBadge quality={solar.quality || 'GOOD'} />]
            ]
          };
        case 'battery':
          return {
            title: 'Battery Energy Storage (BESS)',
            sub: 'Inverter: battery-01 (100 kWh LiFePO4 Pack)',
            color: '#7C3AED',
            badge: <SimulatedBadge label="BESS Controller" />,
            rows: [
              ['Current Power Flow', `${(batt.powerKw || 0).toFixed(1)} kW (${batt.powerKw > 0 ? 'Discharging' : batt.powerKw < 0 ? 'Charging' : 'Standby'})`],
              ['State of Charge (SOC)', `${(batt.socPct || 76.5).toFixed(1)}%`],
              ['Pack Usable Capacity', '100.0 kWh'],
              ['Min SOC Constraint', '20.0% Reserve Limit'],
              ['Dispatch Mode', 'Peak Shaving Automated'],
              ['Telemetry Quality', <QualityBadge quality={batt.quality || 'GOOD'} />]
            ]
          };
        case 'campus':
          return {
            title: 'Campus Main Distribution Bus',
            sub: 'Central Switchgear & Power Quality Meter',
            color: '#16845B',
            badge: <MeasuredBadge label="Bus Incomer" />,
            rows: [
              ['Total Campus Load', `${values.totalLoadKw.toFixed(1)} kW`],
              ['Grid Import Contribution', `${values.gridImportKw.toFixed(1)} kW (${values.totalLoadKw > 0 ? ((values.gridImportKw / values.totalLoadKw) * 100).toFixed(1) : 0}%)`],
              ['Clean Solar Contribution', `${values.solarGenerationKw.toFixed(1)} kW (${values.totalLoadKw > 0 ? ((values.solarGenerationKw / values.totalLoadKw) * 100).toFixed(1) : 0}%)`],
              ['BESS Dispatch Contribution', `${values.batteryDischargeKw.toFixed(1)} kW`],
              ['Bus Power Factor', '0.94 Lagging'],
              ['Frequency', '50.02 Hz Stable']
            ]
          };
        case 'hvac':
          return {
            title: 'Central HVAC Chiller Plant',
            sub: 'hvac-01 (Zone East) & hvac-02 (Zone West)',
            color: '#0891B2',
            badge: <SimulatedBadge label="BACnet Modbus" />,
            rows: [
              ['Chiller 01 Active Power', `${(hvac1.powerKw || 0).toFixed(1)} kW`],
              ['Chiller 02 Active Power', `${(hvac2.powerKw || 0).toFixed(1)} kW`],
              ['Combined Cooling Load', `${values.hvacKw.toFixed(1)} kW`],
              ['Thermostat Setpoint', '24.0°C (Comfort range 23-26°C)'],
              ['Power Factor', `${(hvac1.powerFactor || 0.88).toFixed(2)}`],
              ['Data Quality', <QualityBadge quality={hvac1.quality || 'GOOD'} />]
            ]
          };
        case 'lights':
          return {
            title: 'Facility Smart Lighting Bus',
            sub: 'Device: light-01 (Occupancy & DALI Dimming)',
            color: '#D99A2B',
            badge: <SimulatedBadge label="IoT Telemetry" />,
            rows: [
              ['Active Lighting Power', `${values.lightsKw.toFixed(1)} kW`],
              ['Connected Fixtures', '8 Office Floors LED Arrays'],
              ['Daylight Harvesting', 'Active (40% dimming)'],
              ['Power Factor', `${(light.powerFactor || 0.95).toFixed(2)}`],
              ['Data Quality', <QualityBadge quality={light.quality || 'GOOD'} />]
            ]
          };
        case 'ev':
          return {
            title: 'Campus EV Fleet Charging Hub',
            sub: 'Device: ev-01 (Type-2 Dual 22kW Fast Charger)',
            color: '#059669',
            badge: <SimulatedBadge label="OCPP Telemetry" />,
            rows: [
              ['Charging Demand', `${values.evKw.toFixed(1)} kW`],
              ['Connected Vehicles', '2 Fleet Vehicles Connected'],
              ['Tariff Shifting Status', 'Shiftable Load (Target 06:00 AM)'],
              ['Charging Mode', 'Smart Delay Active on Peak Tariff'],
              ['Data Quality', <QualityBadge quality={ev.quality || 'GOOD'} />]
            ]
          };
        default: return null;
      }
    }

    if (selectedEdge) {
      const val = values[selectedEdge.dataKey] ?? 0;
      return {
        title: selectedEdge.label,
        sub: `Flow vector: ${selectedEdge.from.toUpperCase()} ➔ ${selectedEdge.to.toUpperCase()}`,
        color: selectedEdge.color,
        badge: <MeasuredBadge label="Real-Time Vector" />,
        rows: [
          ['Active Transfer', `${val.toFixed(1)} kW`],
          ['Current Direction', `${selectedEdge.from} ➔ ${selectedEdge.to}`],
          ['Operating State', val > 0.5 ? 'Active Transmission' : 'Zero / Idle Flow'],
          ['Voltage Class', '415V 3-Phase Low Voltage Bus'],
          ['Quality Status', 'GOOD (Telemetry synchronized)']
        ]
      };
    }

    return null;
  };

  const detail = getDetail();

  const clearSelection = () => {
    setSelectedNode(null);
    setSelectedEdge(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, width: '100%' }}>
      {/* Visual Canvas Area with optional side-by-side details panel */}
      <div style={{ display: 'flex', gap: 16, alignItems: 'stretch', flexWrap: 'wrap' }}>
        {/* SVG Canvas */}
        <div style={{ flex: detail ? '1 1 480px' : '1 1 100%', minWidth: 280, position: 'relative' }}>
          <svg
            viewBox="0 0 760 410"
            style={{ width: '100%', height: 'auto', minHeight: 250, maxHeight: 370 }}
            aria-label="Real-time campus energy flow diagram"
          >
            {/* Render connection edges */}
            {EDGES.map(edge => (
              <EdgeLine
                key={`${edge.from}-${edge.to}`}
                edge={edge}
                values={values}
                isSelected={selectedEdge?.label === edge.label}
                onClick={(e) => { setSelectedEdge(e); setSelectedNode(null); }}
              />
            ))}

            {/* Render asset nodes */}
            {NODES.map(node => (
              <NodeCircle
                key={node.id}
                node={node}
                isSelected={selectedNode?.id === node.id}
                onClick={(n) => { setSelectedNode(n); setSelectedEdge(null); }}
                telemetryData={getNodePower(node.id)}
              />
            ))}
          </svg>
        </div>

        {/* Reserved Details Panel (never covers the diagram) */}
        {detail && (
          <div style={{
            flex: '0 0 240px',
            background: 'var(--surface-2)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: '14px 16px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            alignSelf: 'stretch'
          }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: detail.color }}>{detail.title}</div>
                  <div style={{ fontSize: 10.5, color: 'var(--text-muted)', marginTop: 2, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                    {detail.sub}
                  </div>
                </div>
                <button
                  onClick={clearSelection}
                  aria-label="Close detail panel"
                  style={{ background: 'none', border: 'none', padding: 2, cursor: 'pointer', color: 'var(--text-muted)', flexShrink: 0 }}
                >
                  <X size={15} />
                </button>
              </div>

              <div style={{ marginBottom: 10 }}>{detail.badge}</div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {detail.rows.map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11.5, padding: '3px 0', borderBottom: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{k}</span>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)', textAlign: 'right' }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={clearSelection}
              className="btn btn-outline"
              style={{ width: '100%', justifyContent: 'center', fontSize: 11, padding: '4px 8px', marginTop: 12 }}
            >
              Close Asset Details
            </button>
          </div>
        )}
      </div>

      {/* Legend & interaction hint */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 4px',
        fontSize: 11,
        color: 'var(--text-muted)'
      }}>
        <span>Click any asset node to view live readings in the reserved panel</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--green)' }} /> Line thickness ∝ active kW
        </span>
      </div>
    </div>
  );
}
