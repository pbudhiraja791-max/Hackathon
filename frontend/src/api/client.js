const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `HTTP Error ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request('/health'),

  // Telemetry
  getLiveTelemetry: () => request('/telemetry/live'),
  getTelemetryHistory: (deviceId, limit = 60) => 
    request(`/telemetry/history?${deviceId ? `deviceId=${deviceId}&` : ''}limit=${limit}`),
  postTelemetryReading: (data) => 
    request('/telemetry/readings', { method: 'POST', body: JSON.stringify(data) }),

  // Devices
  getDevices: () => request('/devices'),
  getDeviceDetail: (id) => request(`/devices/${id}`),
  sendDeviceCommand: (id, command, parameters = {}) => 
    request(`/devices/${id}/command`, { 
      method: 'POST', 
      body: JSON.stringify({ command, parameters, actor: 'operator@fluxora.local' }) 
    }),

  // Analytics
  getLoadAnalytics: () => request('/analytics/load'),
  getCostAnalytics: () => request('/analytics/cost'),
  getSourcesAnalytics: () => request('/analytics/sources'),
  getPeakAnalytics: () => request('/analytics/peak'),
  getCarbonAnalytics: () => request('/analytics/carbon'),

  // Forecast & Anomalies
  getForecast: (horizonHours = 24) => request(`/forecast?horizonHours=${horizonHours}`),
  getAnomalies: () => request('/anomalies'),
  acknowledgeAnomaly: (id) => request(`/anomalies/${id}/acknowledge`, { method: 'POST' }),
  resolveAnomaly: (id) => request(`/anomalies/${id}/resolve`, { method: 'POST' }),

  // Optimization & Recommendations
  runOptimization: () => request('/optimization/run', { method: 'POST' }),
  getRecommendations: () => request('/optimization/recommendations'),
  approveRecommendation: (id) => request(`/optimization/recommendations/${id}/approve`, { method: 'POST' }),
  rejectRecommendation: (id) => request(`/optimization/recommendations/${id}/reject`, { method: 'POST' }),

  // Savings Verification
  getSavingsBaseline: () => request('/savings/baseline'),
  getVerifiedSavings: () => request('/savings/verified'),
  getSavingsBreakdown: () => request('/savings/breakdown'),

  // Reports
  getDailyReport: () => request('/reports/daily'),
  getMonthlyReport: () => request('/reports/monthly'),
  getExportCsvUrl: () => `${API_BASE}/reports/export/csv`,

  // Simulator
  getSimulatorState: () => request('/simulator/state'),
  setSimulatorScenario: (scenario) => 
    request('/simulator/scenario', { method: 'POST', body: JSON.stringify({ scenario }) }),
  triggerSimulatorTick: () => request('/simulator/tick', { method: 'POST' }),
};
