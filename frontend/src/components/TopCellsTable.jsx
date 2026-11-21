import React from 'react';
import { Award, ArrowUpRight } from 'lucide-react';

export default function TopCellsTable({
  cells = [],
  selectedCell,
  onSelectCell
}) {
  const top15 = cells.slice(0, 15);

  return (
    <div className="card-base p-3 space-y-2 bg-[#111827]">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <span className="text-xs font-semibold text-white flex items-center gap-1.5">
          <Award size={13} className="text-rose-400" />
          Highest Susceptibility Priority (Top 15)
        </span>
        <span className="text-[10px] text-slate-400 font-mono">Rank 1–15</span>
      </div>

      <div className="overflow-x-auto max-h-[280px] overflow-y-auto pr-1">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-[10px] text-slate-500 uppercase tracking-wider border-b border-white/5 font-mono">
              <th className="py-1.5 px-2">Rank</th>
              <th className="py-1.5 px-2">Cell ID</th>
              <th className="py-1.5 px-2">Ward</th>
              <th className="py-1.5 px-2 text-right">Score</th>
              <th className="py-1.5 px-2 text-center">Tier</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-mono">
            {top15.map((c) => {
              const isSelected = selectedCell?.cell_id === c.cell_id;
              return (
                <tr
                  key={c.cell_id}
                  onClick={() => onSelectCell(c)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-sky-950/60 text-sky-200 border-l-2 border-sky-400'
                      : 'hover:bg-slate-800/60 text-slate-300'
                  }`}
                >
                  <td className="py-1.5 px-2 font-bold text-sky-400">#{c.rank}</td>
                  <td className="py-1.5 px-2 text-white font-semibold">Cell {c.cell_id}</td>
                  <td className="py-1.5 px-2 text-slate-400">W-{c.ward}</td>
                  <td className="py-1.5 px-2 text-right font-medium text-slate-200">
                    {c.score.toFixed(4)}
                  </td>
                  <td className="py-1.5 px-2 text-center">
                    <span className="badge-high text-[10px] px-1.5 py-0.5">High</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="text-[10px] text-slate-500 pt-1 text-center italic">
        Click any row to pinpoint and inspect target on the map.
      </div>
    </div>
  );
}
