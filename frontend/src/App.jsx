import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';

// Pages
import DashboardPage from './pages/DashboardPage';
import LiveEnergyPage from './pages/LiveEnergyPage';
import HistoricalPage from './pages/HistoricalPage';
import ForecastPage from './pages/ForecastPage';
import AnomaliesPage from './pages/AnomaliesPage';
import OptimizationPage from './pages/OptimizationPage';
import DevicesPage from './pages/DevicesPage';
import RenewablePage from './pages/RenewablePage';
import AlertsPage from './pages/AlertsPage';
import SavingsPage from './pages/SavingsPage';
import ReportsPage from './pages/ReportsPage';
import SettingsSimulatorPage from './pages/SettingsSimulatorPage';

import { api } from './api/client';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [currentScenario, setCurrentScenario] = useState('normal');
  const [isRefreshing, setIsRefreshing] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Core Data State
  const [telemetry, setTelemetry] = useState(null);
  const [devices, setDevices] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [savings, setSavings] = useState(null);
  const [sources, setSources] = useState(null);

  const refreshTimerRef = useRef(null);

  // Initial load
  useEffect(() => {
    fetchInitialData();
  }, []);

  // Periodic polling for real-time telemetry (every 5 seconds)
  useEffect(() => {
    if (isRefreshing) {
      refreshTimerRef.current = setInterval(() => {
        pollLiveData();
      }, 5000);
    } else {
      if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);
    }
    return () => {
      if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);
    };
  }, [isRefreshing]);

  const fetchInitialData = async () => {
    await Promise.all([
      pollLiveData(),
      loadForecast(),
      loadRecommendations(),
      loadAnomalies(),
      loadSavings(),
      loadSimulatorState()
    ]);
  };

  const pollLiveData = async () => {
    try {
      const [tRes, dRes, sRes] = await Promise.all([
        api.getLiveTelemetry(),
        api.getDevices(),
        api.getSourcesAnalytics()
      ]);

      if (tRes.success) setTelemetry(tRes.data);
      if (dRes.success) setDevices(dRes.data);
      if (sRes.success) setSources(sRes.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.warn('Telemetry polling notice:', err.message);
    }
  };

  const loadForecast = async () => {
    try {
      const res = await api.getForecast(24);
      if (res.success) setForecast(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadRecommendations = async () => {
    try {
      const res = await api.getRecommendations();
      if (res.success) setRecommendations(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadAnomalies = async () => {
    try {
      const res = await api.getAnomalies();
      if (res.success) setAnomalies(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadSavings = async () => {
    try {
      const res = await api.getVerifiedSavings();
      if (res.success) setSavings(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadSimulatorState = async () => {
    try {
      const res = await api.getSimulatorState();
      if (res.success && res.data.currentScenario) {
        setCurrentScenario(res.data.currentScenario);
      }
    } catch (e) {
      console.warn(e);
    }
  };

  // Scenario Change Handler
  const handleScenarioChange = async (newScenario) => {
    setCurrentScenario(newScenario);
    try {
      await api.setSimulatorScenario(newScenario);
      await pollLiveData();
      await loadAnomalies();
      await loadForecast();
    } catch (e) {
      alert(`Scenario Error: ${e.message}`);
    }
  };

  // Manual Tick Step
  const handleManualTick = async () => {
    try {
      await api.triggerSimulatorTick();
      await pollLiveData();
    } catch (e) {
      console.error(e);
    }
  };

  // Approve Prescriptive Recommendation
  const handleApproveRecommendation = async (recId) => {
    try {
      const res = await api.approveRecommendation(recId);
      if (res.success) {
        await loadRecommendations();
        await pollLiveData();
        await loadSavings();
      }
    } catch (e) {
      alert(`Approval error: ${e.message}`);
    }
  };

  // Acknowledge Anomaly
  const handleAcknowledgeAnomaly = async (anomId) => {
    try {
      await api.acknowledgeAnomaly(anomId);
      await loadAnomalies();
    } catch (e) {
      console.error(e);
    }
  };

  // Resolve Anomaly
  const handleResolveAnomaly = async (anomId) => {
    try {
      await api.resolveAnomaly(anomId);
      await loadAnomalies();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg)' }}>
      {/* Top Navigation & Context Bar */}
      <Header
        currentScenario={currentScenario}
        onScenarioChange={handleScenarioChange}
        onManualTick={handleManualTick}
        isRefreshing={isRefreshing}
        onRefreshToggle={() => setIsRefreshing(prev => !prev)}
        lastUpdated={lastUpdated}
      />

      {/* Main Workspace: Sidebar + Content */}
      <div style={{ display: 'flex', flex: 1 }}>
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          alertCount={anomalies.filter(a => a.status === 'open').length}
          recommendationCount={recommendations.filter(r => r.status === 'pending').length}
        />

        <main style={{ flex: 1, padding: '24px', overflowY: 'auto', maxWidth: '1440px', margin: '0 auto' }}>
          {currentTab === 'dashboard' && (
            <DashboardPage
              telemetry={telemetry}
              forecast={forecast}
              recommendations={recommendations}
              savings={savings}
              sources={sources}
              onApproveRecommendation={handleApproveRecommendation}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'live' && (
            <LiveEnergyPage
              devices={telemetry?.devices || devices}
              onSelectDevice={(id) => setCurrentTab('devices')}
            />
          )}

          {currentTab === 'historical' && (
            <HistoricalPage />
          )}

          {currentTab === 'forecast' && (
            <ForecastPage onNavigate={setCurrentTab} />
          )}

          {currentTab === 'anomalies' && (
            <AnomaliesPage
              anomalies={anomalies}
              onAcknowledge={handleAcknowledgeAnomaly}
              onResolve={handleResolveAnomaly}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'optimization' && (
            <OptimizationPage
              recommendations={recommendations}
              onApproveRecommendation={handleApproveRecommendation}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'devices' && (
            <DevicesPage
              devices={devices}
              onCommandSuccess={pollLiveData}
            />
          )}

          {currentTab === 'renewable' && (
            <RenewablePage
              telemetry={telemetry}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'alerts' && (
            <AlertsPage />
          )}

          {currentTab === 'savings' && (
            <SavingsPage />
          )}

          {currentTab === 'reports' && (
            <ReportsPage />
          )}

          {currentTab === 'simulator' && (
            <SettingsSimulatorPage
              currentScenario={currentScenario}
              onScenarioChange={handleScenarioChange}
              onManualTick={handleManualTick}
              onNavigate={setCurrentTab}
            />
          )}
        </main>
      </div>
    </div>
  );
}
