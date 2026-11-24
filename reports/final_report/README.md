# N²M Flood Prediction Model — Undergraduate Academic Project Report

**Project Title**: N²M Flood Prediction Model — An ML-Based Urban Flood Susceptibility Mapping and Visualization System for Bengaluru  
**Institution**: Department of Computer Science & Engineering, Dayananda Sagar College of Engineering, Bengaluru  
**Degree**: Bachelor of Engineering in Computer Science and Engineering  
**Academic Year**: 2026 – 2027  
**Faculty Project Advisor**: Dr. Punith Kumar, Associate Professor  
**Student Authors**:  
- **Nishanth G M** (Data Pipeline, Hydrological Features & GIS Extraction)  
- **Mohith M** (Machine Learning Model, Class Imbalance Tuning & Validation)  
- **Nihal Rao** (Full-Stack Architecture, Map Visualization & Demonstration Bot)  

---

## 1. Project Report Deliverables

This directory contains the revised, genuine undergraduate engineering mini-project report (35 pages) written specifically for a second-year Computer Science and Engineering student team. The tone is clear, direct, and academically honest, avoiding exaggerated corporate vocabulary while thoroughly documenting what was actually built, evaluated, and deployed.

| Deliverable File | Format | Size / Pages | Description |
| :--- | :---: | :---: | :--- |
| **`N2M_Project_Report.pdf`** | PDF Document | 1.4 MB (**35 Pages**) | The final rendered undergraduate mini-project report. Formatted to engineering college standards with Cover Page, Abstract, Table of Contents, Lists of Figures/Tables/Abbreviations, Chapters 1–7, embedded diagrams, tables, and IEEE references. |
| **`N2M_Project_Report.docx`** | Word (.docx) | 1.4 MB | Fully editable Microsoft Word version with professional styling, Deep Navy palette, custom table formatting, callouts, and 300 DPI figures. |
| **`report.md`** | Markdown | 80 kB (11,731 words) | Complete Markdown source document containing the entire text of the revised student report. |
| **`references.md`** | Markdown | 2.8 kB | Verified bibliographic records for all cited peer-reviewed papers (2015–2026) with valid DOI links. |
| **`figures/`** | Directory | 13 PNG files | High-resolution architectural schematics, data processing workflows, and rainfall distribution charts. |
| **`screenshots/`** | Directory | PNG + JPG | Genuine screenshot of the deployed React Leaflet Canvas interface (`flood_map_interface_overview.png`), plus capture guide. |

---

## 2. Report Chapter Structure (35 Pages)

- **Front Matter (Pages 1–6)**
  - Page 1: Cover Page (DSCE, CSE Department, Project Title, Student Names & Roles, Advisor, Academic Year)
  - Page 2: Abstract & Keywords (Problem background, 3,026 cells, XGBoost ranking, 2.0× lift, plain summary)
  - Pages 3–4: Table of Contents
  - Pages 5–6: List of Figures, List of Tables, and List of Abbreviations
- **Chapter 1: Introduction (Pages 7–9)**
  - 1.1 Background of Urban Flooding
  - 1.2 Urban Flooding Challenges in Bengaluru (198 wards, 93% concrete cover, lake cascades, rajakaluves)
  - 1.3 Why Machine Learning Helps in Flood Susceptibility Studies
  - 1.4 Motivation for the Project (Student motivation living in Bengaluru)
  - 1.5 Project Objectives (5 core student project goals)
  - 1.6 Scope and Practical Limitations (Relative ranking, experimental research, not an operational warning)
  - 1.7 Organization of the Report
- **Chapter 2: Literature Review (Pages 10–12)**
  - 2.1 Urban Flood Susceptibility Mapping Approaches
  - 2.2 Machine Learning in Flood-Related Studies
  - 2.3 Rainfall and Hydrological Studies in Bengaluru
  - 2.4 Technology-Enabled Flood Information Platforms
  - 2.5 Table 1: Comparative Summary of Reviewed Literature (6 papers compared across 4 axes)
  - 2.6 Project Motivation and Identified Gaps
