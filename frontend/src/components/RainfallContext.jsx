import React from 'react';
import { CloudRain, Info, ShieldCheck, Database } from 'lucide-react';

export default function RainfallContext({ selectedDate }) {
  const rainfallFeatures = [
    { name: 'rain_1d_mm', label: '1-Day Rainfall', desc: 'Rainfall accumulated on the evaluated date' },
    { name: 'rain_3d_mm', label: '3-Day Rolling Sum', desc: 'Sum of evaluated date plus 2 preceding days' },
    { name: 'rain_7d_mm', label: '7-Day Rolling Sum', desc: 'Sum of evaluated date plus 6 preceding days' },
    { name: 'rain_14d_mm', label: '14-Day Rolling Sum', desc: 'Antecedent soil saturation window (14 days)' },
    { name: 'rain_30d_mm', label: '30-Day Rolling Sum', desc: 'Extended monsoon moisture index (30 days)' },
    { name: 'rain_lag1_mm', label: 'Lag 1 (Yesterday)', desc: 'Rainfall recorded 1 day prior' },
    { name: 'rain_lag2_mm', label: 'Lag 2 (2 Days Prior)', desc: 'Rainfall recorded 2 days prior' },
    { name: 'rain_lag3_mm', label: 'Lag 3 (3 Days Prior)', desc: 'Rainfall recorded 3 days prior' },
  ];

  return (
    <div className="card-base p-3.5 space-y-3 bg-[#111827]">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <span className="text-xs font-semibold text-white flex items-center gap-1.5">
          <CloudRain size={14} className="text-sky-400" />
          Rainfall Feature Pipeline & Data Grounding
        </span>
        <span className="text-[10px] text-slate-400 font-mono">CHIRPS 5km Gridded</span>
      </div>

      {/* Transparent API Exposure Notice */}
      <div className="p-2.5 rounded bg-sky-950/40 border border-sky-500/20 text-[11px] text-sky-200/90 leading-relaxed space-y-1">
        <div className="flex items-center gap-1.5 font-semibold text-sky-300">
          <Info size={13} className="text-sky-400" />
          API Data Grounding & Transparency Disclosure
        </div>
        <p>
          The XGBoost susceptibility engine consumes 8 antecedent rainfall features per grid cell derived
          from <strong>CHIRPS daily rainfall (~5 km gridded product)</strong>.
        </p>
        <p className="text-slate-300">
          <strong>Note:</strong> The compact replay API (<code className="text-sky-300">/api/risk</code>) optimizes spatial payload performance by transmitting cell rank, score, and tier. Raw millimeter values are encapsulated inside the internal model feature matrix and are not individually serialized on the public risk route.
        </p>
      </div>

      {/* Feature Breakdown */}
      <div className="space-y-1.5">
        <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block">
          Model Dynamic Precipitation Inputs (18 Features Total)
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs">
          {rainfallFeatures.map((f) => (
            <div key={f.name} className="p-1.5 rounded bg-[#162032] border border-white/5 flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="font-mono text-sky-400 font-semibold text-[11px]">{f.name}</span>
                <span className="text-[9.5px] text-slate-400">{f.label}</span>
              </div>
              <span className="text-[10px] text-slate-400 leading-tight mt-0.5">{f.desc}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Source Characteristics & Spatial Mapping */}
      <div className="border-t border-white/10 pt-2 grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-400">
        <div className="flex items-start gap-1.5">
          <Database size={13} className="text-slate-500 shrink-0 mt-0.5" />
          <span>
            <strong>Spatial Linkage:</strong> 3,026 cells are mapped to rainfall pixel centers via <code className="text-slate-300">cell_pixel_map.csv</code>.
          </span>
        </div>
        <div className="flex items-start gap-1.5">
          <ShieldCheck size={13} className="text-slate-500 shrink-0 mt-0.5" />
          <span>
            <strong>Integrity Guardrail:</strong> Alternative live weather sources (e.g. Open-Meteo, IMD) cannot be silently substituted without complete distributional recalibration.
          </span>
        </div>
      </div>
    </div>
  );
}
