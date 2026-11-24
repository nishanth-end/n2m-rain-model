# N²M Flood Prediction Model — Project Fact Sheet

This document compiles all verified empirical and architectural facts extracted directly from the codebase, ML training assets, spatial datasets, API definitions, test suites, and frontend components of the **N²M Flood Prediction Model** repository.

---

## 1. Project Identification
- **Full Project Name**: N²M Flood Prediction Model — An ML-Based Urban Flood Susceptibility Mapping and Visualization System for Bengaluru
- **Short Name**: N²M Model (named after student team: Nishanth G M, Nihal Rao, Mohith M)
- **Academic Context**: Undergraduate Engineering Mini-Project
- **Department**: Department of Computer Science & Engineering
- **Institution**: Dayananda Sagar College of Engineering, Bengaluru, Karnataka, India
- **Faculty Project Advisor**: Dr. Punith Kumar, Associate Professor, Dept. of CSE
- **Student Contributors & Roles**:
  - **Nishanth G M**: Data Pipeline & Hydrological Terrain Feature Extraction
  - **Mohith M**: Machine Learning Modeling & Holdout Validation
  - **Nihal Rao**: Full-Stack Architecture, GIS Interface & Cartographic Rendering
- **Contact / Repository**: `https://github.com/nishanth-end/n2m-rain-model`

---

## 2. Problem Definition & Objectives
- **Core Problem**: Rapid, uncontrolled urbanization in Bengaluru (built-up cover expanded from <8% in 1973 to >93% in 2020) has encroached on interconnected lake cascades (*keres*) and natural drainage channels (*rajakaluves*). Monsoonal convective storms frequently produce intense localized downpours (70–120 mm within 90 minutes) that overwhelm micro-catchments. Existing civic flood warnings remain generalized at the BBMP municipal or taluk scale, providing zero actionable spatial differentiation for micro-catchments, underpasses, and low-lying valleys.
- **Specific Objectives**:
  1. Construct a structured, reproducible geospatial data ingestion and feature extraction pipeline partitioning Bengaluru into a uniform spatial grid.
  2. Implement an explainable machine learning model (XGBoost) to evaluate relative daily flood susceptibility.
  3. Formulate a rank-based spatial thresholding protocol (top 5% High, next 5% Moderate, remaining 90% Baseline) avoiding arbitrary uncalibrated probability thresholds.
  4. Develop an interactive cartographic web dashboard (React, Vite, Leaflet, Canvas) supporting historical flood replay.
  5. Build a decoupled asynchronous backend API (FastAPI) providing sub-second spatial querying and filtering across 3,026 cells.
  6. Implement a private Telegram demonstration bot interface for automated event bulletin dispatch to authorized project evaluators.
  7. Formally evaluate the model using strict temporal holdout validation (September 2022 event, $E2022\_09$) and document all empirical constraints.

---

## 3. Study Area & Spatial Discretization
- **Geographic Focus**: Greater Bengaluru (Bruhat Bengaluru Mahanagara Palike — BBMP administrative boundary), Karnataka, India.
- **Bounding Box**: Latitudes $12.834^\circ\text{N}$ to $13.143^\circ\text{N}$, Longitudes $77.460^\circ\text{E}$ to $77.784^\circ\text{E}$.
- **Mapped Area**: 711.59 km² across all 198 administrative wards (2011 delimitation).
- **Spatial Mesh**: Uniform Cartesian grid of **3,026 cells** (~500 m × 500 m, 0.25 km² per nominal cell).
  - 2,674 interior full cells.
  - 352 boundary-clipped peripheral cells.
- **Drainage Valleys Covered**:
  - Vrishabhavathi Valley (Western / South-Western drainage).
  - Koramangala–Challaghatta (KC) Valley (Central / South-Eastern drainage; major IT corridor).
  - Hebbal Valley (Northern drainage).

---

## 4. Datasets & Provenance
| Dataset Name | Provider / Source | Native Resolution | Temporal Span | Role in System |
| :--- | :--- | :--- | :--- | :--- |
| **CHIRPS Daily Rainfall** | Climate Hazards Center (UC Santa Barbara) | 0.05° (~5.3 km) | 2017–2023 (May–Nov) | Dynamic antecedent precipitation features |
| **SRTM DEM** | NASA / USGS | 1 Arc-Second (~30 m) | Static (2000 mission) | Topography, slope, flow accumulation, TWI |
| **Copernicus GLO-30 DEM** | European Space Agency (ESA) | 30 m | Static | Elevation validation and HAND derivation |
| **OpenStreetMap (OSM)** | OpenStreetMap Contributors (ODbL) | Vector | Dynamic extracts | Lakes (*keres*), drains (*rajakaluves*), arterial roads |
| **ESA WorldCover** | European Space Agency (ESA) | 10 m | 2020 / 2021 | Impervious surface fraction proxy |
| **Flood Situation Reports** | BBMP & KSNDMC Situation Bulletins | Point locations | 2017, 2021, 2022, 2023 | Ground truth flood event records & seed cells |

