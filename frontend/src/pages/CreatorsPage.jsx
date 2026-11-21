import React from 'react';
import { content } from '../config/content';
import { Users, GraduationCap, BookOpen, Database, Wrench, Mail, Github } from 'lucide-react';

export default function CreatorsPage() {
  const { creators } = content;

  return (
    <div className="page-container page-container-narrow">
      <div className="creators-page-flow">
        {/* Editorial Header */}
        <div className="page-editorial-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Users size={20} className="text-water" />
            <span className="page-eyebrow" style={{ margin: 0 }}>
              Academic Provenance & Research Team
            </span>
          </div>
          <h1 className="page-title">{creators.title}</h1>
          <p className="page-subtitle">{creators.subtitle}</p>
        </div>

        {/* Academic Institution Header Plate */}
        <section className="affiliation-plate">
          <span className="form-label" style={{ textTransform: 'uppercase' }}>
            Academic Affiliation
          </span>
          <h2 className="affiliation-title">
            {creators.institution}
          </h2>
          <p className="text-mono" style={{ fontSize: '13px', color: 'var(--ink-secondary)', margin: 0 }}>
            {creators.department}
          </p>
        </section>

        {/* Faculty Advisor Section */}
        <section className="sim-section">
          <div className="sim-section-header">
            <div className="sim-section-title-group">
              <GraduationCap size={16} className="text-olive" />
              <h3 className="section-title" style={{ fontSize: '1.15rem', margin: 0 }}>
                Faculty Project Supervision
              </h3>
            </div>
          </div>

          <div className="faculty-card">
            <div className="faculty-header-row">
              <h4 className="faculty-name">{creators.facultyGuide.name}</h4>
              <span className="badge badge-water">{creators.facultyGuide.role}</span>
            </div>
            <p className="text-mono" style={{ fontSize: '13px', color: 'var(--ink-secondary)', margin: 0 }}>
              {creators.facultyGuide.designation}
            </p>
            <p style={{ fontSize: '12px', color: 'var(--ink-muted)', margin: 0 }}>
              {creators.facultyGuide.affiliation}
            </p>
          </div>
        </section>

        {/* Engineering Research Team */}
        <section className="sim-section">
          <div className="sim-section-header">
            <h3 className="section-title" style={{ fontSize: '1.15rem', margin: 0 }}>
              Project Contributors & Roles
            </h3>
            <span className="page-eyebrow" style={{ margin: 0 }}>Team N²M</span>
          </div>

          <div className="team-grid">
            {creators.teamMembers.map((member, idx) => (
              <div key={idx} className="team-member-card">
                <div className="team-member-header">
                  <h4 className="team-member-name">{member.name}</h4>
                  <span className="text-mono text-water" style={{ fontSize: '11px', fontWeight: 600 }}>
                    Member 0{idx + 1}
                  </span>
                </div>
                <p className="team-member-role">{member.role}</p>
                <p style={{ fontSize: '12px', color: 'var(--ink-secondary)', lineHeight: 1.5, margin: 0 }}>
                  {member.contribution}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Dataset Provenance & Attribution */}
        <section className="sim-section">
          <div className="sim-section-header">
            <div className="sim-section-title-group">
              <Database size={16} className="text-water" />
              <h3 className="section-title" style={{ fontSize: '1.15rem', margin: 0 }}>
                Dataset Provenance & Spatial Repositories
              </h3>
            </div>
          </div>

          <div className="datasets-grid">
            {creators.datasetCredits.map((ds, idx) => (
              <div key={idx} className="dataset-card">
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <h4 className="dataset-title">{ds.title}</h4>
                  <span className="text-mono text-dim" style={{ fontSize: '11px' }}>{ds.source}</span>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--ink-secondary)', lineHeight: 1.45, margin: 0 }}>
                  {ds.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Tooling and Libraries */}
        <section className="sim-section">
          <div className="sim-section-header">
            <div className="sim-section-title-group">
              <Wrench size={15} className="text-dim" />
              <h3 className="section-title" style={{ fontSize: '1.15rem', margin: 0 }}>
                Core Computation & Software Tooling
              </h3>
            </div>
          </div>

          <div className="tooling-grid">
            {creators.tooling.map((t, idx) => (
              <div key={idx} className="tool-chip">
                <span className="tool-name">{t.name}</span>
                <span className="tool-role">{t.role}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Acknowledgements */}
        <section className="editorial-plate">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <BookOpen size={16} className="text-olive" />
            <h3 className="section-title" style={{ fontSize: '1.05rem', margin: 0 }}>
              Acknowledgements
            </h3>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--ink-secondary)', lineHeight: 1.6, margin: 0 }}>
            {creators.acknowledgements}
          </p>
        </section>

        {/* Contact & Repository */}
        <div className="contact-row">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--ink-primary)' }}>
            <Mail size={14} className="text-water" />
            <span>{creators.contact.email}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--ink-primary)' }}>
            <Github size={14} className="text-ink" />
            <span>{creators.contact.github}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
