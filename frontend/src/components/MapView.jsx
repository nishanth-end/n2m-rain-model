import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Layers, Eye, Crosshair } from 'lucide-react';

// Tile layer config
const TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const TILE_ATTR =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';

export default function MapView({
  cells = [],
  selectedCell,
  onSelectCell,
  isLoading
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);
  const highlightLayerRef = useRef(null);
  const canvasRendererRef = useRef(null);

  const [filterLevel, setFilterLevel] = useState('ALL'); // ALL, HIGH_ONLY, HIGH_MOD

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [12.9716, 77.5946],
        zoom: 11,
        minZoom: 10,
        maxZoom: 16,
        zoomControl: true,
      });

      L.tileLayer(TILE_URL, {
        attribution: TILE_ATTR,
        subdomains: 'abcd',
        maxZoom: 19,
      }).addTo(map);

      // Dedicated Canvas Renderer for high performance with 3000+ points
      const canvasRenderer = L.canvas({ padding: 0.5 });
      canvasRendererRef.current = canvasRenderer;

      const layerGroup = L.layerGroup().addTo(map);
      layerGroupRef.current = layerGroup;

      const highlightLayer = L.layerGroup().addTo(map);
      highlightLayerRef.current = highlightLayer;

      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Render / Update Points whenever cells or filterLevel changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    const canvasRenderer = canvasRendererRef.current;

    if (!map || !layerGroup || !canvasRenderer) return;

    layerGroup.clearLayers();

    // Filter points based on user toggle
    let visibleCells = cells;
    if (filterLevel === 'HIGH_ONLY') {
      visibleCells = cells.filter((c) => c.level === 'High');
    } else if (filterLevel === 'HIGH_MOD') {
      visibleCells = cells.filter((c) => c.level === 'High' || c.level === 'Moderate');
    }

    visibleCells.forEach((c) => {
      let radius = 3.5;
      let fillColor = '#64748b';
      let strokeColor = '#475569';
      let fillOpacity = 0.45;
      let weight = 0.6;

      if (c.level === 'High') {
        radius = 5.5;
        fillColor = '#ef4444';
        strokeColor = '#fca5a5';
        fillOpacity = 0.9;
        weight = 1.2;
      } else if (c.level === 'Moderate') {
        radius = 4.5;
        fillColor = '#f59e0b';
        strokeColor = '#fcd34d';
        fillOpacity = 0.8;
        weight = 1.0;
      }

      const marker = L.circleMarker([c.lat, c.lon], {
        renderer: canvasRenderer,
        radius,
        fillColor,
        color: strokeColor,
        weight,
        fillOpacity,
      });

      // Simple tooltip on hover
      marker.bindTooltip(
        `<div style="font-family: inherit; font-size: 11px;">
          <strong style="color: #38bdf8;">Cell #${c.cell_id}</strong> (Ward ${c.ward})<br/>
          Rank: <strong>#${c.rank}</strong> • Level: <strong>${c.level}</strong><br/>
          Score: <strong>${c.score.toFixed(4)}</strong>
        </div>`,
        { direction: 'top', offset: [0, -4], opacity: 0.95 }
      );

      marker.on('click', () => {
        onSelectCell(c);
      });

      marker.addTo(layerGroup);
    });
  }, [cells, filterLevel, onSelectCell]);

  // Update Highlight Layer when selectedCell changes
  useEffect(() => {
    const highlightLayer = highlightLayerRef.current;
    const map = mapInstanceRef.current;
    if (!highlightLayer || !map) return;

    highlightLayer.clearLayers();

    if (selectedCell) {
      const { lat, lon, cell_id, ward, rank, score, level } = selectedCell;

      // Outer glowing ring
      const ring = L.circleMarker([lat, lon], {
        radius: 12,
        fillColor: 'transparent',
        color: '#38bdf8',
        weight: 2.5,
        opacity: 0.9,
      }).addTo(highlightLayer);

      // Inner solid target
      const target = L.circleMarker([lat, lon], {
        radius: 6,
        fillColor: '#38bdf8',
        color: '#ffffff',
        weight: 1.5,
        fillOpacity: 0.9,
      }).addTo(highlightLayer);

      // Open a nice popup
      const popupContent = `
        <div style="font-size: 12px; line-height: 1.4; padding: 2px;">
          <div style="font-weight: 700; color: #38bdf8; font-size: 13px; margin-bottom: 2px;">
            Target Grid Cell #${cell_id}
          </div>
          <div style="color: #cbd5e1; font-size: 11px; margin-bottom: 4px;">
            Ward ${ward} • Coordinates: ${lat.toFixed(4)}, ${lon.toFixed(4)}
          </div>
          <div style="display: flex; gap: 6px; margin-bottom: 6px;">
            <span style="background: ${level === 'High' ? '#7f1d1d' : level === 'Moderate' ? '#78350f' : '#334155'}; color: #fff; padding: 1px 6px; border-radius: 3px; font-weight: 600; font-size: 10px;">
              ${level.toUpperCase()}
            </span>
            <span style="background: #1e293b; color: #94a3b8; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-family: monospace;">
              Rank #${rank} / 3026
            </span>
          </div>
          <div style="font-size: 11px; color: #94a3b8;">
            Model Score: <strong style="color: #f8fafc; font-family: monospace;">${score.toFixed(4)}</strong>
          </div>
          <div style="margin-top: 4px; font-size: 9px; color: #64748b; font-style: italic;">
            Relative priority rank. Not a flood probability.
          </div>
        </div>
      `;

      target.bindPopup(popupContent, { offset: [0, -6] }).openPopup();
    }
  }, [selectedCell]);

  // Recenter map on Bengaluru
  const handleRecenter = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([12.9716, 77.5946], 11, { animate: true });
    }
  };

  return (
    <div className="relative w-full h-[620px] rounded-lg overflow-hidden border border-white/10 bg-[#080b11]">
      {/* Map Container */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Top Left: Filter Overlays */}
      <div className="absolute top-3 left-12 z-[1000] flex items-center gap-1.5 bg-[#111827]/90 backdrop-blur-md p-1.5 rounded-md border border-white/10 shadow-lg text-xs">
        <span className="text-slate-400 font-medium px-1.5 flex items-center gap-1">
          <Eye size={12} /> Filter:
        </span>
        <button
          onClick={() => setFilterLevel('ALL')}
          className={`px-2 py-1 rounded font-mono text-[11px] transition-colors ${
            filterLevel === 'ALL'
              ? 'bg-sky-600 text-white font-bold'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          All (3,026)
        </button>
        <button
          onClick={() => setFilterLevel('HIGH_MOD')}
          className={`px-2 py-1 rounded font-mono text-[11px] transition-colors ${
            filterLevel === 'HIGH_MOD'
              ? 'bg-amber-600 text-white font-bold'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          High + Mod (300)
        </button>
        <button
          onClick={() => setFilterLevel('HIGH_ONLY')}
          className={`px-2 py-1 rounded font-mono text-[11px] transition-colors ${
            filterLevel === 'HIGH_ONLY'
              ? 'bg-rose-600 text-white font-bold'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          High Only (150)
        </button>

        <button
          onClick={handleRecenter}
          className="ml-1 p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800"
          title="Recenter Map on Bengaluru"
        >
          <Crosshair size={14} />
        </button>
      </div>

      {/* Bottom Right: Compact GIS Legend */}
      <div className="absolute bottom-6 right-3 z-[1000] bg-[#111827]/95 backdrop-blur-md p-3 rounded-lg border border-white/15 shadow-2xl max-w-xs text-xs space-y-2 pointer-events-auto">
        <div className="flex items-center justify-between border-b border-white/10 pb-1.5 font-semibold text-white">
          <span className="flex items-center gap-1.5 text-xs">
            <Layers size={13} className="text-sky-400" />
            Ranked Alert Tiers
          </span>
          <span className="text-[10px] text-slate-400 font-mono">Daily Partition</span>
        </div>

        <div className="space-y-1.5 text-[11px]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-rose-500 border border-rose-300"></span>
              <span className="text-slate-200 font-medium">High</span>
            </div>
            <span className="text-slate-400 font-mono">Top 150 (Ranks 1–150)</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500 border border-amber-300"></span>
              <span className="text-slate-200 font-medium">Moderate</span>
            </div>
            <span className="text-slate-400 font-mono">Next 150 (Ranks 151–300)</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-slate-500 border border-slate-400"></span>
              <span className="text-slate-400">None / Baseline</span>
            </div>
            <span className="text-slate-400 font-mono">Remaining (Ranks 301–3026)</span>
          </div>
        </div>

        <div className="border-t border-white/10 pt-1.5 text-[9.5px] text-slate-400 leading-tight">
          Relative daily prioritization. Scores do not represent flood probabilities.
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 z-[1001] bg-[#0b0f17]/60 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-[#111827] border border-white/10 px-4 py-2.5 rounded-lg shadow-xl flex items-center gap-2.5 text-xs text-sky-400">
            <div className="w-4 h-4 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></div>
            <span>Evaluating cell rankings for selected date...</span>
          </div>
        </div>
      )}
    </div>
  );
}