---

## 5. Master Training Matrix & Historical Events
- **Master Dataset File**: `data/flood_dataset.parquet` (delivery clone: `delivery/flood_dataset.parquet`).
- **Dimensions**: 1,764,158 rows × 42 columns.
- **Candidate Stormy Days**: Exactly 583 calendar days selected across May 1 to November 30 in 2017, 2021, 2022, and 2023 (rule: max citywide 3-day rainfall $\ge 10\text{ mm}$ or within $[-14, +7]$ days of documented flood events).
- **Positive Cell-Day Count**: Exactly 240 positive labels ($0.0136\%$ positive prevalence; class imbalance ratio $\approx 1 : 7,350$).
- **Historical Events (6 Events)**:
  1. `E2017_08` (Aug 2017): 1 seed day, 8 buffer positives = 9 positives. (Koramangala 4th Block).
  2. `E2017_09` (Sep 2017): 2 seed days, 16 buffer positives = 18 positives. (Bilekahalli / HSR).
  3. `E2021_11` (Nov 2021): 1 seed day, 8 buffer positives = 9 positives. (Kendriya Vihar, Yelahanka).
  4. `E2022_05` (May 2022): 1 seed day, 6 buffer positives = 7 positives. (RBD Layout / Sarjapur Road).
  5. `E2022_09` (Sep 2022 holdout): 24 seed days, 164 buffer positives = 188 positives. (Ecospace, Rainbow Drive, Outer Ring Road, Mahadevapura).
  6. `E2023_05` (May 2023): 1 seed day, 8 buffer positives = 9 positives. (KR Circle Underpass).
- **Distinct Seed Cells**: 10 unique cells (`[555, 666, 774, 847, 897, 910, 977, 1444, 1478, 2882]`).
- **Spatial Label Expansion**: $3 \times 3$ topological grid buffer (seed cell + 8 contiguous neighbors) to capture overland water pooling.

---

## 6. Input Features (18 Model Features)
The XGBoost model takes exactly 18 features defined in `features.json`:

### Dynamic Rainfall Features (8)
1. `rain_1d_mm`: Observation day 24h precipitation (0.0 to 82.5 mm).
2. `rain_3d_mm`: Rolling 3-day precipitation sum (0.0 to 145.0 mm).
3. `rain_7d_mm`: Rolling 7-day precipitation sum (0.0 to 215.0 mm).
4. `rain_14d_mm`: Rolling 14-day precipitation sum (0.0 to 285.0 mm).
5. `rain_30d_mm`: Rolling 30-day precipitation sum (0.0 to 420.0 mm).
6. `rain_lag1_mm`: Precipitation on day $t-1$ (0.0 to 82.5 mm).
7. `rain_lag2_mm`: Precipitation on day $t-2$ (0.0 to 82.5 mm).
8. `rain_lag3_mm`: Precipitation on day $t-3$ (0.0 to 82.5 mm).

### Static Terrain & Built Environment Features (10)
9. `elev_m`: Mean cell elevation (767.1 m to 951.7 m).
10. `slope_deg`: Mean slope angle (0.0° to 12.3°).
11. `twi`: Topographic Wetness Index $\ln(a / \tan \beta)$ (4.8 to 13.1).
12. `hand_m`: Height Above Nearest Drainage (0.0 m to 58.5 m).
13. `flow_acc`: Contributing upstream drainage catchment area (0.0 to 76.5 km²).
14. `imperv_frac`: Impervious surface land cover fraction (0.0 to 0.99).
15. `dist_lake_m`: Euclidean distance to nearest lake boundary ($\ge 0$ m).
16. `dist_drain_m`: Euclidean distance to nearest primary stormwater channel ($\ge 0$ m).
17. `dist_road_m`: Euclidean distance to nearest major arterial road ($\ge 0$ m).
18. `lakes_within_1km`: Count of distinct lake waterbodies within 1 km radius (0 to 11).

