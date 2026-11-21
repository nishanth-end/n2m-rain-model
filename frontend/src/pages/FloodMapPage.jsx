import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  Play,
  Pause,
  ChevronLeft,
  ChevronRight,
  Hash,
  Compass,
  Layers,
  Crosshair,
  Filter,
  Calendar,
  ChevronDown,
  ChevronUp,
  RefreshCw
} from 'lucide-react';

// Standard OpenStreetMap tiles — zero API key requirement, fully accessible
const TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
const TILE_ATTR =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

export default function FloodMapPage({
  dates = [],
  selectedDate,
  onSelectDate,
  cells = [],
  summary,
  selectedCell,
  onSelectCell,
  isLoading
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);
  const highlightLayerRef = useRef(null);

  const [mapReady, setMapReady] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [filterTier, setFilterTier] = useState('ALL'); // ALL, HIGH_ONLY, HIGH_MOD
  const [searchInput, setSearchInput] = useState('');
  const [searchError, setSearchError] = useState('');
  const [infoPanelOpen, setInfoPanelOpen] = useState(true);

  const timerRef = useRef(null);
  const currentIndex = dates.indexOf(selectedDate);
  const totalDates = dates.length;

  // Initialize Map with preferCanvas: true for reliable 3,026-point rendering
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Reset leaflet internal id if container was previously mounted
    if (mapContainerRef.current._leaflet_id && !mapInstanceRef.current) {
      mapContainerRef.current._leaflet_id = null;
    }

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [12.9716, 77.5946],
        zoom: 11,
        minZoom: 10,
        maxZoom: 18,
        zoomControl: true,
        preferCanvas: true, // Native Leaflet canvas management across all vectors
      });

      L.tileLayer(TILE_URL, {
        attribution: TILE_ATTR,
        subdomains: ['a', 'b', 'c'],
        maxZoom: 19,
      }).addTo(map);

      const layerGroup = L.layerGroup().addTo(map);
      layerGroupRef.current = layerGroup;

      const highlightLayer = L.layerGroup().addTo(map);
      highlightLayerRef.current = highlightLayer;

      mapInstanceRef.current = map;
      setMapReady(true);

      // Force size recalculation to ensure tiles and canvas match container
      setTimeout(() => {
        if (map) {
          map.invalidateSize();
        }
      }, 100);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
        setMapReady(false);
      }
      if (mapContainerRef.current) {
        mapContainerRef.current._leaflet_id = null;
      }
    };
  }, []);

  // Render / Update Points whenever cells, filterTier, or mapReady updates
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup || !mapReady) return;

    layerGroup.clearLayers();

    let visibleCells = cells;
    if (filterTier === 'HIGH_ONLY') {
      visibleCells = cells.filter((c) => c.level === 'High');
    } else if (filterTier === 'HIGH_MOD') {
      visibleCells = cells.filter((c) => c.level === 'High' || c.level === 'Moderate');
    }

    visibleCells.forEach((c) => {
      let radius = 3.5;
      let fillColor = '#64748b'; // Baseline risk
      let strokeColor = '#334155';
      let fillOpacity = 0.65;
      let weight = 0.8;

      if (c.level === 'High') {
        radius = 6.0;
        fillColor = '#dc2626'; // Terracotta Red
        strokeColor = '#7f1d1d';
        fillOpacity = 0.95;
        weight = 1.5;
      } else if (c.level === 'Moderate') {
        radius = 4.8;
        fillColor = '#f59e0b'; // Warm Amber
        strokeColor = '#78350f';
        fillOpacity = 0.9;
        weight = 1.2;
      }

      const marker = L.circleMarker([c.lat, c.lon], {
        radius,
        fillColor,
        color: strokeColor,
        weight,
        fillOpacity,
      });

      marker.bindTooltip(
        `<div style="font-family: inherit; font-size: 11px; color: #151d1b;">
          <strong>Spatial Cell #${c.cell_id}</strong> (Ward ${c.ward})<br/>
          Priority Rank: <strong>#${c.rank}</strong> • Tier: <strong>${c.level}</strong><br/>
          Susceptibility Score: <strong>${typeof c.score === 'number' ? c.score.toFixed(4) : c.score}</strong>
        </div>`,
        { direction: 'top', offset: [0, -4], opacity: 0.95 }
      );

      marker.on('click', () => {
        onSelectCell(c);
        setInfoPanelOpen(true);
      });

      marker.addTo(layerGroup);
    });
  }, [cells, filterTier, mapReady, onSelectCell]);

  // Selected Target Highlight Ring & Target Pin
  useEffect(() => {
    const highlightLayer = highlightLayerRef.current;
    const map = mapInstanceRef.current;
    if (!highlightLayer || !map || !mapReady) return;

    highlightLayer.clearLayers();

    if (selectedCell) {
      const { lat, lon, cell_id, ward, rank, score, level } = selectedCell;

      // Outer focus ring
      L.circleMarker([lat, lon], {
        radius: 14,
        fillColor: 'transparent',
        color: '#1b4965',
        weight: 2.5,
        opacity: 0.9,
      }).addTo(highlightLayer);

      // Inner target pip
      const target = L.circleMarker([lat, lon], {
        radius: 6,
        fillColor: '#1b4965',
        color: '#ffffff',
        weight: 1.5,
        fillOpacity: 0.95,
      }).addTo(highlightLayer);

      const popupContent = `
        <div style="font-size: 12px; line-height: 1.45; padding: 2px; font-family: inherit; color: #151d1b;">
          <div style="font-family: 'DM Serif Display', Georgia, serif; font-size: 14px; font-weight: bold; margin-bottom: 2px;">
            Spatial Cell #${cell_id}
          </div>
          <div style="font-size: 11px; color: #62726d; margin-bottom: 5px;">
            Ward ${ward} • ${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E
          </div>
          <div style="display: flex; gap: 5px; margin-bottom: 6px;">
            <span style="background: ${level === 'High' ? '#faecea' : level === 'Moderate' ? '#fdf4e7' : '#f0f2f1'}; color: ${level === 'High' ? '#af382b' : level === 'Moderate' ? '#b87314' : '#6d7d79'}; border: 1px solid ${level === 'High' ? '#e8b1a8' : level === 'Moderate' ? '#ebd1aa' : '#cad3d0'}; padding: 1px 6px; border-radius: 2px; font-weight: 600; font-size: 10px;">
              ${level.toUpperCase()}
            </span>
            <span style="background: #f3efe6; border: 1px solid #ded8cb; color: #3b4945; padding: 1px 6px; border-radius: 2px; font-size: 10px; font-family: monospace;">
              Rank #${rank} / 3026
            </span>
          </div>
          <div style="font-size: 11px; color: #3b4945;">
            Susceptibility Index: <strong style="font-family: monospace;">${typeof score === 'number' ? score.toFixed(4) : score}</strong>
          </div>
        </div>
      `;

      target.bindPopup(popupContent, { offset: [0, -6] }).openPopup();
    }
  }, [selectedCell, mapReady]);

  // Autoplay Replay Loop with Graceful End-of-Replay Handling
  useEffect(() => {
    if (isPlaying && totalDates > 0) {
      timerRef.current = setInterval(() => {
        const curIdx = dates.indexOf(selectedDate);
        if (curIdx >= 0 && curIdx < totalDates - 1) {
          onSelectDate(dates[curIdx + 1]);
        } else {
          // Reached final date of replay: stop playback gracefully
          setIsPlaying(false);
        }
      }, 1800);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, dates, selectedDate, onSelectDate, totalDates]);

  const handleTogglePlay = () => {
    if (!isPlaying) {
      // If at end of replay, restart from beginning
      if (currentIndex >= totalDates - 1) {
        onSelectDate(dates[0]);
      }
      setIsPlaying(true);
    } else {
      setIsPlaying(false);
    }
  };

  const handlePrev = () => {
    setIsPlaying(false);
    if (currentIndex > 0) {
      onSelectDate(dates[currentIndex - 1]);
    }
  };

  const handleNext = () => {
    setIsPlaying(false);
    if (currentIndex < totalDates - 1) {
      onSelectDate(dates[currentIndex + 1]);
    }
  };

  const handleSelectDateFromDropdown = (e) => {
    setIsPlaying(false);
    onSelectDate(e.target.value);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchError('');
    const id = parseInt(searchInput.trim(), 10);
    if (isNaN(id) || id < 0 || id > 3025) {
      setSearchError('Cell ID must be between 0 and 3025.');
      return;
    }
    const found = cells.find((c) => c.cell_id === id);
    if (found) {
      onSelectCell(found);
      setInfoPanelOpen(true);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.setView([found.lat, found.lon], 13, { animate: true });
      }
    } else {
      setSearchError(`Cell #${id} not present in active date.`);
    }
  };

  const handleRecenter = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([12.9716, 77.5946], 11, { animate: true });
    }
  };

  const highCount = summary?.high_count ?? 150;
  const modCount = summary?.moderate_count ?? 150;
  const noneCount = summary?.none_count ?? 2726;
  const totalCount = summary?.total_cells_scored ?? 3026;

  return (
    <div className="map-page-flow">
      {/* 1. TOP TOOLBAR: REPLAY CONTROLS & CITYWIDE METRICS */}
      <div className="map-toolbar">
        {/* Replay Stepper */}
        <div className="map-stepper-group">
          <button
            onClick={handleTogglePlay}
            className={isPlaying ? 'btn-secondary btn-sm' : 'btn-primary btn-sm'}
            title={isPlaying ? 'Pause replay' : 'Play historical sequence'}
          >
            {isPlaying ? <Pause size={13} /> : <Play size={13} />}
            <span>{isPlaying ? 'PAUSE' : 'REPLAY'}</span>
          </button>

          <button
            onClick={handlePrev}
            disabled={currentIndex <= 0}
            className="btn-secondary btn-sm"
            title="Previous Date"
          >
            <ChevronLeft size={14} />
          </button>

          <div className="map-date-display">
            <Calendar size={14} className="text-water" />
            <span className="map-active-date">{selectedDate || '—'}</span>
            <span className="map-date-counter">
              ({currentIndex >= 0 ? `${currentIndex + 1} / ${totalDates}` : '—'})
            </span>
            {isLoading && (
              <RefreshCw size={12} className="animate-spin text-water" title="Updating rankings..." />
            )}
          </div>

          <button
            onClick={handleNext}
            disabled={currentIndex >= totalDates - 1 || totalDates === 0}
            className="btn-secondary btn-sm"
            title="Next Date"
          >
            <ChevronRight size={14} />
          </button>

          <select
            value={selectedDate}
            onChange={handleSelectDateFromDropdown}
            disabled={totalDates === 0}
            className="map-date-select"
          >
            {dates.map((d, i) => (
              <option key={d} value={d}>
                Day {i + 1}: {d}
              </option>
            ))}
          </select>
        </div>

        {/* Citywide Susceptibility Summary Strip */}
        <div className="map-metrics-group">
          <div className="map-metric-item" title="Top 150 cells per day">
            <span className="metric-dot high"></span>
            <span className="metric-label">High:</span>
            <span className="metric-val text-high">{highCount}</span>
            <span className="metric-pct">(5%)</span>
          </div>

          <div className="map-metric-item" title="Ranks 151-300 per day">
            <span className="metric-dot mod"></span>
            <span className="metric-label">Moderate:</span>
            <span className="metric-val text-mod">{modCount}</span>
            <span className="metric-pct">(5%)</span>
          </div>

          <div className="map-metric-item" title="Ranks 301-3026 per day">
            <span className="metric-dot none"></span>
            <span className="metric-label">Baseline:</span>
            <span className="metric-val text-muted">{noneCount}</span>
          </div>

          <div className="map-metric-divider">
            Total: <strong>{totalCount}</strong> Cells
          </div>
        </div>
      </div>

      {/* 2. LEAFLET PRESENTATION STAGE */}
      <div className="map-stage-wrapper">
        {/* Real Mount Element with explicit 100% dimensions */}
        <div ref={mapContainerRef} className="leaflet-mount-container" />

        {/* Top Controls Overlay: Tier Filters + Recenter */}
        <div className="map-overlay-filters">
          <span className="page-eyebrow" style={{ fontSize: '10px', margin: 0, padding: '0 4px' }}>
            <Filter size={11} /> Filter:
          </span>
          <button
            onClick={() => setFilterTier('ALL')}
            className={`filter-btn ${filterTier === 'ALL' ? 'active-all' : ''}`}
          >
            All (3,026)
          </button>
          <button
            onClick={() => setFilterTier('HIGH_MOD')}
            className={`filter-btn ${filterTier === 'HIGH_MOD' ? 'active-mod' : ''}`}
          >
            High + Mod (300)
          </button>
          <button
            onClick={() => setFilterTier('HIGH_ONLY')}
            className={`filter-btn ${filterTier === 'HIGH_ONLY' ? 'active-high' : ''}`}
          >
            High Only (150)
          </button>
          <button
            onClick={handleRecenter}
            className="recenter-btn"
            title="Recenter Map View on Bengaluru"
          >
            <Crosshair size={13} />
          </button>
        </div>

        {/* Top Right: Target Pinpoint Search Bar */}
        <div className="map-overlay-search">
          <form onSubmit={handleSearch} className="search-form-row">
            <div className="search-input-wrapper">
              <Hash size={12} className="search-input-icon" />
              <input
                type="number"
                min="0"
                max="3025"
                placeholder="Find Cell ID (e.g. 722)"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="search-input-field"
              />
            </div>
            <button type="submit" className="btn-primary btn-sm">
              Find
            </button>
          </form>
          {searchError && (
            <p className="search-error-text">{searchError}</p>
          )}
        </div>

        {/* Collapsible Slide-over Information Drawer (Bottom Left) */}
        <div className="map-overlay-inspector">
          <div
            onClick={() => setInfoPanelOpen(!infoPanelOpen)}
            className="inspector-header-bar"
          >
            <div className="inspector-header-title">
              <Compass size={14} className="text-water" />
              <span>
                {selectedCell ? `Target Inspector — Cell #${selectedCell.cell_id}` : 'Cell Telemetry & Attributes'}
              </span>
            </div>
            <button className="btn-ghost" style={{ padding: 0 }}>
              {infoPanelOpen ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
            </button>
          </div>

          {infoPanelOpen && (
            <div className="inspector-content">
              {selectedCell ? (
                <>
                  <div className="inspector-top-row">
                    <div>
                      <span className="page-eyebrow" style={{ fontSize: '10px', margin: 0 }}>
                        Micro-Catchment
                      </span>
                      <div className="inspector-cell-title">
                        Cell #{selectedCell.cell_id}
                      </div>
                    </div>
                    <span
                      className={
                        selectedCell.level === 'High'
                          ? 'badge badge-high'
                          : selectedCell.level === 'Moderate'
                          ? 'badge badge-mod'
                          : 'badge badge-baseline'
                      }
                    >
                      {selectedCell.level}
                    </span>
                  </div>

                  <div className="inspector-grid">
                    <div className="inspector-grid-cell">
                      <span className="inspector-metric-label">Daily Relative Rank</span>
                      <strong className="text-water font-bold">#{selectedCell.rank}</strong> / 3,026
                    </div>

                    <div className="inspector-grid-cell">
                      <span className="inspector-metric-label">Model Score</span>
                      <strong>{typeof selectedCell.score === 'number' ? selectedCell.score.toFixed(4) : selectedCell.score}</strong>
                    </div>

                    <div className="inspector-grid-cell">
                      <span className="inspector-metric-label">Civic Ward</span>
                      <span>Ward #{selectedCell.ward}</span>
                    </div>

                    <div className="inspector-grid-cell">
                      <span className="inspector-metric-label">Evaluated Date</span>
                      <span>{selectedCell.date}</span>
                    </div>
                  </div>

                  <div className="inspector-coords-row">
                    <span>Coordinates:</span>
                    <span>
                      {selectedCell.lat.toFixed(4)}° N, {selectedCell.lon.toFixed(4)}° E
                    </span>
                  </div>

                  <div className="inspector-guardrail">
                    <strong>Guardrail:</strong> Score represents relative daily vulnerability across Bengaluru, not a physical flood probability.
                  </div>
                </>
              ) : (
                <div style={{ textAlign: 'center', padding: '1rem 0.5rem', color: 'var(--ink-muted)' }}>
                  <p style={{ fontWeight: 600, color: 'var(--ink-primary)', marginBottom: '4px' }}>
                    No Cell Currently Selected
                  </p>
                  <p style={{ fontSize: '11px', color: 'var(--ink-muted)', lineHeight: 1.4 }}>
                    Click any circle on the map or input a Cell ID in the search box above to inspect its spatial score.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Bottom Right: Cartographic Legend */}
        <div className="map-overlay-legend">
          <div className="legend-header">
            <Layers size={13} className="text-water" />
            <span>Susceptibility Ranking Legend</span>
          </div>

          <div className="legend-rows">
            <div className="legend-row">
              <div className="legend-item-group">
                <span className="metric-dot high"></span>
                <span style={{ fontWeight: 600, color: 'var(--ink-primary)' }}>High Priority</span>
              </div>
              <span className="text-dim">Top 150 Cells (Rank 1–150)</span>
            </div>

            <div className="legend-row">
              <div className="legend-item-group">
                <span className="metric-dot mod"></span>
                <span style={{ fontWeight: 600, color: 'var(--ink-primary)' }}>Moderate Priority</span>
              </div>
              <span className="text-dim">Next 150 Cells (151–300)</span>
            </div>

            <div className="legend-row">
              <div className="legend-item-group">
                <span className="metric-dot none"></span>
                <span style={{ color: 'var(--ink-secondary)' }}>Baseline Risk</span>
              </div>
              <span className="text-dim">Remaining 2,726 Cells</span>
            </div>
          </div>

          <div className="legend-subtext">
            Classifications are relative daily rankings, not certified inundation boundaries.
          </div>
        </div>
      </div>
    </div>
  );
}
