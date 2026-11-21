import React from 'react';
import { content } from '../config/content';
import { Compass, ShieldAlert } from 'lucide-react';

export default function Footer({ onSelectTab }) {
  return (
    <footer className="app-footer">
      <div className="footer-inner">
        <div className="footer-top">
          <div className="footer-brand-col">
            <div className="footer-brand-title">
              <Compass size={16} className="text-water" />
              <span>{content.brand.name}</span>
            </div>
            <p className="footer-brand-desc">
              {content.brand.tagline}
            </p>
            <p className="footer-brand-meta">
              {content.creators.institution} • {content.creators.department}
            </p>
          </div>

          <div className="footer-links-group">
            <div className="footer-nav-col">
              <span className="footer-heading">Platform Modules</span>
              <ul className="footer-list">
                <li>
                  <button onClick={() => onSelectTab('home')} className="footer-link-btn">
                    Home & Overview
                  </button>
                </li>
                <li>
                  <button onClick={() => onSelectTab('map')} className="footer-link-btn">
                    Spatial Replay Map
                  </button>
                </li>
                <li>
                  <button onClick={() => onSelectTab('simulation')} className="footer-link-btn">
                    Live Data & Simulation Lab
                  </button>
                </li>
              </ul>
            </div>

            <div className="footer-nav-col">
              <span className="footer-heading">Documentation</span>
              <ul className="footer-list">
                <li>
                  <button onClick={() => onSelectTab('telegram')} className="footer-link-btn">
                    Telegram Sandbox
                  </button>
                </li>
                <li>
                  <button onClick={() => onSelectTab('creators')} className="footer-link-btn">
                    Maintainers & Provenance
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-disclaimer">
            <ShieldAlert size={14} className="text-mod" />
            <span>
              Academic research model. Outputs represent spatial relative susceptibility index scores, not hydraulic inundation forecasts or civil emergency alerts.
            </span>
          </div>
          <span className="footer-event-tag">
            {content.brand.monsoonEvent} • E2022_09
          </span>
        </div>
      </div>
    </footer>
  );
}
