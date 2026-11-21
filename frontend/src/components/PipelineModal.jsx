import React, { useState, useEffect } from 'react';
import { X, Cpu, ShieldAlert, AlertTriangle, Layers, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';

export default function PipelineModal({ isOpen, onClose }) {
  const [pipelineData, setPipelineData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setIsLoading(true);
    api
      .getPipelineStatus()
      .then((data) => setPipelineData(data))
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-dialog max-w-lg text-slate-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b border-white/10 flex items-center justify-between bg-[#162032]">
          <div className="flex items-center gap-2">
            <Cpu size={18} className="text-slate-400" />
            <div>
              <h3 className="text-base font-bold text-white">
                Live Rainfall Ingestion Architecture
              </h3>
              <p className="text-xs text-slate-400">
                Isolated research prototype status & compatibility boundaries
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-white/10"
          >
            <X size={18} />
          </button>
        </div>

        <div className="p-4 overflow-y-auto space-y-3.5 text-xs">
          {/* Status Badge Card */}
          <div className="p-3 rounded-lg bg-[#162032] border border-white/5 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-400 block uppercase font-mono">
                Pipeline Operational State
              </span>
              <span className="text-sm font-bold text-slate-300 font-mono flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-slate-500"></span>
                {pipelineData?.status?.toUpperCase() || 'DISABLED BY DEFAULT'}
              </span>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 block uppercase font-mono">
                Alert Connectivity
              </span>
              <span className="text-xs font-semibold text-emerald-400 font-mono">
                DISCONNECTED (SAFE)
              </span>
            </div>
          </div>

          {/* Compatibility Warning */}
          <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-200 space-y-1.5 leading-relaxed">
            <div className="flex items-center gap-1.5 font-bold text-amber-300">
              <AlertTriangle size={15} />
              Distributional Recalibration Rule
            </div>
            <p>
              The XGBoost model is trained strictly on <strong>CHIRPS ~5 km gridded daily rainfall</strong>.
              Point-source meteorological APIs (such as Open-Meteo, IMD ground stations, or AccuWeather) exhibit systematic spatial resolution shifts and temporal mismatches.
            </p>
            <p className="text-[11px] text-amber-300/80">
              Silently streaming uncalibrated real-time data into this model without full re-training will distort cell rankings.
            </p>
          </div>

          {/* Required Features */}
          <div className="space-y-1.5">
            <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block">
              Required Dynamic Preprocessing Aggregates (8 Columns)
            </span>
            <div className="flex flex-wrap gap-1.5 font-mono text-[11px]">
              {(pipelineData?.required_features || [
                'rain_1d_mm', 'rain_3d_mm', 'rain_7d_mm', 'rain_14d_mm',
                'rain_30d_mm', 'rain_lag1_mm', 'rain_lag2_mm', 'rain_lag3_mm'
              ]).map((feat) => (
                <span
                  key={feat}
                  className="px-2 py-0.5 rounded bg-[#1e293b] border border-white/10 text-sky-300"
                >
                  {feat}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="p-3 border-t border-white/10 bg-[#0e1422] flex justify-end">
          <button onClick={onClose} className="btn-secondary text-xs px-4">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
