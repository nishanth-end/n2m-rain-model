import React, { useState, useEffect } from 'react';
import { content } from '../config/content';
import { api } from '../api/client';
import { Send, Copy, Check, ShieldCheck, Lock, Terminal, Radio, Info, AlertTriangle, MessageSquare } from 'lucide-react';

export default function TelegramPage({ dates = [], selectedDate }) {
  const { telegram } = content;
  const [activeDate, setActiveDate] = useState(selectedDate || '2022-09-08');
  const [previewData, setPreviewData] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isCopied, setIsCopied] = useState(false);
  const [sendResult, setSendResult] = useState(null);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    if (selectedDate) {
      setActiveDate(selectedDate);
    }
  }, [selectedDate]);

  // Fetch bot configuration status
  useEffect(() => {
    api
      .getTelegramStatus()
      .then((data) => setBotStatus(data))
      .catch((err) => console.error('Failed to get bot status:', err));
  }, []);

  // Fetch preview for selected date
  useEffect(() => {
    if (!activeDate) return;

    let isMounted = true;
    setIsLoading(true);
    setError('');
    setSendResult(null);

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

  const handleSendDemo = () => {
    setIsSending(true);
    setSendResult(null);
    api
      .sendTelegramDemo(activeDate)
      .then((res) => {
        setSendResult(res);
        setIsSending(false);
      })
      .catch((err) => {
        setSendResult({
          sent: false,
          reason: err.message || 'Failed to dispatch request.'
        });
        setIsSending(false);
      });
  };

  const isEnabled = botStatus?.enabled;
  const isConfigured = botStatus?.configured;

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
          {/* Left Column: Configuration Guidelines & Status */}
          <div className="tg-config-col">
            <div className="sim-section-header" style={{ paddingBottom: '0.4rem', marginBottom: 0 }}>
              <span style={{ fontFamily: 'var(--font-serif)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--ink-primary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Lock size={14} className="text-water" />
                Bot Configuration & Access Control
              </span>
              <span className="badge">
                {isEnabled && isConfigured ? 'LIVE DISPATCH CONFIGURED' : 'PRIVATE SANDBOX'}
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              <div>
                <span className="form-label" style={{ marginBottom: '0.25rem' }}>
                  Bot Handle / Username:
                </span>
                <div className="terminal-box" style={{ fontWeight: 600, color: 'var(--ink-primary)' }}>
                  {botStatus?.bot_username ? `@${botStatus.bot_username}` : telegram.botPlaceholder}
                </div>
              </div>

              <div>
                <span className="form-label" style={{ marginBottom: '0.25rem' }}>
                  Connection & Access State:
                </span>
                <div className="terminal-box text-dim" style={{ fontSize: '11px', lineHeight: 1.5 }}>
                  <strong>Operational Mode:</strong> {botStatus?.mode || 'private_academic_demo'}<br />
                  <strong>Live Token:</strong> {botStatus?.token_configured ? 'Configured (Server-Side Secret)' : 'Not Set (Sandbox Preview Mode)'}<br />
                  <strong>Authorized Chats:</strong> {botStatus?.authorized_chats_count ?? 0} Evaluator(s) Allowed
                </div>
              </div>

              {/* Bot Commands Directory */}
              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.8rem' }}>
                <span className="form-label" style={{ fontWeight: 'bold', color: 'var(--ink-primary)', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <MessageSquare size={13} className="text-olive" />
                  Supported Private Commands
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                  <div style={{ padding: '3px 6px', background: 'var(--bg-subtle)', borderRadius: 3 }}>
                    <strong>/start</strong> — Project overview & scientific boundaries
                  </div>
                  <div style={{ padding: '3px 6px', background: 'var(--bg-subtle)', borderRadius: 3 }}>
                    <strong>/help</strong> — Command manual & usage instructions
                  </div>
                  <div style={{ padding: '3px 6px', background: 'var(--bg-subtle)', borderRadius: 3 }}>
                    <strong>/status</strong> — Telemetry status & simulated notices
                  </div>
                  <div style={{ padding: '3px 6px', background: 'var(--bg-subtle)', borderRadius: 3 }}>
                    <strong>/demo [YYYY-MM-DD]</strong> — Dispatch experimental alert summary
                  </div>
                </div>
              </div>

              {/* Environment Setup Protocol */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.8rem', fontSize: '12px', color: 'var(--ink-secondary)', lineHeight: 1.5 }}>
                <span className="form-label" style={{ fontWeight: 'bold', color: 'var(--ink-primary)' }}>
                  Server-Side Secret Configuration:
                </span>
                <p style={{ margin: 0 }}>
                  To enable private test dispatch, configure environment variables in your server's <code>.env</code> file. Tokens are never exposed to the frontend.
                </p>
                <div className="terminal-box" style={{ fontSize: '11px', marginTop: '0.4rem' }}>
                  TELEGRAM_ENABLED=false<br />
                  TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN<br />
                  TELEGRAM_CHAT_ID=YOUR_PRIVATE_CHAT_ID<br />
                  TELEGRAM_AUTHORIZED_CHAT_IDS=CHAT_ID_1,CHAT_ID_2
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
                  Target: Private Evaluator Sandbox
                </span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <button
                    onClick={handleSendDemo}
                    disabled={isSending || isLoading}
                    className="btn btn-primary btn-sm"
                    title="Dispatch test message via backend"
                  >
                    <Send size={11} className={isSending ? 'spin' : ''} />
                    {isSending ? 'Sending...' : 'Send Demo Alert'}
                  </button>
                  <button
                    onClick={handleCopy}
                    disabled={!previewData?.formatted_message || isLoading}
                    className="btn btn-secondary btn-sm"
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
              </div>

              {/* Send feedback notice */}
              {sendResult && (
                <div className={`callout-box ${sendResult.sent ? 'callout-green' : 'callout-amber'}`} style={{ padding: '0.5rem 0.8rem', fontSize: '11px' }}>
                  {sendResult.sent ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#166534' }}>
                      <Check size={14} />
                      <span><strong>Alert Delivered:</strong> Message sent successfully to authorized private chat.</span>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#854d0e' }}>
                      <Info size={14} />
                      <span><strong>Notice:</strong> {sendResult.reason || sendResult.error || 'Demonstration dispatch blocked by configuration.'}</span>
                    </div>
                  )}
                </div>
              )}

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
