import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle2, Layers, Award, TrendingUp } from 'lucide-react';

export default function StatsOverview({ summary, selectedDate }) {
  if (!summary) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-3 animate-pulse">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="card-base p-3 h-20 bg-slate-900/60 border-white/5"></div>
        ))}
      </div>
    );
  }

  const total = summary.total_cells_scored || 3026;
  const high = summary.high_count || 0;
  const moderate = summary.moderate_count || 0;
  const none = summary.none_count || 0;

  const highPct = ((high / total) * 100).toFixed(1);
  const modPct = ((moderate / total) * 100).toFixed(1);
  const nonePct = ((none / total) * 100).toFixed(1);

  const topCell = summary.top_ranked_cell;

  return (
    <div className="space-y-2.5 mb-3">
      {/* 6 Grid Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5">
        {/* Total Cells */}
        <div className="card-base p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Grid Cells</span>
            <Layers size={14} className="text-slate-500" />
          </div>
          <div className="mt-1">
            <span className="text-xl font-bold font-mono text-white tracking-tight">
              {total.toLocaleString()}
            </span>
            <span className="text-[11px] text-slate-400 ml-1.5">100% coverage</span>
          </div>
        </div>

        {/* High Tier */}
        <div className="card-base p-3 flex flex-col justify-between border-rose-500/20 bg-rose-950/10">
          <div className="flex items-center justify-between text-rose-300 text-xs font-medium">
            <span>High Priority</span>
            <AlertTriangle size={14} className="text-rose-400" />
          </div>
          <div className="mt-1">
            <span className="text-xl font-bold font-mono text-rose-400 tracking-tight">
              {high}
            </span>
            <span className="text-[11px] text-rose-400/80 ml-1.5 font-mono">
              Top {highPct}% (Rank 1–150)
            </span>
          </div>
        </div>

        {/* Moderate Tier */}
        <div className="card-base p-3 flex flex-col justify-between border-amber-500/20 bg-amber-950/10">
          <div className="flex items-center justify-between text-amber-300 text-xs font-medium">
            <span>Moderate Priority</span>
            <AlertCircle size={14} className="text-amber-400" />
          </div>
          <div className="mt-1">
            <span className="text-xl font-bold font-mono text-amber-400 tracking-tight">
              {moderate}
            </span>
            <span className="text-[11px] text-amber-400/80 ml-1.5 font-mono">
              Next {modPct}% (151–300)
            </span>
          </div>
        </div>

        {/* Baseline / None Tier */}
        <div className="card-base p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Remaining Cells</span>
            <CheckCircle2 size={14} className="text-slate-500" />
          </div>
          <div className="mt-1">
            <span className="text-xl font-bold font-mono text-slate-300 tracking-tight">
              {none.toLocaleString()}
            </span>
            <span className="text-[11px] text-slate-500 ml-1.5 font-mono">
              {nonePct}% (Ranks 301+)
            </span>
          </div>
        </div>

        {/* Highest Susceptibility Cell */}
        <div className="card-base p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Top-Ranked Cell</span>
            <Award size={14} className="text-sky-400" />
          </div>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-bold font-mono text-sky-400">
              #{topCell?.cell_id ?? 'N/A'}
            </span>
            <span className="text-[11px] text-slate-400">
              Ward {topCell?.ward ?? '—'}
            </span>
          </div>
        </div>

        {/* Day Score Averages */}
        <div className="card-base p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Mean Model Score</span>
            <TrendingUp size={14} className="text-emerald-400" />
          </div>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-bold font-mono text-emerald-400">
              {summary.average_score != null ? summary.average_score.toFixed(4) : '—'}
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              Max: {summary.max_score != null ? summary.max_score.toFixed(3) : '—'}
            </span>
          </div>
        </div>
      </div>

      {/* Relative Tier Distribution Bar */}
      <div className="card-base px-3 py-2 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 font-medium">Daily Citywide Partition:</span>
          <div className="w-48 sm:w-64 h-2 bg-slate-800 rounded-full overflow-hidden flex">
            <div style={{ width: `${highPct}%` }} className="bg-rose-500" title={`High: ${high}`}></div>
            <div style={{ width: `${modPct}%` }} className="bg-amber-500" title={`Moderate: ${moderate}`}></div>
            <div style={{ width: `${nonePct}%` }} className="bg-slate-700" title={`None: ${none}`}></div>
          </div>
        </div>
        <div className="flex items-center gap-4 text-[11px] text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
            High (150 cells)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-500"></span>
            Moderate (150 cells)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-slate-600"></span>
            None (2,726 cells)
          </span>
        </div>
      </div>
    </div>
  );
}
