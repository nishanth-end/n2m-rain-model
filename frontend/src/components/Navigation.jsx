import React, { useState } from 'react';
import { Compass, Map, Activity, Send, Users, Menu, X } from 'lucide-react';
import { content } from '../config/content';

export default function Navigation({ activeTab, onSelectTab, apiStatus }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const tabs = [
    { id: 'home', label: 'Home', icon: Compass },
    { id: 'map', label: 'Flood Map', icon: Map },
    { id: 'simulation', label: 'Live & Simulation', icon: Activity },
    { id: 'telegram', label: 'Telegram', icon: Send },
    { id: 'creators', label: 'Maintainers & Creators', icon: Users },
  ];

  return (
    <nav className="nav-header">
      <div className="nav-inner">
        {/* Brand Group */}
        <button
          onClick={() => onSelectTab('home')}
          className="nav-brand"
          aria-label="Return to Home"
        >
          <div className="nav-brand-icon">
            <Compass size={18} />
          </div>
          <div className="nav-brand-text">
            <div className="nav-brand-title-row">
              <span className="nav-brand-title">{content.brand.name}</span>
              <span className="badge badge-water">Replay V1</span>
            </div>
            <p className="nav-brand-sub">
              {content.brand.location} • 3,026 Cell Hydrological Mesh
            </p>
          </div>
        </button>

        {/* Desktop Navigation Links */}
        <div className="nav-links-desktop">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`nav-tab-btn ${isActive ? 'active' : ''}`}
              >
                <Icon size={14} className="nav-icon" />
                <span>{tab.label}</span>
              </button>
            );
          })}

          {/* Backend Health Telemetry */}
          <div className="nav-status">
            <span
              className={`status-dot ${
                apiStatus === 'online'
                  ? 'online'
                  : apiStatus === 'offline'
                  ? 'offline'
                  : 'checking'
              }`}
            />
            <span>
              {apiStatus === 'online'
                ? 'API Online'
                : apiStatus === 'offline'
                ? 'API Offline'
                : 'Connecting'}
            </span>
          </div>
        </div>

        {/* Mobile Menu Toggle Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="nav-mobile-toggle"
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      <div className={`nav-drawer-mobile ${mobileMenuOpen ? 'open' : ''}`}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                onSelectTab(tab.id);
                setMobileMenuOpen(false);
              }}
              className={`nav-drawer-btn ${isActive ? 'active' : ''}`}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
