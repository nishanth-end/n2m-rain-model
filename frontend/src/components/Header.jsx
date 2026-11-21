import React from 'react';
import { ShieldAlert, BookOpen, Send, Radio, MapPin, RefreshCw } from 'lucide-react';

export default function Header({
  apiStatus,
  onRefresh,
  onOpenAbout,
  onOpenTelegram,
  onOpenPipeline,
  isLoading
}) {
  return (
    <header className="border-b border-white/10 bg-[#0e1422] px-4 py-3 sticky top-0 z-40">
      <div className="max-w-[1700px] mx-auto flex flex-wrap items-center justify-between gap-3">
        {/* Branding & Subtitle */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-sky-950/80 border border-sky-500/40 flex items-center justify-center text-sky-400 shadow-sm shadow-sky-500/10">
            <ShieldAlert size={20} className="text-sky-400" />
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="font-extrabold tracking-wider text-lg text-white font-mono">
                N²M MODEL
              </span>
              <span className="badge-replay">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                HISTORICAL REPLAY
              </span>
              <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                <MapPin size={12} className="text-slate-500" />
                <span>Bengaluru, India</span>
              </div>
            </div>
            <p className="text-xs text-slate-400 tracking-tight">
              Experimental Urban Flood Susceptibility Mapping & Spatial Ranking
            </p>
          </div>
        </div>

        {/* Status & Navigation Actions */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* API Health Pill */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#162032] border border-white/10 text-xs">
            <Radio
              size={14}
              className={
                apiStatus === 'online'
                  ? 'text-emerald-400 animate-pulse'
                  : apiStatus === 'offline'
                  ? 'text-rose-400'
                  : 'text-amber-400 animate-spin'
              }
            />
            <span className="text-slate-300 font-mono">
              {apiStatus === 'online'
                ? 'API CONNECTED'
                : apiStatus === 'offline'
                ? 'API OFFLINE'
                : 'CONNECTING...'}
            </span>
            <button
              onClick={onRefresh}
              title="Refresh connection"
              className="text-slate-400 hover:text-white transition-colors ml-0.5"
            >
              <RefreshCw size={12} className={isLoading ? 'animate-spin' : ''} />
            </button>
          </div>

          {/* Pipeline Scaffolding Button */}
          <button
            onClick={onOpenPipeline}
            className="btn-ghost text-xs"
            title="Inspect Live Pipeline Scaffolding Status"
          >
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-slate-500"></span>
            <span>Pipeline Scaffolding</span>
          </button>

          {/* Telegram Demo Button */}
          <button
            onClick={onOpenTelegram}
            className="btn-secondary text-xs"
            title="Telegram Demonstration Preview"
          >
            <Send size={13} className="text-sky-400" />
            <span>Telegram Demo</span>
          </button>

          {/* Methodology & Limitations Button */}
          <button
            onClick={onOpenAbout}
            className="btn-primary text-xs"
            title="Model Methodology and Known Validation Limits"
          >
            <BookOpen size={13} />
            <span>Methodology & Limits</span>
          </button>
        </div>
      </div>
    </header>
  );
}