---

## 7. Machine Learning Model & Training
- **Model Type**: Extreme Gradient Boosting Classifier (`xgboost.XGBClassifier`, API v3.4.1).
- **Objective Function**: `binary:logistic`.
- **Class Imbalance Strategy**: `scale_pos_weight = 89.1636429` (derived from ratio of negative to positive cell-days in training events).
- **Holdout Model File**: `handover_member3/flood_xgb_holdout_E2022_09.json` (size: 214 KB).
  - Strictly trained on historical events excluding September 2022 ($E2022\_09$).
  - Training positives available: 52 cell-days.
- **Production Reference Model File**: `handover_member3/flood_xgb.json` (size: 224 KB).
  - Trained across all 6 events (240 positives).

---

## 8. Ranking & Alert Level Protocol
- **Methodology**: Dense daily ranking of uncalibrated model scores:
  $$\text{Daily Rank}(c_i) = \text{DenseRank}\Big(\text{Score}(c_i)\Big), \quad \text{Rank } 1 = \text{Highest Susceptibility}$$
- **Threshold Tiers** (defined in `thresholds.json`):
  - **High Priority (Tier 1)**: Top 150 ranked cells ($\approx 5\%$ of city).
  - **Moderate Priority (Tier 2)**: Ranks 151 to 300 ($\approx 5\%$ of city).
  - **Baseline / None (Tier 3)**: Ranks 301 to 3,026 ($\approx 90\%$ of city).

---

## 9. Empirical Holdout Validation Results (September 2022 Holdout)
- **Validation Dataset**: 24 consecutive days (2022-08-22 to 2022-09-14), 72,624 evaluated cell-days, 188 positive labels.
- **PR-AUC**: **0.0026** vs. random chance baseline **0.0013** (**2.0× lift**).
- **High Tier Hit Rate (Top 150 cells / 5%)**: **8.3%** vs. random chance **5.0%** (**1.66× lift**).
- **Moderate + High Tier Hit Rate (Top 300 cells / 10%)**: **25.0%** vs. random chance **9.9%** (**2.53× lift**).
- **Representative Benchmark Cell**: Cell #722 (Ward 150, Bellandur / Mahadevapura reach), peak score 0.2191 on September 8, 2022 (Rank #1 citywide).

---

## 10. Software Architecture & Implementation
- **Backend Framework**: Python 3.10+, FastAPI 0.128.8, Uvicorn 0.39.0.
- **ML & Data Stack**: XGBoost 2.1.4, Pandas 2.3.3, PyArrow 21.0.0, NumPy 2.0.2.
- **Frontend Framework**: React 18.3.1, Vite 5.4.10, Leaflet 1.9.4, Lucide-React.
- **Mapping Engine**: Leaflet with custom Canvas vector layer rendering all 3,026 cells at 60 FPS.
- **Basemap Tile Provider**: OpenStreetMap Standard Cartographic Tiles (CartoDB / API keys removed).
- **Telegram Demonstration Bot**:
  - Implemented in `backend/services/telegram_service.py`.
  - Whitelist authorization gate (`is_authorized` checking `TELEGRAM_AUTHORIZED_CHAT_IDS`).
  - Supported commands: `/start`, `/help`, `/status`, `/demo [YYYY-MM-DD]`.
  - Outbound dispatch via Telegram Bot API with token-safe error parsing.

---

## 11. Deployment Architecture
- **Frontend**: Deployed on **Vercel** (`n2m-flood-prediction-frontend`, SPA rewrites via `vercel.json`).
- **Backend**: Deployed on **Render** (Web Service, `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`, health check at `/health`).
- **Asset Packaging**: Model files and parquet datasets bundled in `handover_member3/` (~1.9 MB total footprint; ~15–20 MB resident memory, well below Render's 512 MB free tier limit).
- **Outbound Telemetry Integration**: Open-Meteo Weather API integration for experimental real-time context retrieval.

---

## 12. Verification & Test Metrics
- **Automated Backend Test Suite**: Exactly **82 / 82 tests passing** in 1.5s (`pytest tests/test_backend.py tests/test_audit_suite.py tests/test_rainfall_service.py tests/test_telegram_service.py`).
- **Frontend Build**: Zero errors, 751ms build time via `npm run build` (57.10 kB CSS, 377.67 kB JS).
- **Security Audit**: 0 tokens, secrets, or internal paths leaked in frontend build assets or API responses.
