import React, { useState, useEffect } from 'react';
import { X, Send, Copy, Check, ShieldCheck, AlertCircle } from 'lucide-react';
import { api } from '../api/client';

export default function TelegramModal({ isOpen, onClose, selectedDate, dates = [] }) {
  const [activeDate, setActiveDate] = useState(selectedDate);
  const [previewData, setPreviewData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    setActiveDate(selectedDate);
  }, [selectedDate]);

  useEffect(() => {
    if (!isOpen || !activeDate) return;

    let isMounted = true;
    setIsLoading(true);
    setError('');

    api
      .getTelegramPreview(activeDate)
      .then((data) => {
        if (isMounted) setPreviewData(data);
      })
      .catch((err) => {
        if (isMounted) setError(err.message || 'Failed to load Telegram preview.');
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, activeDate]);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (previewData?.formatted_message) {
      navigator.clipboard.writeText(previewData.formatted_message);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-dialog max-w-xl text-slate-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between bg-[#162032]">
          <div className="flex items-center gap-2.5">
            <Send size={18} className="text-sky-400" />
            <div>
              <h3 className="text-base font-bold text-white">
                Telegram Dispatch Demo (Sandbox Preview)
              </h3>
              <p className="text-xs text-slate-400">
                Inspect simulated notification formatting without network dispatch
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

        {/* Modal Body */}
        <div className="p-4 overflow-y-auto space-y-3.5 text-xs">
          {/* Safety Banner */}
          <div className="p-2.5 rounded bg-emerald-950/40 border border-emerald-500/30 text-emerald-200 text-[11px] flex items-start gap-2">
            <ShieldCheck size={16} className="text-emerald-400 shrink-0 mt-0.5" />
            <span>
              <strong>Safe Sandbox Mode:</strong> Real Telegram delivery is <strong>disabled by default</strong> (<code className="text-emerald-300">TELEGRAM_ENABLED=false</code>). This panel renders message formatting in memory without hitting Telegram bot APIs.
            </span>
          </div>

          {/* Date Picker Selector */}
          <div className="flex items-center justify-between bg-[#1e293b] p-2 rounded-md border border-white/5">
            <span className="text-slate-300 font-medium">Replay Evaluation Date:</span>
            <select
              value={activeDate}
              onChange={(e) => setActiveDate(e.target.value)}
              className="bg-[#111827] text-white border border-white/10 rounded px-2.5 py-1 font-mono text-xs focus:outline-none focus:border-sky-500"
            >
              {dates.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Message Preview Box */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">
                Rendered Message Template
              </span>
              <button
                onClick={handleCopy}
                disabled={!previewData?.formatted_message || isLoading}
                className="btn-ghost text-xs py-1 px-2 text-sky-400 hover:text-sky-300"
              >
                {isCopied ? (
                  <>
                    <Check size={12} className="text-emerald-400" />
                    <span className="text-emerald-400">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy size={12} />
                    <span>Copy Text</span>
                  </>
                )}
              </button>
            </div>

            {isLoading ? (
              <div className="p-8 text-center text-slate-500 bg-[#080b11] border border-white/10 rounded-lg">
                <div className="w-5 h-5 border-2 border-sky-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                Generating message preview for {activeDate}...
              </div>
            ) : error ? (
              <div className="p-3 bg-rose-950/40 border border-rose-500/30 rounded-lg text-rose-300 flex items-center gap-2">
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            ) : (
              <div className="p-3.5 bg-[#080b11] border border-white/10 rounded-lg font-mono text-[11px] text-slate-300 whitespace-pre-wrap leading-relaxed max-h-[300px] overflow-y-auto">
                {previewData?.formatted_message}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-3 border-t border-white/10 bg-[#0e1422] flex items-center justify-between">
          <span className="text-[10px] text-slate-500">
            Source: <code className="text-slate-400">/api/telegram/demo-preview</code>
          </span>
          <button onClick={onClose} className="btn-secondary text-xs px-4">
            Close Preview
          </button>
        </div>
      </div>
    </div>
  );
}
