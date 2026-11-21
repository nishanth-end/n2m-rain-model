import React from 'react';
import { content } from '../config/content';
import { ArrowRight, Compass, Layers, Cpu, AlertTriangle, Database } from 'lucide-react';

export default function HomePage({ onNavigateToMap, onNavigateToSimulation }) {
  const { home } = content;

  return (
    <div className="page-container">
      <div className="home-flow">
        {/* 1. EDITORIAL HERO VIEWPORT */}
        <section className="hero-editorial-viewport">
          <div className="hero-lead-col">
            <div className="hero-tag">
              <Compass size={13} />
              <span>Academic Cartography & Geospatial ML</span>
            </div>

            <h1 className="hero-headline">
              {home.hero.headline}
            </h1>

            <p className="hero-subheadline">
              {home.hero.subheadline}
            </p>

            <div className="hero-actions-row">
              <button
                onClick={onNavigateToMap}
                className="btn-primary"
              >
                <span>{home.hero.ctaPrimary}</span>
                <ArrowRight size={14} />
              </button>

              <button
                onClick={onNavigateToSimulation}
                className="btn-secondary"
              >
                {home.hero.ctaSecondary}
              </button>

              <span className="hero-event-note">
                Historical Replay: September 2022 Monsoon Event
              </span>
            </div>
          </div>

          {/* Cartographic Specimen Plate (Right Hero Column) */}
          <div className="hero-specimen-plate">
            <div className="specimen-header">
              <span className="specimen-header-title">
                <Compass size={12} className="text-water" />
                Bengaluru Spatial Mesh Specimen
              </span>
              <span className="specimen-coordinates">12.97° N, 77.59° E</span>
            </div>

            <div className="specimen-canvas">
              <Compass size={36} className="specimen-compass-icon" />
              <div className="specimen-canvas-title">
                3,026 Discrete Spatial Micro-Catchments
              </div>
              <p className="specimen-canvas-desc">
                Continuous 500m × 500m spatial tessellation across BBMP municipal zones, peripheral lake corridors, and eastern IT clusters.
              </p>
            </div>

            <div className="specimen-footer">
              <button
                onClick={onNavigateToMap}
                className="btn-secondary"
                style={{ width: '100%', justifyContent: 'center' }}
              >
                Inspect Spatial Replay Map
              </button>
            </div>
          </div>
        </section>

        {/* 2. TELEMETRY DATA RIBBON */}
        <section className="telemetry-ribbon">
          {home.statistics.map((stat, idx) => (
            <div key={idx} className="telemetry-cell">
              <span className="telemetry-label">{stat.label}</span>
              <div className="telemetry-value">{stat.value}</div>
              <p className="telemetry-detail">{stat.detail}</p>
            </div>
          ))}
        </section>

        {/* 3. PROBLEM STATEMENT & DATA COUPLING SPLIT */}
        <section className="problem-editorial-split">
          <div className="editorial-article">
            <div className="section-eyebrow">
              <Layers size={13} />
              <span>Hydrological Topography</span>
            </div>

            <h2 className="section-title">
              {home.problemStatement.title}
            </h2>

            <p className="article-body-p">
              {home.problemStatement.content}
            </p>

            <div className="article-pullquote">
              {home.problemStatement.urbanChallenge}
            </div>
          </div>

          <div className="coupling-plate">
            <div className="section-eyebrow">
              <Database size={13} />
              <span>Data Fusion Architecture</span>
            </div>

            <h3 className="coupling-plate-title">
              Multi-Source Coupling Matrix
            </h3>

            <div className="coupling-list">
              <div className="coupling-item">
                <span className="coupling-item-title">Topographic Relief</span>
                <span>SRTM 30m digital elevation, slope gradients, and HAND (Height Above Nearest Drainage).</span>
              </div>

              <div className="coupling-item">
                <span className="coupling-item-title">Drainage & Urban Infrastructure</span>
                <span>OpenStreetMap storm drains (Rajakaluve), lake polygons, and road densities.</span>
              </div>

              <div className="coupling-item">
                <span className="coupling-item-title">Satellite Precipitation</span>
                <span>CHIRPS gridded daily precipitation with 1d, 3d, 7d, 14d, 30d, and lagged vectors.</span>
              </div>
            </div>
          </div>
        </section>

        {/* 4. THREE ENGINEERING PILLARS */}
        <section className="pillars-section">
          <div className="pillars-header-bar">
            <h2 className="section-title">
              {home.approach.title}
            </h2>
            <span className="page-eyebrow" style={{ margin: 0 }}>
              18 Features Architecture
            </span>
          </div>

          <p className="page-subtitle">
            {home.approach.content}
          </p>

          <div className="pillars-grid">
            {home.approach.pillars.map((pillar, i) => (
              <div key={i} className="pillar-editorial-card">
                <span className="pillar-index">Pillar 0{i + 1}</span>
                <h3 className="pillar-title">{pillar.title}</h3>
                <p className="pillar-desc">{pillar.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* 5. MODEL OVERVIEW */}
        <section className="model-overview-plate">
          <div className="model-header-row">
            <div className="model-header-title-group">
              <Cpu size={16} className="text-water" />
              <h2 className="section-title" style={{ fontSize: '1.25rem', margin: 0 }}>
                {home.modelOverview.title}
              </h2>
            </div>
            <span className="badge badge-water">
              {home.modelOverview.architecture}
            </span>
          </div>

          <p className="article-body-p">
            {home.modelOverview.summary}
          </p>

          <p className="article-pullquote" style={{ fontStyle: 'italic', borderLeftColor: 'var(--tier-high)' }}>
            {home.modelOverview.trainingEventContext}
          </p>
        </section>

        {/* 6. METHODOLOGICAL LIMITATIONS */}
        <section className="limitations-box">
          <div className="limitations-header">
            <AlertTriangle size={18} />
            <h2 className="limitations-title">{home.limitations.title}</h2>
          </div>

          <p className="limitations-summary">
            {home.limitations.summary}
          </p>

          <div className="limitations-grid">
            {home.limitations.items.map((item, idx) => (
              <div key={idx} className="limitation-item">
                <span className="limitation-num">Constraint 0{idx + 1}</span>
                <p className="limitation-text">{item}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
