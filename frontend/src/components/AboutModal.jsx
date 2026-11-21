import React from 'react';
import { X, AlertTriangle, CheckCircle, ShieldAlert, FileText, Database } from 'lucide-react';

export default function AboutModal({ isOpen, onClose, aboutData }) {
  if (!isOpen) return null;

  const stats = aboutData?.validation_limitations || {
    labelled_places_count: 10,
    historical_events_count: 6,
    spatial_resolution_km: 5.0,
    holdout_event: 'September 2022 (E2022_09)',
    pr_auc: 0.0026,
    random_chance_auc: 0.0013,
    high_hit_rate_pct: 8.3,
    high_random_baseline_pct: 5.0,
    moderate_high_hit_rate_pct: 25.0,
    moderate_high_random_baseline_pct: 9.9,
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-dialog max-w-2xl text-slate-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between bg-[#162032]">
          <div className="flex items-center gap-2.5">
            <ShieldAlert size={20} className="text-amber-400" />
            <div>
              <h3 className="text-base font-bold text-white">
                Methodology, Model Boundaries & Validation Limits
              </h3>
              <p className="text-xs text-slate-400">
                N²M Flood Prediction Model — Bengaluru Research Prototype
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

        {/* Modal Scrollable Body */}
        <div className="p-5 overflow-y-auto space-y-4 text-xs leading-relaxed max-h-[70vh]">
          {/* Critical Operational Guardrail Alert */}
          <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-200 space-y-1.5">
            <div className="flex items-center gap-1.5 font-bold text-rose-300">
              <AlertTriangle size={15} />
              CRITICAL OPERATIONAL NOTICE
            </div>
            <p>
              This project is an <strong>experimental spatial susceptibility ranking tool</strong> across 3,026 Bengaluru grid cells.
              It is <strong>NOT a calibrated flood forecast</strong>, NOT an early warning system, and NOT an emergency management tool.
            </p>
            <p className="text-[11px] text-rose-300/80">
              Model scores represent <em>relative spatial prioritization</em>, NOT predicted flood probabilities. Never use for life-safety or public alert dissemination.
            </p>
          </div>

          {/* Validation Metrics Grid */}
          <div className="space-y-2">
            <h4 className="font-semibold text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle size={14} className="text-emerald-400" />
              Strict Holdout Validation Benchmarks (September 2022 Event)
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
              <div className="p-2.5 rounded bg-[#162032] border border-white/5">
                <span className="text-[10px] text-slate-400 block">PR-AUC (Holdout)</span>
                <span className="text-base font-bold font-mono text-sky-400">
                  {stats.pr_auc}
                </span>
                <span className="text-[10px] text-slate-500 block">vs 0.0013 chance</span>
              </div>

              <div className="p-2.5 rounded bg-[#162032] border border-white/5">
                <span className="text-[10px] text-slate-400 block">Baseline Lift</span>
                <span className="text-base font-bold font-mono text-emerald-400">
                  ~2.0x
                </span>
                <span className="text-[10px] text-slate-500 block">above random</span>
              </div>

              <div className="p-2.5 rounded bg-[#162032] border border-white/5">
                <span className="text-[10px] text-slate-400 block">High Tier Hit Rate</span>
                <span className="text-base font-bold font-mono text-rose-400">
                  {stats.high_hit_rate_pct}%
                </span>
                <span className="text-[10px] text-slate-500 block">vs {stats.high_random_baseline_pct}% baseline</span>
              </div>

              <div className="p-2.5 rounded bg-[#162032] border border-white/5">
                <span className="text-[10px] text-slate-400 block">Mod+High Hit Rate</span>
                <span className="text-base font-bold font-mono text-amber-400">
                  {stats.moderate_high_hit_rate_pct}%
                </span>
                <span className="text-[10px] text-slate-500 block">vs {stats.moderate_high_random_baseline_pct}% baseline</span>
              </div>
            </div>
          </div>

          {/* Known Limitations List */}
          <div className="space-y-2 border-t border-white/10 pt-3">
            <h4 className="font-semibold text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
              <FileText size={14} className="text-sky-400" />
              Documented Limitations & Scientific Context
            </h4>
            <ul className="space-y-1.5 text-slate-300 list-disc list-inside">
              <li>
                <strong>Sparse Ground Truth:</strong> Ground truth labels cover only ~10 verified places across 6 historical flood events.
              </li>
              <li>
                <strong>Neighborhood Label Assumptions:</strong> Positive flood labels were assumed for neighboring cells (3x3 grid around documented locations).
              </li>
              <li>
                <strong>Rainfall Spatial Resolution:</strong> CHIRPS daily ~5 km gridded precipitation data cannot resolve hyper-local, short-duration convective cloudbursts.
              </li>
              <li>
                <strong>Statistical Interpretation:</strong> While PR-AUC shows ~2x lift over random chance, absolute precision remains low due to class imbalance (~99.9% non-flood cell-days).
              </li>
              <li>
                <strong>Dedicated Holdout Model:</strong> Historical replay uses <code className="text-sky-300">flood_xgb_holdout_E2022_09.json</code>, which was strictly held out from training on the September 2022 event.
              </li>
            </ul>
          </div>

          {/* Model Architecture */}
          <div className="border-t border-white/10 pt-3 space-y-1 text-slate-400 text-[11px]">
            <p>
              <strong>Architecture:</strong> Gradient-boosted decision trees (<code className="text-slate-300">xgboost.XGBClassifier</code>) trained with 18 features (8 dynamic CHIRPS precipitation aggregations + 10 static terrain/drainage indices).
            </p>
            <p>
              <strong>Daily Alert Rule:</strong> Top 150 cells = High (5%); Ranks 151–300 = Moderate (10%); Remaining 2,726 = None.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-3 border-t border-white/10 bg-[#0e1422] flex justify-end">
          <button onClick={onClose} className="btn-secondary text-xs px-4">
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
}
