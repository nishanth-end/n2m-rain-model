import React, { useState } from 'react';
import { Search, MapPin, AlertTriangle, Info, Compass, Hash } from 'lucide-react';

export default function CellDetailPanel({
  selectedCell,
  onSearchCellId,
  onClearSelection
}) {
  const [searchInput, setSearchInput] = useState('');
  const [searchError, setSearchError] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchError('');
    const id = parseInt(searchInput.trim(), 10);
    if (isNaN(id) || id < 0 || id > 3025) {
      setSearchError('Enter a valid Cell ID (0 to 3025).');
      return;
    }
    const found = onSearchCellId(id);
    if (!found) {
      setSearchError(`Cell #${id} not found in current date.`);
    }
  };

  return (
    <div className="card-base p-3.5 space-y-3.5 bg-[#111827]">
      {/* Search Bar */}
      <div>
        <div className="flex items-center justify-between text-xs text-slate-300 font-semibold mb-1.5">
          <span className="flex items-center gap-1.5">
            <Search size={13} className="text-sky-400" />
            Lookup Grid Cell
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Range: 0–3025</span>
        </div>
        <form onSubmit={handleSearch} className="flex gap-1.5">
          <div className="relative flex-1">
            <Hash size={13} className="absolute left-2.5 top-2.5 text-slate-500" />
            <input
              type="number"
              min="0"
              max="3025"
              placeholder="e.g. 722"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full bg-[#1e293b] text-slate-100 pl-7 pr-2.5 py-1.5 rounded-md text-xs font-mono border border-white/10 focus:outline-none focus:border-sky-500 placeholder:text-slate-500"
            />
          </div>
          <button type="submit" className="btn-secondary text-xs px-3">
            Find
          </button>
        </form>
        {searchError && (
          <p className="text-rose-400 text-[11px] mt-1">{searchError}</p>
        )}
      </div>

      {/* Selected Cell Content */}
      <div className="border-t border-white/10 pt-3">
        {selectedCell ? (
          <div className="space-y-3">
            {/* Header: Cell ID + Level Badge */}
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
                  Selected Target
                </span>
                <h4 className="text-lg font-bold text-white font-mono flex items-center gap-1.5">
                  Cell #{selectedCell.cell_id}
                </h4>
              </div>
              <span
                className={
                  selectedCell.level === 'High'
                    ? 'badge-high'
                    : selectedCell.level === 'Moderate'
                    ? 'badge-mod'
                    : 'badge-none'
                }
              >
                {selectedCell.level}
              </span>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded bg-[#162032] border border-white/5">
                <span className="text-[11px] text-slate-400 block">Relative Rank</span>
                <span className="text-sm font-bold font-mono text-sky-400">
                  #{selectedCell.rank}{' '}
                  <span className="text-[10px] text-slate-500 font-normal">/ 3,026</span>
                </span>
              </div>

              <div className="p-2 rounded bg-[#162032] border border-white/5">
                <span className="text-[11px] text-slate-400 block">Model Score</span>
                <span className="text-sm font-bold font-mono text-white">
                  {selectedCell.score.toFixed(4)}
                </span>
              </div>

              <div className="p-2 rounded bg-[#162032] border border-white/5">
                <span className="text-[11px] text-slate-400 block">Administrative Ward</span>
                <span className="text-xs font-semibold text-slate-200">
                  Ward #{selectedCell.ward}
                </span>
              </div>

              <div className="p-2 rounded bg-[#162032] border border-white/5">
                <span className="text-[11px] text-slate-400 block">Replay Date</span>
                <span className="text-xs font-mono text-slate-200">
                  {selectedCell.date}
                </span>
              </div>
            </div>

            {/* Coordinates */}
            <div className="p-2 rounded bg-[#162032] border border-white/5 flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-1.5 text-slate-400">
                <Compass size={13} className="text-sky-400" />
                <span>Coordinates:</span>
              </div>
              <span className="text-slate-200">
                {selectedCell.lat.toFixed(5)}° N, {selectedCell.lon.toFixed(5)}° E
              </span>
            </div>

            {/* Scientific Notice */}
            <div className="p-2.5 rounded bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300/90 leading-relaxed flex items-start gap-2">
              <Info size={14} className="text-amber-400 shrink-0 mt-0.5" />
              <span>
                <strong>Interpretation Guardrail:</strong> This score represents an empirical spatial susceptibility rank
                relative to other cells on {selectedCell.date}. It does <em>not</em> represent a calibrated flood probability or early warning.
              </span>
            </div>

            <button
              onClick={onClearSelection}
              className="btn-ghost text-xs w-full justify-center text-slate-400"
            >
              Clear Selection
            </button>
          </div>
        ) : (
          <div className="text-center py-6 text-slate-500 space-y-1.5">
            <MapPin size={24} className="mx-auto text-slate-600 mb-1" />
            <p className="text-xs text-slate-300 font-medium">No Cell Selected</p>
            <p className="text-[11px] text-slate-500 max-w-[200px] mx-auto leading-relaxed">
              Click any point on the map, choose from the Top 15 list, or search by Cell ID above.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
