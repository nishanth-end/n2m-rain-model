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
  AlertTriangle
} from 'lucide-react';

export default function LiveSimulationPage() {
  const { simulation } = content;
  const [pipelineData, setPipelineData] = useState(null);

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

  // Fetch backend pipeline status
  useEffect(() => {
    api
      .getPipelineStatus()
      .then((data) => setPipelineData(data))
      .catch((err) => console.error(err));
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
  }, []);

  const handleApplyPreset = (presetValues) => {
    setInputs((prev) => ({
      ...prev,
      ...presetValues,
    }));
  };

  const handleReset = () => {
    setInputs(defaultInputs);
    setValidationError('');
  };

  return (
    <div className="page-container">
      <div className="sim-page-flow">
        {/* Editorial Page Header */}
        <div className="page-editorial-header">
          <span className="page-eyebrow">Interactive Sensitivity Lab</span>
          <h1 className="page-title">Live Data Status & Simulation Lab</h1>
          <p className="page-subtitle">
            Examining precipitation data provenance, live ingestion scaffolding boundaries, and manual rainfall input sensitivity analysis.
          </p>
        </div>

        {/* SECTION A: RAINFALL DATA CONTEXT */}
        <section className="sim-section">
          <div className="sim-section-header">
            <div className="sim-section-title-group">
              <CloudRain size={18} className="text-water" />
              <h2 className="section-title" style={{ fontSize: '1.25rem', margin: 0 }}>
                A. Rainfall Data Context & Provenance
              </h2>
            </div>
          </div>

          <div className="provenance-grid">
            {/* Left Data Sheet */}
            <div className="specs-sheet">
              <div className="sim-section-header" style={{ paddingBottom: '0.5rem', marginBottom: 0 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1rem', fontWeight: 700, color: 'var(--ink-primary)' }}>
                  Precipitation Specifications
                </span>
                <span className="badge badge-water">
                  CHIRPS Satellite-Gauge Gridded
                </span>
              </div>

              <div className="specs-table">
                <div className="specs-row">
                  <span className="specs-prop">Data Provider:</span>
                  <span className="specs-val">{simulation.rainfallContext.provider}</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">Spatial Grid Resolution:</span>
                  <span className="specs-val text-mono">{simulation.rainfallContext.resolution}</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">Temporal Cadence:</span>
                  <span className="specs-val">{simulation.rainfallContext.temporalCadence}</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">Spatial Boundary Linkage:</span>
                  <span className="specs-val">{simulation.rainfallContext.coverage}</span>
                </div>
                <div className="specs-row">
                  <span className="specs-prop">Measurement Unit:</span>
                  <span className="specs-val text-mono font-bold">Millimeters (mm)</span>
                </div>
              </div>

              <div className="callout-box callout-amber">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 'bold', color: 'var(--tier-moderate)', marginBottom: '0.25rem' }}>
                  <Info size={14} />
                  <span>Model Calibration & Provider Guardrail</span>
                </div>
                <p>{simulation.rainfallContext.statusNotice}</p>
              </div>
            </div>

            {/* Right Ingestion Scaffolding Plate */}
            <div className="ingestion-plate">
              <div className="sim-section-header" style={{ paddingBottom: '0.5rem', marginBottom: 0 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1rem', fontWeight: 700, color: 'var(--ink-primary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Radio size={16} className="text-dim" />
                  Live Ingestion State
                </span>
                <span className="text-mono text-dim" style={{ fontSize: '11px' }}>
                  Isolated Scaffolding
                </span>
              </div>

              <div className="status-card-inner">
                <div className="status-row">
                  <span className="specs-prop">Operational Stream:</span>
                  <span className="badge">
                    {pipelineData?.status?.toUpperCase() || 'DISABLED BY DEFAULT'}
                  </span>
                </div>

                <div className="status-row">
                  <span className="specs-prop">Public Alert Routing:</span>
                  <span className="text-mono" style={{ color: '#16a34a', fontWeight: 'bold' }}>
                    DISCONNECTED (SAFE)
                  </span>
                </div>

                <p style={{ fontSize: '11px', color: 'var(--ink-muted)', lineHeight: 1.4, borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem', margin: 0 }}>
                  Real-time automated alerting is strictly prevented by system architecture. Historical replay mode functions completely offline.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <span className="form-label" style={{ fontWeight: 'bold', color: 'var(--ink-primary)' }}>
                  Required Preprocessing Matrix (8 Attributes)
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
            {simulation.demoMode.subtitle} Select a demonstration preset or manually adjust cumulative rainfall parameters to inspect the model's empirical susceptibility response.
          </p>

          {/* Presets Toolbar */}
          <div className="presets-toolbar">
            <span className="presets-label">
              <Sparkles size={13} className="text-water" />
              Load Presets:
            </span>
            {simulation.demoMode.presets.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => handleApplyPreset(preset.values)}
                className="btn-secondary btn-sm"
                title={preset.desc}
              >
                {preset.name}
              </button>
            ))}
            <button
              onClick={handleReset}
              className="btn-ghost btn-sm"
              style={{ marginLeft: 'auto' }}
              title="Reset to default inputs"
            >
              <RotateCcw size={12} />
              <span>Reset</span>
            </button>
          </div>

          {validationError && (
            <div className="callout-box callout-danger" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontFamily: 'var(--font-mono)' }}>
              <AlertTriangle size={14} />
              <span>{validationError}</span>
            </div>
          )}

          {/* Form and Output 2-Col Grid */}
          <div className="sim-lab-grid">
            {/* Input Form Column */}
            <div className="sim-form-container">
              <div className="sim-section-header" style={{ paddingBottom: '0.4rem', marginBottom: 0 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--ink-primary)' }}>
                  1. Select Reference Spatial Cell
                </span>
                <span className="text-mono text-dim" style={{ fontSize: '11px' }}>Fixed Terrain Profile</span>
              </div>

              <div>
                <select
                  value={inputs.cellId}
                  onChange={(e) => setInputs({ ...inputs, cellId: parseInt(e.target.value, 10) })}
                  className="select-control"
                >
                  {sampleCells.map((cell) => (
                    <option key={cell.id} value={cell.id}>
                      {cell.name} — Elev: {cell.elevation}, {cell.hand}
                    </option>
                  ))}
                </select>
              </div>

              <div className="sim-section-header" style={{ paddingBottom: '0.4rem', marginBottom: 0 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--ink-primary)' }}>
                  2. Enter Cumulative & Lagged Precipitation (mm)
                </span>
              </div>

              <div className="sim-inputs-grid">
                <div className="form-group">
                  <label className="form-label">1-Day Rainfall (rain_1d_mm):</label>
                  <input
                    type="number"
                    min="0"
                    max="300"
                    step="0.5"
                    value={inputs.rain_1d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_1d_mm: parseFloat(e.target.value) || 0 })}
                    className="input-control"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">3-Day Cumulative (rain_3d_mm):</label>
                  <input
                    type="number"
                    min="0"
                    max="500"
                    step="0.5"
                    value={inputs.rain_3d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_3d_mm: parseFloat(e.target.value) || 0 })}
                    className="input-control"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">7-Day Cumulative (rain_7d_mm):</label>
                  <input
                    type="number"
                    min="0"
                    max="700"
                    step="1"
                    value={inputs.rain_7d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_7d_mm: parseFloat(e.target.value) || 0 })}
                    className="input-control"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">14-Day Cumulative (rain_14d_mm):</label>
                  <input
                    type="number"
                    min="0"
                    max="1000"
                    step="1"
                    value={inputs.rain_14d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_14d_mm: parseFloat(e.target.value) || 0 })}
                    className="input-control"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">30-Day Cumulative (rain_30d_mm):</label>
                  <input
                    type="number"
                    min="0"
                    max="1500"
                    step="1"
                    value={inputs.rain_30d_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_30d_mm: parseFloat(e.target.value) || 0 })}
                    className="input-control"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Lag 1 Day Prior (rain_lag1_mm):</label>
                  <input
                    type="number"
                    min="0"
                    max="200"
                    step="0.5"
                    value={inputs.rain_lag1_mm}
                    onChange={(e) => setInputs({ ...inputs, rain_lag1_mm: parseFloat(e.target.value) || 0 })}
                    className="input-control"
                  />
                </div>
              </div>

              <button
                onClick={runSimulation}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
              >
                Evaluate Simulated Susceptibility
              </button>
            </div>

            {/* Simulation Output Plate */}
            <div className="sim-output-container">
              <div className="sim-section-header" style={{ paddingBottom: '0.4rem', marginBottom: 0 }}>
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--ink-primary)' }}>
                  Simulated Sensitivity Output
                </span>
                <span className="text-mono text-dim" style={{ fontSize: '11px' }}>
                  Updated: {simulatedResult?.timestamp || '—'}
                </span>
              </div>

              {simulatedResult ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                  <div className="sim-score-card">
                    <div className="sim-score-row">
                      <span className="form-label">Assigned Tier:</span>
                      <span
                        className={
                          simulatedResult.tier === 'High'
                            ? 'badge badge-high'
                            : simulatedResult.tier === 'Moderate'
                            ? 'badge badge-mod'
                            : 'badge badge-baseline'
                        }
                      >
                        {simulatedResult.tier.toUpperCase()} TIER
                      </span>
                    </div>

                    <div className="sim-score-row">
                      <span className="form-label">Susceptibility Score:</span>
                      <span className="sim-score-num">
                        {simulatedResult.score.toFixed(4)}
                      </span>
                    </div>

                    <div className="sim-score-row" style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem' }}>
                      <span className="form-label">Estimated City Rank:</span>
                      <span className="sim-rank-num">
                        ~#{simulatedResult.estimatedRank} <span style={{ fontSize: '11px', color: 'var(--ink-muted)', fontWeight: 'normal' }}>/ 3,026</span>
                      </span>
                    </div>
                  </div>

                  <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '0.25rem', fontFamily: 'var(--font-mono)', color: 'var(--ink-muted)' }}>
                    <div>Target: <strong style={{ color: 'var(--ink-primary)' }}>{simulatedResult.cell.name}</strong></div>
                    <div>Topography: {simulatedResult.cell.hand}</div>
                  </div>

                  <div className="callout-box callout-amber" style={{ fontSize: '11px' }}>
                    <strong>Academic Disclaimer:</strong> This sensitivity calculation is an empirical demonstration proxy. Scores represent relative prioritization for the specified rainfall and terrain vector, not hydraulic flood prediction.
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--ink-muted)', fontSize: '12px' }}>
                  Adjust parameters and evaluate susceptibility.
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
