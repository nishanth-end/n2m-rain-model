import React, { useState, useEffect } from 'react';
import { content } from '../config/content';
import { api } from '../api/client';
import { Send, Copy, Check, ShieldCheck, Lock, Terminal } from 'lucide-react';

export default function TelegramPage({ dates = [], selectedDate }) {
  const { telegram } = content;
  const [activeDate, setActiveDate] = useState(selectedDate || '2022-09-08');
  const [previewData, setPreviewData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    if (selectedDate) {
      setActiveDate(selectedDate);
    }
  }, [selectedDate]);

  useEffect(() => {
    if (!activeDate) return;

    let isMounted = true;
    setIsLoading(true);
    setError('');

    api
      .getTelegramPreview(activeDate)
      .then((data) => {
        if (isMounted) setPreviewData(data);
      })
      .catch((err) => {
        if (isMounted) setError(err.message || 'Failed to retrieve preview.');
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [activeDate]);

  const handleCopy = () => {
    if (previewData?.formatted_message) {
      navigator.clipboard.writeText(previewData.formatted_message);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  return (
    <div className="page-container page-container-narrow">
      <div className="tg-page-flow">
        {/* Editorial Header */}
        <div className="page-editorial-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Send size={20} className="text-water" />
            <span className="page-eyebrow" style={{ margin: 0 }}>
              Automated Messaging Sandbox
            </span>
          </div>
          <h1 className="page-title">{telegram.title}</h1>
          <p className="page-subtitle">{telegram.subtitle}</p>
        </div>

        {/* Safety Boundary Callout */}
        <div className="callout-box callout-amber">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 'bold', color: 'var(--tier-moderate)', marginBottom: '0.35rem' }}>
            <ShieldCheck size={16} />
            <span>Operational Safety Boundary & Sandbox Protocol</span>
          </div>
          <p style={{ marginBottom: '0.4rem' }}>{telegram.statusDescription}</p>
          <p style={{ fontSize: '11px', color: 'var(--ink-muted)', fontStyle: 'italic', margin: 0 }}>
            {telegram.warning}
          </p>
        </div>

        <div className="tg-grid">
          {/* Left Column: Configuration Guidelines */}
          <div className="tg-config-col">
            <div className="sim-section-header" style={{ paddingBottom: '0.4rem', marginBottom: 0 }}>
              <span style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--ink-primary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Lock size={14} className="text-water" />
                Bot Configuration Guidelines
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              <div>
                <span className="form-label" style={{ marginBottom: '0.25rem' }}>
                  Bot Handle Placeholder:
                </span>
                <div className="terminal-box" style={{ fontWeight: 600, color: 'var(--ink-primary)' }}>
                  {telegram.botPlaceholder}
                </div>
              </div>

              <div>
                <span className="form-label" style={{ marginBottom: '0.25rem' }}>
                  Active Integration Status:
                </span>
                <div className="terminal-box text-dim" style={{ fontSize: '11px' }}>
                  {telegram.status}
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.8rem', fontSize: '12px', color: 'var(--ink-secondary)', lineHeight: 1.5 }}>
                <span className="form-label" style={{ fontWeight: 'bold', color: 'var(--ink-primary)' }}>
                  Environment Secret Protocol:
                </span>
                <p style={{ margin: 0 }}>{telegram.tokenGuidance}</p>
                <div className="terminal-box" style={{ fontSize: '11px', marginTop: '0.4rem' }}>
                  TELEGRAM_ENABLED=false<br />
                  TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN<br />
                  TELEGRAM_CHAT_ID=PRIVATE_CHAT_ID
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Rendered Payload Terminal */}
          <div className="tg-preview-col">
            <div className="tg-preview-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Terminal size={15} className="text-water" />
                <span style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--ink-primary)' }}>
                  Rendered Alert Payload Preview
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <label htmlFor="telegram-date" className="form-label" style={{ margin: 0 }}>
                  Date:
                </label>
                <select
                  id="telegram-date"
                  value={activeDate}
                  onChange={(e) => setActiveDate(e.target.value)}
                  className="select-control"
                  style={{ padding: '0.2rem 0.5rem', fontSize: '11px', width: 'auto' }}
                >
                  {dates.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span className="form-label" style={{ margin: 0 }}>
                  Target: Private Sandbox Chat
                </span>
                <button
                  onClick={handleCopy}
                  disabled={!previewData?.formatted_message || isLoading}
                  className="btn-secondary btn-sm"
                >
                  {isCopied ? (
                    <>
                      <Check size={12} className="text-olive" />
                      <span style={{ color: '#16a34a', fontWeight: 'bold' }}>Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy size={12} />
                      <span>Copy Payload</span>
                    </>
                  )}
                </button>
              </div>

              {isLoading ? (
                <div className="terminal-box" style={{ textAlign: 'center', padding: '2rem' }}>
                  <div className="animate-spin" style={{ width: 16, height: 16, border: '2px solid var(--accent-water)', borderTopColor: 'transparent', borderRadius: '50%', margin: '0 auto 0.5rem' }}></div>
                  Rendering message payload for {activeDate}...
                </div>
              ) : error ? (
                <div className="callout-box callout-danger" style={{ fontFamily: 'var(--font-mono)' }}>
                  {error}
                </div>
              ) : (
                <div className="tg-terminal-display">
                  {previewData?.formatted_message}
                </div>
              )}

              <div style={{ fontSize: '11px', color: 'var(--ink-muted)', fontFamily: 'var(--font-mono)' }}>
                Source: <code>GET /api/telegram/demo-preview?date={activeDate}</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
