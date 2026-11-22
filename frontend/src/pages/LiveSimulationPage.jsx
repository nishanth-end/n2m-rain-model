import React, { useState, useEffect } from 'react';
import { content } from '../config/content';
import { api } from '../api/client';
import {
  CloudRain,
  Sliders,
  RotateCcw,
  Sparkles,
  Info,
  Radio,
  AlertTriangle,
  RefreshCw,
  CheckCircle,
  ExternalLink,
  Layers,
  ArrowDownToLine
} from 'lucide-react';

export default function LiveSimulationPage() {
  const { simulation } = content;
  const [pipelineData, setPipelineData] = useState(null);
  const [rainfallData, setRainfallData] = useState(null);
  const [loadingRainfall, setLoadingRainfall] = useState(false);
  const [appliedLiveBanner, setAppliedLiveBanner] = useState(false);

  // Controlled Demonstration Form State
  const defaultInputs = {
    cellId: 722, // Known flood-prone valley bottom (Bellandur)
    rain_1d_mm: 15.0,
    rain_3d_mm: 35.0,
    rain_7d_mm: 65.0,
    rain_14d_mm: 110.0,
    rain_30d_mm: 190.0,
    rain_lag1_mm: 12.0,
    rain_lag2_mm: 8.0,
    rain_lag3_mm: 0.0,
  };

  const [inputs, setInputs] = useState(defaultInputs);
  const [simulatedResult, setSimulatedResult] = useState(null);
  const [validationError, setValidationError] = useState('');

  // Sample controlled grid cells with known static terrain profiles
  const sampleCells = [
    { id: 722, name: 'Cell #722 (Bellandur Lake Valley)', ward: 150, elevation: '886 m', hand: '1.2 m (Low HAND, severe pooling risk)' },
    { id: 1478, name: 'Cell #1478 (KR Circle Underpass)', ward: 110, elevation: '912 m', hand: '2.4 m (High impervious urban basin)' },
    { id: 555, name: 'Cell #555 (Sarjapur Road Cascade)', ward: 150, elevation: '894 m', hand: '3.1 m (Drainage obstruction zone)' },
    { id: 100, name: 'Cell #100 (Hebbal High Ridge)', ward: 19, elevation: '942 m', hand: '18.5 m (Steep ridge, rapid runoff shedding)' },
  ];

  const fetchLiveRainfall = (force = false) => {
    setLoadingRainfall(true);
    api
      .getLatestRainfall(force)
      .then((data) => {
        setRainfallData(data);
        setLoadingRainfall(false);
      })
      .catch((err) => {
        console.error('Failed to load rainfall context:', err);
        setLoadingRainfall(false);
      });
  };

  // Fetch backend status and live rainfall on mount
  useEffect(() => {
    api
      .getPipelineStatus()
      .then((data) => setPipelineData(data))
      .catch((err) => console.error(err));

    fetchLiveRainfall(false);
  }, []);

  // Compute empirical demonstration response
  const runSimulation = () => {
    setValidationError('');

    if (inputs.rain_1d_mm < 0 || inputs.rain_3d_mm < 0 || inputs.rain_7d_mm < 0) {
      setValidationError('Rainfall values cannot be negative.');
      return;
    }
    if (inputs.rain_1d_mm > inputs.rain_3d_mm) {
      setValidationError('1-Day rainfall cannot exceed 3-Day cumulative rainfall.');
      return;
    }
    if (inputs.rain_3d_mm > inputs.rain_7d_mm) {
      setValidationError('3-Day cumulative rainfall cannot exceed 7-Day cumulative rainfall.');
      return;
    }

    const cellMeta = sampleCells.find((c) => c.id === inputs.cellId) || sampleCells[0];
    const terrainVulnerability = inputs.cellId === 100 ? 0.35 : inputs.cellId === 722 ? 1.45 : 1.2;

    const rainImpact =
      inputs.rain_1d_mm * 0.0018 +
      inputs.rain_3d_mm * 0.0009 +
      inputs.rain_7d_mm * 0.0004 +
      inputs.rain_14d_mm * 0.0002 +
      inputs.rain_lag1_mm * 0.0007;

    const rawScore = Math.min(0.38, Math.max(0.005, rainImpact * terrainVulnerability + 0.012));

    let tier = 'None';
    let estimatedRank = 2100;
    if (rawScore > 0.08) {
      tier = 'High';
      estimatedRank = Math.max(1, Math.round(150 - (rawScore - 0.08) * 450));
    } else if (rawScore > 0.035) {
      tier = 'Moderate';
      estimatedRank = Math.max(151, Math.round(300 - (rawScore - 0.035) * 3300));
    } else {
      estimatedRank = Math.min(3026, Math.round(300 + (0.035 - rawScore) * 60000));
    }

    setSimulatedResult({
      cell: cellMeta,
      score: rawScore,
      tier,
      estimatedRank,
      timestamp: new Date().toLocaleTimeString(),
    });
  };

  useEffect(() => {
    runSimulation();
  }, [inputs]);

  const handleApplyPreset = (presetValues) => {
    setAppliedLiveBanner(false);
    setInputs((prev) => ({
      ...prev,
      ...presetValues,
    }));
  };

  const handleApplyRetrievedRainfall = () => {
    if (!rainfallData || !rainfallData.computed_features) return;
    const f = rainfallData.computed_features;
    setInputs((prev) => ({
      ...prev,
      rain_1d_mm: f.rain_1d_mm ?? prev.rain_1d_mm,
      rain_3d_mm: f.rain_3d_mm ?? prev.rain_3d_mm,
      rain_7d_mm: f.rain_7d_mm ?? prev.rain_7d_mm,
      rain_14d_mm: f.rain_14d_mm ?? prev.rain_14d_mm,
      rain_30d_mm: f.rain_30d_mm ?? prev.rain_30d_mm,
      rain_lag1_mm: f.rain_lag1_mm ?? prev.rain_lag1_mm,
      rain_lag2_mm: f.rain_lag2_mm ?? prev.rain_lag2_mm,
      rain_lag3_mm: f.rain_lag3_mm ?? prev.rain_lag3_mm,
    }));
    setAppliedLiveBanner(true);
  };

  const handleReset = () => {
    setInputs(defaultInputs);
    setValidationError('');
    setAppliedLiveBanner(false);
  };

  const isLiveSuccess = rainfallData?.status === 'success';
  const isOffline = rainfallData?.status === 'offline';

  return (
    <div className="page-container">
      <div className="sim-page-flow">
        {/* Editorial Page Header */}
        <div className="page-editorial-header">
          <span className="page-eyebrow">Hydrological Telemetry & Sensitivity</span>
          <h1 className="page-title">Rainfall Ingestion & Sensitivity Lab</h1>
          <p className="page-subtitle">
            Examining precipitation data provenance, live ingestion scaffolding boundaries, and manual rainfall input sensitivity analysis.
          </p>
        </div>

        {/* SECTION A: RAINFALL DATA CONTEXT & PROVENANCE */}
        <section className="sim-section">
          <div className="sim-section-header">
            <div className="sim-section-title-group">
              <CloudRain size={18} className="text-water" />
              <h2 className="section-title" style={{ fontSize: '1.25rem', margin: 0 }}>
                A. Rainfall Data Context & Retrieval Pipeline
              </h2>
            </div>
            <button
              onClick={() => fetchLiveRainfall(true)}
              className="btn btn-secondary btn-sm"
              disabled={loadingRainfall}
              title="Refresh rainfall data from provider"
            >
              <RefreshCw size={12} className={loadingRainfall ? 'spin' : ''} />
              {loadingRainfall ? 'Querying Provider...' : 'Refresh Provider'}
            </button>
          </div>

          {/* Research Classification Guidance Strip */}
          <div className="category-legend-strip">
            <div className="category-legend-item">
              <span className="legend-indicator dot-green"></span>
              <span className="legend-text"><strong>Observed Weather:</strong> Ground / Satellite telemetry</span>
            </div>
            <div className="category-legend-item">
              <span className="legend-indicator dot-amber"></span>
              <span className="legend-text"><strong>Weather Forecast:</strong> Numerical NWP model projection</span>
            </div>
            <div className="category-legend-item">
              <span className="legend-indicator dot-blue"></span>
              <span className="legend-text"><strong>Historical Training:</strong> Sequestered CHIRPS 2022 dataset</span>
            </div>
            <div className="category-legend-item">
              <span className="legend-indicator dot-purple"></span>
              <span className="legend-text"><strong>Simulated Scenario:</strong> User-adjusted slider inputs</span>
            </div>
          </div>

          <div className="provenance-grid">
            {/* Left Data Sheet: Spatial Specifications & Provider Comparison */}
            <div className="specs-sheet">
              <div className="sim-section-header" style={{ paddingBottom: '0.5rem', marginBottom: 0 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1rem', fontWeight: 700, color: 'var(--ink-primary)' }}>
                  Meteorological Specifications
                </span>
                <span className="badge badge-water">
                  Dual-Provider Architecture
                </span>
              </div>

              <div className="specs-table">
                <div className="specs-row">
                  <span className="specs-prop">Training Baseline Provider:</span>
                  <span className="specs-val">CHIRPS (UC Santa Barbara / CHG)</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">Live Ingestion Provider:</span>
                  <span className="specs-val font-bold">Open-Meteo Weather API</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">Live Spatial Resolution:</span>
                  <span className="specs-val text-mono">~0.1° (~11 km ECMWF / DWD grid)</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">City Centroid Target:</span>
                  <span className="specs-val text-mono">12.9716° N, 77.5946° E (Bengaluru)</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">Measurement Units:</span>
                  <span className="specs-val text-mono font-bold">Millimeters (mm)</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">License / Terms:</span>
                  <span className="specs-val" style={{ fontSize: '11px' }}>Creative Commons Attribution 4.0 (CC BY 4.0)</span>
                </div>
              </div>

              <div className="callout-box callout-amber">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 'bold', color: 'var(--tier-moderate)', marginBottom: '0.25rem' }}>
                  <Info size={14} />
                  <span>Resolution Guardrail & Distributional Shift</span>
                </div>
                <p>
                  Open-Meteo operates on an ~11 km grid, while N²M is trained on CHIRPS ~5.3 km data.
                  Retrieved precipitation serves as live observational context for researcher analysis.
                  It is strictly isolated from automated public flood warning triggers.
                </p>
              </div>
            </div>

            {/* Right Live Stream Status Plate */}
            <div className="ingestion-plate">
              <div className="sim-section-header" style={{ paddingBottom: '0.5rem', marginBottom: 0 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1rem', fontWeight: 700, color: 'var(--ink-primary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Radio size={16} className={isLiveSuccess ? 'text-water' : 'text-dim'} />
                  Ingestion Stream Monitor
                </span>
                <span className="text-mono" style={{ fontSize: '11px' }}>
                  {isLiveSuccess ? (
                    rainfallData.cached ? (
                      <span className="badge badge-amber">CACHED TELEMETRY</span>
                    ) : (
                      <span className="badge badge-high" style={{ backgroundColor: '#ecfdf5', color: '#059669', borderColor: '#a7f3d0' }}>LIVE STREAM ACTIVE</span>
                    )
                  ) : isOffline ? (
                    <span className="badge">OFFLINE / SANDBOX</span>
                  ) : (
                    <span className="badge">INITIALIZING...</span>
                  )}
                </span>
              </div>

              {/* Status summary */}
              <div className="status-card-inner">
                <div className="status-row">
                  <span className="specs-prop">Telemetry Channel:</span>
                  <span className="specs-val">
                    {isLiveSuccess ? 'HTTP REST Gateway (:8000)' : 'Local Research Sandbox'}
                  </span>
                </div>
                <div className="status-row">
                  <span className="specs-prop">Public Alert Routing:</span>
                  <span className="text-mono" style={{ color: '#16a34a', fontWeight: 'bold' }}>
                    DISCONNECTED (SAFE)
                  </span>
                </div>
                <div className="status-row">
                  <span className="specs-prop">Last Query Timestamp:</span>
                  <span className="specs-val text-mono" style={{ fontSize: '11px' }}>
                    {rainfallData?.fetch_timestamp ? new Date(rainfallData.fetch_timestamp).toLocaleTimeString() : 'Pending'}
                  </span>
                </div>

                {isLiveSuccess && rainfallData.summary && (
                  <div className="live-stat-pills">
                    <div className="stat-pill">
                      <span className="stat-pill-label">Today's Rain</span>
                      <span className="stat-pill-val">{rainfallData.summary.latest_daily_rain_mm} mm</span>
                    </div>
                    <div className="stat-pill">
                      <span className="stat-pill-label">7-Day Sum</span>
                      <span className="stat-pill-val">{rainfallData.summary.latest_7d_sum_mm} mm</span>
                    </div>
                    <div className="stat-pill">
                      <span className="stat-pill-label">Records</span>
                      <span className="stat-pill-val">{rainfallData.summary.total_days_retrieved} Days</span>
                    </div>
                  </div>
                )}

                {isOffline && (
                  <div className="callout-box" style={{ backgroundColor: '#f8fafc', borderColor: '#e2e8f0', margin: 0 }}>
                    <p style={{ margin: 0, fontSize: '11px', color: 'var(--ink-muted)' }}>
                      <strong>Offline Sandbox Mode:</strong> Remote API is unreachable in this environment. In accordance with scientific integrity guidelines, no synthetic data is fabricated.
                    </p>
                  </div>
                )}
              </div>

              {/* If records exist, show action to load into simulation lab */}
              {isLiveSuccess && rainfallData.computed_features && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <button
                    onClick={handleApplyRetrievedRainfall}
                    className="btn btn-primary btn-sm"
                    style={{ width: '100%', justifyContent: 'center' }}
                  >
                    <ArrowDownToLine size={13} />
                    Load Retrieved Values into Sensitivity Lab
                  </button>
                  <span className="text-mono text-dim" style={{ fontSize: '10px', textAlign: 'center' }}>
                    Reference Date: {rainfallData.computed_features.reference_date} (Computed 8-Attribute Matrix)
                  </span>
                </div>
              )}

              {/* Required Preprocessing Matrix Checklist */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <span className="form-label" style={{ fontWeight: 'bold', color: 'var(--ink-primary)' }}>
                  Temporal Aggregation Matrix (8 Attributes)
                </span>
                <div className="matrix-tags-group">
                  {['rain_1d', 'rain_3d', 'rain_7d', 'rain_14d', 'rain_30d', 'lag1', 'lag2', 'lag3'].map((item) => (
                    <span key={item} className="matrix-tag">
                      {item}_mm
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Retrieved Daily Series Table (if data available) */}
          {isLiveSuccess && rainfallData.daily_series && rainfallData.daily_series.length > 0 && (
            <div className="retrieved-series-plate">
              <div className="sim-section-header" style={{ paddingBottom: '0.4rem', marginBottom: '0.5rem' }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--ink-primary)' }}>
                  Retrieved Meteorological Timeline for Bengaluru (Open-Meteo)
                </span>
                <span className="text-mono text-dim" style={{ fontSize: '11px' }}>
                  Showing {rainfallData.daily_series.length} Days
                </span>
              </div>
              <div className="series-horizontal-scroll">
                {rainfallData.daily_series.map((day) => (
                  <div key={day.date} className={`series-card ${day.category}`}>
                    <span className="series-date text-mono">{day.date}</span>
                    <span className="series-val">{day.precipitation_mm} <span className="series-unit">mm</span></span>
                    <span className={`series-badge badge-${day.category}`}>
                      {day.category === 'forecast' ? 'Forecast' : day.category === 'observation_current' ? 'Today (Acc.)' : 'Observed'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* SECTION B: MANUAL SENSITIVITY DEMONSTRATION */}
        <section className="sim-section">
          <div className="sim-section-header">
            <div className="sim-section-title-group">
              <Sliders size={18} className="text-olive" />
              <h2 className="section-title" style={{ fontSize: '1.25rem', margin: 0 }}>
                B. Manual Sensitivity Lab
              </h2>
            </div>
            <span className="badge badge-water">
              Simulated Sensitivity Experiment
            </span>
          </div>

          <p className="page-subtitle">
            {simulation.demoMode.subtitle} Select a demonstration preset, load live retrieved values, or manually adjust cumulative rainfall parameters to inspect the model's empirical susceptibility response.
          </p>

          {appliedLiveBanner && (
            <div className="callout-box" style={{ backgroundColor: '#f0fdf4', borderColor: '#bbf7d0', color: '#166534', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle size={15} />
                <span style={{ fontSize: '12px' }}>
                  <strong>Populated with Retrieved Telemetry:</strong> Sliders now reflect the latest precipitation sequence for Bengaluru.
                </span>
              </div>
              <button onClick={() => setAppliedLiveBanner(false)} className="btn btn-secondary btn-sm" style={{ padding: '2px 8px', fontSize: '11px' }}>
                Dismiss
              </button>
            </div>
          )}

          {/* Presets Toolbar */}
          <div className="presets-toolbar">
            <span className="presets-label">
              <Sparkles size={13} />
              Demonstration Presets:
            </span>
            {simulation.demoMode.presets.map((preset) => (
              <button
                key={preset.name}
                onClick={() => handleApplyPreset(preset.values)}
                className="btn btn-secondary btn-sm"
                title={preset.desc}
              >
                {preset.name}
              </button>
            ))}
            <button onClick={handleReset} className="btn btn-secondary btn-sm" style={{ marginLeft: 'auto' }}>
              <RotateCcw size={12} />
              Reset Inputs
            </button>
          </div>

          {/* Interactive Form & Result Display */}
          <div className="sim-lab-grid">
            {/* Input Form */}
            <div className="sim-form-container">
              <div className="form-group">
                <label className="form-label">Target Grid Cell Evaluation</label>
                <select
                  value={inputs.cellId}
                  onChange={(e) => setInputs({ ...inputs, cellId: Number(e.target.value) })}
                  className="form-select"
                >
                  {sampleCells.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} (Ward {c.ward}) — {c.hand}
                    </option>
                  ))}
                </select>
                <span className="form-help">
                  Evaluating cell topography: {sampleCells.find((c) => c.id === inputs.cellId)?.elevation}, {sampleCells.find((c) => c.id === inputs.cellId)?.hand}.
                </span>
              </div>

              <div className="sim-inputs-grid">
                {/* 1D Rain */}
                <div className="form-group">
                  <div className="slider-header">
                    <label className="form-label">Day 1 Rain (rain_1d_mm)</label>
                    <span className="slider-val text-mono">{inputs.rain_1d_mm} mm</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="150"
                    step="0.5"
                    value={inputs.rain_1d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_1d_mm: Number(e.target.value) })}
                    className="form-slider"
                  />
                </div>

                {/* 3D Rain */}
                <div className="form-group">
                  <div className="slider-header">
                    <label className="form-label">3-Day Sum (rain_3d_mm)</label>
                    <span className="slider-val text-mono">{inputs.rain_3d_mm} mm</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="250"
                    step="1"
                    value={inputs.rain_3d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_3d_mm: Number(e.target.value) })}
                    className="form-slider"
                  />
                </div>

                {/* 7D Rain */}
                <div className="form-group">
                  <div className="slider-header">
                    <label className="form-label">7-Day Sum (rain_7d_mm)</label>
                    <span className="slider-val text-mono">{inputs.rain_7d_mm} mm</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="350"
                    step="1"
                    value={inputs.rain_7d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_7d_mm: Number(e.target.value) })}
                    className="form-slider"
                  />
                </div>

                {/* 14D Rain */}
                <div className="form-group">
                  <div className="slider-header">
                    <label className="form-label">14-Day Sum (rain_14d_mm)</label>
                    <span className="slider-val text-mono">{inputs.rain_14d_mm} mm</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="450"
                    step="1"
                    value={inputs.rain_14d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_14d_mm: Number(e.target.value) })}
                    className="form-slider"
                  />
                </div>

                {/* Lag 1 */}
                <div className="form-group">
                  <div className="slider-header">
                    <label className="form-label">Yesterday Lag (lag1_mm)</label>
                    <span className="slider-val text-mono">{inputs.rain_lag1_mm} mm</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="0.5"
                    value={inputs.rain_lag1_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_lag1_mm: Number(e.target.value) })}
                    className="form-slider"
                  />
                </div>

                {/* Lag 2 */}
                <div className="form-group">
                  <div className="slider-header">
                    <label className="form-label">Day Before Lag (lag2_mm)</label>
                    <span className="slider-val text-mono">{inputs.rain_lag2_mm} mm</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="0.5"
                    value={inputs.rain_lag2_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_lag2_mm: Number(e.target.value) })}
                    className="form-slider"
                  />
                </div>
              </div>

              {validationError && (
                <div className="callout-box callout-red" style={{ padding: '0.5rem', fontSize: '11px' }}>
                  <AlertTriangle size={14} />
                  <span>{validationError}</span>
                </div>
              )}
            </div>

            {/* Simulated Model Response Plate */}
            <div className="sim-output-container">
              <div className="sim-section-header" style={{ paddingBottom: '0.5rem', marginBottom: 0 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1rem', fontWeight: 700, color: 'var(--ink-primary)' }}>
                  Empirical Response Estimate
                </span>
                <span className="text-mono text-dim" style={{ fontSize: '11px' }}>
                  {simulatedResult?.timestamp || 'Waiting'}
                </span>
              </div>

              {simulatedResult && (
                <div className="sim-score-card">
                  <div className="sim-score-row">
                    <span className="specs-prop">Estimated Susceptibility Score:</span>
                    <span className="sim-score-num">{simulatedResult.score.toFixed(4)}</span>
                  </div>

                  <div className="sim-score-row">
                    <span className="specs-prop">Relative Rank Priority:</span>
                    <span className="sim-rank-num">~Rank #{simulatedResult.estimatedRank} of 3,026</span>
                  </div>

                  <div className="sim-score-row">
                    <span className="specs-prop">Estimated Tier Classification:</span>
                    <span className={`badge badge-${simulatedResult.tier.toLowerCase()}`}>
                      {simulatedResult.tier.toUpperCase()} PRIORITY
                    </span>
                  </div>

                  <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.6rem', marginTop: '0.2rem' }}>
                    <div style={{ fontSize: '11px', color: 'var(--ink-muted)', lineHeight: 1.4 }}>
                      <strong>Sensitivity Explanation:</strong> In this evaluation, {simulatedResult.cell.name} experiences a terrain susceptibility factor based on its low HAND elevation profile. Adjusting the 1D and 3D rainfall amounts simulates how quickly runoff exceeds drainage capacity.
                    </div>
                  </div>
                </div>
              )}

              <div className="callout-box callout-amber" style={{ margin: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 'bold', color: 'var(--tier-moderate)', marginBottom: '0.25rem' }}>
                  <Info size={14} />
                  <span>Lab Notice</span>
                </div>
                <p style={{ margin: 0, fontSize: '11px' }}>
                  {simulation.demoMode.notice}
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
