import React, { useState, useEffect, useCallback } from 'react';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import FloodMapPage from './pages/FloodMapPage';
import LiveSimulationPage from './pages/LiveSimulationPage';
import TelegramPage from './pages/TelegramPage';
import CreatorsPage from './pages/CreatorsPage';
import { api } from './api/client';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // home, map, simulation, telegram, creators
  const [dates, setDates] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [summary, setSummary] = useState(null);
  const [cells, setCells] = useState([]);
  const [selectedCell, setSelectedCell] = useState(null);

  const [apiStatus, setApiStatus] = useState('checking'); // online, offline, checking
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize: Check backend health and retrieve available replay dates
  const initApp = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setApiStatus('checking');

    try {
      await api.getHealth();
      setApiStatus('online');

      const datesRes = await api.getDates();
      const dateList = datesRes.dates || [];
      setDates(dateList);

      // Default to 2022-09-08 (peak September cloudburst day) or latest date
      const initialDate = dateList.includes('2022-09-08')
        ? '2022-09-08'
        : dateList[dateList.length - 1] || '';
      setSelectedDate(initialDate);
    } catch (err) {
      console.error('API connection error:', err);
      setApiStatus('offline');
      setError(
        `Unable to connect to the N²M Flood Prediction Model backend at ${api.getBaseUrl()}. Please ensure the FastAPI server is running.`
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    initApp();
  }, [initApp]);

  // Fetch Risk Cells & Summary when selectedDate changes
  useEffect(() => {
    if (!selectedDate) return;

    let isCurrent = true;
    setIsLoading(true);

    Promise.all([api.getRisk(selectedDate), api.getSummary(selectedDate)])
      .then(([riskRes, summaryRes]) => {
        if (!isCurrent) return;
        const cellData = riskRes.cells || [];
        setCells(cellData);
        setSummary(summaryRes);

        // Keep selected cell updated if active
        setSelectedCell((prev) => {
          if (!prev) return null;
          const updated = cellData.find((c) => c.cell_id === prev.cell_id);
          return updated || prev;
        });
      })
      .catch((err) => {
        if (!isCurrent) return;
        console.error(`Error loading replay data for ${selectedDate}:`, err);
        setError(`Failed to retrieve replay data for ${selectedDate}: ${err.message}`);
      })
      .finally(() => {
        if (isCurrent) setIsLoading(false);
      });

    return () => {
      isCurrent = false;
    };
  }, [selectedDate]);

  return (
    <div className="app-shell">
      {/* Persistent Academic Top Navigation */}
      <Navigation
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        apiStatus={apiStatus}
      />

      {/* Main View Router */}
      <main className="app-main">
        {/* Offline Warning Notice */}
        {error && (
          <div className="page-container" style={{ paddingBottom: 0 }}>
            <div className="callout-box callout-danger" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{error}</span>
              </div>
              <button
                onClick={initApp}
                className="btn-secondary btn-sm"
                style={{ flexShrink: 0 }}
              >
                <RefreshCw size={12} /> Retry
              </button>
            </div>
          </div>
        )}

        {/* Tab 1: Home Landing Page */}
        {activeTab === 'home' && (
          <HomePage
            onNavigateToMap={() => setActiveTab('map')}
            onNavigateToSimulation={() => setActiveTab('simulation')}
          />
        )}

        {/* Tab 2: Interactive Flood Map */}
        {activeTab === 'map' && (
          <FloodMapPage
            dates={dates}
            selectedDate={selectedDate}
            onSelectDate={setSelectedDate}
            cells={cells}
            summary={summary}
            selectedCell={selectedCell}
            onSelectCell={setSelectedCell}
            isLoading={isLoading}
          />
        )}

        {/* Tab 3: Live Data Context & Simulation Lab */}
        {activeTab === 'simulation' && <LiveSimulationPage />}

        {/* Tab 4: Telegram Demonstration Bot */}
        {activeTab === 'telegram' && (
          <TelegramPage dates={dates} selectedDate={selectedDate} />
        )}

        {/* Tab 5: Maintainers & Creators */}
        {activeTab === 'creators' && <CreatorsPage />}
      </main>

      {/* Shared Cartographic Footer */}
      <Footer onSelectTab={setActiveTab} />
    </div>
  );
}