- **Chapter 3: Problem Statement and Proposed Solution (Pages 13–15)**
  - 3.1 Problem Statement
  - 3.2 Existing Challenges (Label sparsity, convective rain variation, browser map lag, free cloud hosting)
  - 3.3 Proposed Solution (4-layer geospatial architecture)
  - 3.4 Functional Requirements (Table 2: FR-1 to FR-8)
  - 3.5 Non-Functional Requirements (Table 3: NFR-1 to NFR-6)
  - 3.6 Scope and Operational Boundaries
- **Chapter 4: System Design and Architecture (Pages 16–20)**
  - 4.1 Overall System Architecture (Figure 1)
  - 4.2 Geospatial Data Processing Pipeline (Figure 2)
  - 4.3 Machine Learning Component
  - 4.4 Backend Architecture and REST API (Table 4: 10 production endpoints)
  - 4.5 Frontend Web Application and Map Architecture (Leaflet Canvas 60 FPS)
  - 4.6 Historical Replay Mechanism (24-day September 2022 sequence)
  - 4.7 Telegram Demonstration Bot Integration (Token isolation, whitelist access)
  - 4.8 Cloud Deployment Architecture (Render + Vercel)
- **Chapter 5: Methodology (Pages 21–26)**
  - 5.1 Dataset and Data Sources (Table 5: SRTM DEM, ESA WorldCover, OSM, CHIRPS)
  - 5.2 Spatial Grid Discretization (3,026 uniform cells, 500 m × 500 m, 0.25 km² each)
  - 5.3 Input Features and Descriptions (Table 6: Complete 18 features — 10 static terrain + 8 dynamic rainfall)
  - 5.4 Data Preprocessing and Feature Calculation (D8 flow, TWI, HAND, Euclidean distances)
  - 5.5 Ground-Truth Flood Labels and Extreme Imbalance (Table 7: 6 events, 240 positive cell-days, 0.0136%)
  - 5.6 Model Selection and XGBoost Configuration (Table 8: Hyperparameters, `scale_pos_weight = 89.16`)
  - 5.7 Daily Susceptibility Ranking Methodology (Figure 3 & Table 9: High, Moderate, Baseline tiers)
  - 5.8 Out-of-Sample Holdout Evaluation Protocol (September 2022 benchmark)
- **Chapter 6: Implementation and Results (Pages 27–32)**
  - 6.1 Technologies and Tools Used (Table 11: Python, FastAPI, React, Vite, Leaflet, XGBoost)
  - 6.2 Data Pipeline Implementation
  - 6.3 Machine Learning and Ranking Implementation (Core Python code listing)
  - 6.4 Backend Service Implementation
  - 6.5 Frontend Map Implementation (Figure 4: Genuine UI screenshot)
  - 6.6 Historical Replay and Rainfall Trends (Figure 5: September 2022 rainfall profile, Cell #722 peak 0.2191)
  - 6.7 Telegram Demonstration Bot Implementation
  - 6.8 Automated Testing Suite (Table 12: 82/82 passing tests across 4 modules)
  - 6.9 Deployment Setup on Vercel and Render
  - 6.10 Experimental Results and Plain Language Explanation (Table 10: 2.0× PR-AUC lift, 2.53× enrichment)
- **Chapter 7: Conclusion and Future Scope (Pages 33–34)**
  - 7.1 Project Summary
  - 7.2 What the Group Successfully Implemented (5 key student milestones)
  - 7.3 Main Engineering Observations
  - 7.4 Practical Limitations
  - 7.5 Future Work and Scope for Improvement (KSNDMC rain gauges, IMD NWP forecasts, 1D/2D SWMM coupling)
- **References (Page 35)**
  - 10 Verified Citations in IEEE Style with active DOI links.

---

## 3. Recompilation Instructions

All deliverables are generated automatically from the source files using:

```bash
# 1. Assemble Markdown source (report.md)
./.venv/bin/python reports/final_report/assemble_report.py

# 2. Compile Word Document (N2M_Project_Report.docx)
./.venv/bin/python reports/final_report/compile_student_docx.py

# 3. Render PDF via LibreOffice headless (N2M_Project_Report.pdf)
/Applications/LibreOffice.app/Contents/MacOS/soffice --headless --convert-to pdf --outdir reports/final_report reports/final_report/N2M_Project_Report.docx
```
