"""
N²M Flood Prediction Model — Chapters 4 to 6
===========================================
"""

CHAPTERS_4_TO_6_MD = r"""# CHAPTER 4 — SYSTEM ARCHITECTURE AND DESIGN

### 4.1 System Overview
The N²M Flood Prediction Model is architected as an end-to-end, decoupled geospatial data science platform designed for high performance, explainability, and accessible cloud delivery. The system architecture coordinates four primary layers:
1. **Offline Geospatial Data & Feature Pipeline**: Ingests multi-source remote sensing raster grids and vector hydrography, executes spatial discretization into 3,026 uniform cells, extracts hydrological terrain indices, links dynamic precipitation grids, and compiles verified Parquet datasets.
2. **Machine Learning & Inference Subsystem**: Houses the extreme gradient-boosted decision tree ensemble (**XGBoost**), class imbalance weighting logic (`scale_pos_weight = 89.16`), and daily dense spatial ranking algorithms.
3. **Asynchronous Backend API Gateway (FastAPI)**: Serves spatial data slices, executes on-the-fly filtering, interfaces with an experimental external meteorological stream (Open-Meteo), and manages secure, token-redacted Telegram bot communication.
4. **Client-Side Cartographic Dashboard (React + Vite)**: Renders the urban spatial mesh using a high-performance Leaflet Canvas engine, orchestrates interactive historical replay across 24 consecutive monsoon dates, and provides intuitive cell inspection drawers and priority tier filters.

Figure 1 illustrates the overall system architecture, mapping data flows from raw satellite and vector inputs to the deployed cloud web client and Telegram demonstration interface.

*(Refer to Figure 1: Overall System Architecture of N²M Flood Prediction Model)*

### 4.2 Overall Architecture
The overall architecture operates on a decoupled client-server paradigm. The machine learning assets and historical replay datasets are stored as immutable, precomputed tabular Parquet files within the backend service repository (`handover_member3/`). This design decision guarantees deterministic reproducibility, sub-millisecond query execution, and an ultra-lightweight memory footprint (~15–20 MB resident RAM) that easily complies with free-tier cloud hosting limits (512 MB RAM).

When a client loads the application in a web browser, the React single-page application initializes its global state, checks backend health via `GET /health`, retrieves the verified date registry via `GET /api/dates`, and requests spatial risk rankings via `GET /api/risk?date=YYYY-MM-DD`. The FastAPI backend processes the request by querying in-memory PyArrow Parquet tables, executes rank-based tier labeling, and transmits a lightweight JSON response containing the 3,026 cell coordinates and priority classifications. The frontend renders these coordinates onto a high-performance HTML5 Canvas layer atop standard OpenStreetMap tiles at 60 frames per second.

### 4.3 Data Pipeline Architecture
The data pipeline transforms disparate global and municipal geospatial datasets into standardized tabular matrices ready for machine learning. The pipeline consists of four sequential stages, as depicted in Figure 2:

*(Refer to Figure 2: Data Ingestion and Feature Processing Pipeline)*

1. **Ingestion & Boundary Clipping**: Ingests administrative ward boundary shapefiles from the Bruhat Bengaluru Mahanagara Palike (198 wards), SRTM 30 m digital elevation rasters, ESA WorldCover 10 m land cover classifications, and OpenStreetMap vector extracts.
2. **Cartesian Grid Discretization**: Partitions the 711.59 km² urban territory into a uniform Cartesian grid of 3,026 cells, each measuring exactly 500 m × 500 m (0.25 km²). Cell centroids (`lat`, `lon`) are calculated, and administrative ward associations are established via spatial intersection.
3. **Topographic & Built Environment Extraction**: Calculates hydrological indices per cell using digital elevation analysis: mean elevation (`elev_m`), terrain gradient (`slope_deg`), Topographic Wetness Index (`twi`), and Height Above Nearest Drainage (`hand_m`). Vector spatial indexing computes Euclidean distances to the nearest lake polygon (`dist_lake_m`), stormwater channel (`dist_drain_m`), and arterial road (`dist_road_m`).
4. **Meteorological Linkage**: Computes a spatial nearest-neighbor index linking each cell centroid to its corresponding 0.05° Climate Hazards Center CHIRPS precipitation pixel (`pixel_id` $\in [0, 36]$), compiling 8 rolling cumulative precipitation sums and antecedent lag matrices.

### 4.4 Machine Learning Model Architecture
The machine learning subsystem relies on an optimized `xgboost.XGBClassifier` architecture. Figure 3 illustrates the model training, temporal holdout sequestering, and out-of-sample evaluation workflow:

*(Refer to Figure 3: XGBoost Training and Out-of-Sample Holdout Workflow)*

- **Holdout Sequestering Protocol**: To ensure an unbiased, scientifically valid evaluation, the primary replay model (`flood_xgb_holdout_E2022_09.json`) was trained exclusively on five historical monsoon events (`E2017_08`, `E2017_09`, `E2021_11`, `E2022_05`, `E2023_05`). The devastating September 2022 monsoon flood event (`E2022_09`, 24 days, 188 positive cell-days) was held out completely during model training and used strictly as an out-of-sample benchmark.
- **Class Imbalance Optimization**: Because confirmed flood days constitute only 0.0136% of the master dataset, the XGBoost split objective is tuned using `scale_pos_weight = 89.16`. This parameter weights positive label errors ~89× heavier during tree gradient calculations, forcing the decision trees to identify sparse topographical flood signatures rather than defaulting to the majority non-flooded class.
- **Feature Importance & Non-Linear Splitting**: The ensemble comprises 100 gradient-boosted decision trees with a maximum depth of 6, allowing the model to capture compound non-linear interactions—such as a cell having low slope, high impervious cover, and high 3-day rainfall simultaneously.

### 4.5 Backend Architecture
The backend is implemented using **FastAPI** (Python 3.10+) running on an asynchronous Uvicorn ASGI server. Figure 5 illustrates the internal backend architecture and its component subsystems:

*(Refer to Figure 5: FastAPI Backend Architecture and Core Subsystems)*

- **`DataLoader` Singleton (`data_loader.py`)**: Manages eager loading, memory caching, and schema validation of all ML assets during application startup (`lifespan` context). Once loaded into memory via PyArrow and Pandas, subsequent HTTP requests incur zero disk I/O latency.
- **`ReplayService` (`replay_service.py`)**: Handles historical simulation slicing. Queries the 72,624-row September 2022 Parquet dataset, extracts daily 3,026-cell vectors, calculates citywide summary statistics, and filters records by priority tier.
- **`RainfallService` (`rainfall_service.py`)**: Interacts with the external Open-Meteo REST API to retrieve real-time observed and forecast precipitation context for Bengaluru. Incorporates a time-to-live (TTL) memory cache (3,600 seconds) and fallback handlers ensuring that external network failures do not disrupt historical replay operations.
- **`TelegramService` (`telegram_service.py`)**: Governs the private demonstration bot. Enforces a strict evaluator chat ID whitelist (`is_authorized`), parses incoming slash commands, formats scientific demonstration bulletins, and dispatches outbound messages via the Telegram Bot API with token-safe error handling.
- **Middleware & CORS Layer**: Configures CORS middleware to dynamically authorize requests from the deployed Vercel frontend origin (`https://*.vercel.app`) as well as local development environments (`localhost:5173`).

### 4.6 API Architecture and Contract Specifications
The backend exposes 14 well-defined REST endpoints categorized by operational domain. Table 4 provides the complete API directory including HTTP methods, URL paths, authentication requirements, and functional descriptions.

**Table 4: Complete REST API Endpoints Directory**

| Endpoint Path | HTTP Method | Request Params / Body | Primary Response Schema | Functional Purpose & Description |
| :--- | :---: | :--- | :--- | :--- |
| **`/`** | `GET` | None | `RootResponse` (JSON) | API health, service status, active mode, and route directory. |
| **`/health`** | `GET` | None | `{"status": "ok", ...}` | Lightweight health probe for cloud load balancers (Render). |
| **`/api/about`** | `GET` | None | `AboutResponse` (JSON) | Model metadata, features, validation stats, and scientific disclaimers. |
| **`/api/dates`** | `GET` | None | `DatesResponse` (JSON) | Chronologically sorted list of 24 available replay dates. |
| **`/api/risk`** | `GET` | `date` (str, req), `level` (opt), `limit` (opt) | `RiskResponse` (JSON) | Spatial susceptibility records for 3,026 cells for target date. |
| **`/api/risk/latest`** | `GET` | `level` (opt), `limit` (opt) | `RiskResponse` (JSON) | Susceptibility records for the latest available replay date. |
| **`/api/summary`** | `GET` | `date` (str, req) | `SummaryResponse` (JSON) | Aggregated statistics, tier counts, mean score, and top cell. |
| **`/api/telegram/status`** | `GET` | None | `TelegramStatus` (JSON) | Public bot configuration status (token redacted). |
| **`/api/telegram/webhook`** | `POST` | Telegram `Update` (JSON) | `WebhookResult` (JSON) | Ingests Telegram updates and executes `/start`, `/help`, `/status`, `/demo`. |
| **`/api/telegram/send-demo`**| `POST` | `TelegramSendDemoRequest` | `SendDemoResponse` (JSON)| Dispatches test demonstration alert to authorized evaluator chat. |
| **`/api/telegram/demo-preview`**|`GET`| `date` (str, opt) | `TelegramPreviewResponse`| Renders formatted demonstration text without dispatching message. |
| **`/api/pipeline/status`** | `GET` | None | `PipelineStatus` (JSON) | Operational and isolation status of rainfall pipeline scaffolding. |
| **`/api/rainfall/latest`** | `GET` | `force_refresh` (bool) | `RainfallLatestResponse` | Normalized daily rainfall series and rolling features from Open-Meteo. |
| **`/api/rainfall/status`** | `GET` | None | `RainfallStatusResponse` | Operational status, provenance, and caching telemetry of rainfall feed. |

### 4.7 Frontend Architecture
The frontend is constructed using **React 18.3.1** and bundled with **Vite 5.4.10**. Figure 6 illustrates the component hierarchy and data flow:

*(Refer to Figure 6: Frontend Component Architecture and Visualization Engine)*

- **Top-Level Orchestrator (`App.jsx`)**: Manages active tab routing (`Home`, `FloodMap`, `LiveSimulation`, `Telegram`, `Credits`), global state synchronization (active replay date, selected grid cell, API connectivity status), and persistent navigation headers and editorial footers.
- **Central API Client (`frontend/src/api/client.js`)**: Encapsulates all asynchronous `fetch` operations to the backend API, automatically normalizing the base URL (`VITE_API_BASE_URL`), stripping trailing slashes, and handling network timeouts and error boundaries.
- **Content Configuration Registry (`content.js`)**: Centralizes all editorial copy, institutional credentials, project advisor designations, team member biographies, and academic disclaimers into a single, clean configuration file.

### 4.8 Spatial Visualization Engine
Visualizing 3,026 interactive spatial cells simultaneously in a web browser poses severe performance challenges for standard SVG or DOM-based mapping layers (which create 3,026 distinct DOM nodes, leading to severe frame dropping and unresponsive scrubbing). 

To resolve this, the N²M frontend implements a **custom Leaflet Canvas vector rendering layer** (`FloodMapPage.jsx`):
- All 3,026 cell centroids are projected onto a single HTML5 `<canvas>` element managed by Leaflet.
- Points are colored dynamically according to their daily priority tier: **High Priority** in deep red (`#dc2626`), **Moderate Priority** in vivid amber (`#ea580c`), and **Baseline Risk** in subdued translucent slate (`#94a3b8`).
- When an active date changes during replay, the Canvas layer clears and redraws all 3,026 points in a single requestAnimationFrame batch, sustaining a smooth **60 frames per second** even during rapid automated date sequencing.
- Clicking any point executes an optimized spatial distance calculation to resolve the target cell ID, opening the floating **Telemetry Inspector Drawer** displaying the cell's physical attributes and relative rank.

### 4.9 Historical Replay Architecture
The historical replay subsystem allows researchers to step forward, backward, or automatically loop through the 24 consecutive dates of the benchmark September 2022 monsoon sequence (2022-08-22 to 2022-09-14). Figure 7 details the replay sequence and spatial updating logic:

*(Refer to Figure 7: Historical Replay Sequence and Daily Spatial Updating)*

- An automated replay timer steps through dates at 1,800 ms intervals, updating map marker colors and dashboard summary metrics in lockstep.
- Users can pause the playback, step day-by-day, jump to specific milestone storm dates via a dropdown, or filter the map display to show only the Top 150 High Priority cells.

### 4.10 Telegram Integration Architecture
To demonstrate automated alert dissemination to emergency evaluators, the platform integrates a private Telegram demonstration bot (`@N2M_Flood_Bot`). Figure 8 illustrates the complete interaction sequence:

*(Refer to Figure 8: Telegram Demonstration Dispatch Sequence Diagram)*

- **Server-Side Security**: The bot token is maintained strictly in server-side environment variables (`TELEGRAM_BOT_TOKEN`) and is never exposed in client bundles or API payloads.
- **Whitelist Authorization Gate**: Outbound message delivery is strictly restricted to authorized evaluator chat IDs configured in `TELEGRAM_AUTHORIZED_CHAT_IDS`. Inbound commands from unauthorized users receive a polite access-restricted notice.
- **Demonstration Bulletin Generation**: Bulletins format the active date, tier breakdown, citywide average score, and top 5 vulnerable cells, embedded within mandatory academic disclaimers.

### 4.11 Cloud Deployment Architecture
The platform is deployed using modern, decoupled free-tier cloud infrastructure, as illustrated in Figure 9:

*(Refer to Figure 9: Cloud Deployment Architecture on Vercel and Render)*

- **Frontend on Vercel**: Hosted as a static React SPA on Vercel's Edge CDN. Single Page Application routing is guaranteed via [frontend/vercel.json](file:///Users/nishanthgm/Documents/n2m-rain-predictive-model/frontend/vercel.json) rewrites (`/(.*)` $\rightarrow$ `/index.html`). Total compressed asset footprint is ~120 kB gzip.
- **Backend on Render**: Hosted as a Python 3 Web Service on Render, started via `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. The backend preloads the lightweight ML assets (`handover_member3/`, ~1.9 MB total size) on startup, consuming ~15–20 MB resident RAM (less than 4% of Render's 512 MB free-tier allowance). Health monitoring is wired to `/health`.

Figure 10 summarizes the complete end-user interaction and navigation flowchart through the system.

*(Refer to Figure 10: User Interaction and Research Navigation Flowchart)*

---

# CHAPTER 5 — DATA AND METHODOLOGY

### 5.1 Dataset Description and Provenance
The N²M project relies on high-resolution open geospatial rasters, vector infrastructure datasets, and historical hydrometeorological observations. Table 5 details the source datasets, providers, native resolutions, and specific roles within the project.

**Table 5: Primary Geospatial and Hydrometeorological Datasets**

| Dataset Identifier | Providing Organization | Native Spatial / Temporal Resolution | Spatial Coverage | Project Function & Role |
| :--- | :--- | :--- | :--- | :--- |
| **CHIRPS Daily Rainfall** | Climate Hazards Center, UC Santa Barbara | 0.05° (~5.3 km) / Daily | Quasi-Global (50°S–50°N) | Dynamic antecedent rainfall, rolling sums, and lag matrices. |
| **SRTM 1 Arc-Second DEM**| NASA / USGS | 1 Arc-Second (~30 m) / Static | Near-Global (60°N–56°S) | Digital elevation model, terrain slope, TWI, and flow accumulation. |
| **Copernicus GLO-30 DEM**| European Space Agency (ESA) | 30 m / Static | Global | Elevation validation and drainage basin delineation. |
| **ESA WorldCover 10m** | European Space Agency (ESA) | 10 m / Annual (2020/2021) | Global | Impervious surface land cover fraction (`imperv_frac`). |
| **OpenStreetMap Vectors** | OpenStreetMap Contributors | Vector (Polygons & Lines) | Greater Bengaluru | Lakes (*keres*), stormwater channels (*rajakaluves*), roads. |
| **Flood Situation Reports**| BBMP & KSNDMC Bulletins | Point Locations / Event-Based | BBMP Administrative Wards | Verified ground-truth flood occurrence points and seed cells. |

### 5.2 Spatial Representation and Grid Discretization
To establish a continuous and uniform spatial analysis framework, Greater Bengaluru was discretized into a regular Cartesian grid:
- **Mesh Boundary**: Defined by the official Bruhat Bengaluru Mahanagara Palike administrative delimitation spanning all 198 municipal wards.
- **Cell Dimensions**: Exactly 500 m × 500 m (0.25 km² per nominal interior cell).
- **Cell Inventory**: Total of **3,026 discrete grid cells** covering 711.59 km². Of these, 2,674 represent full interior cells and 352 represent clipped peripheral boundary cells.
- **Spatial Linkage Table (`cell_pixel_map.csv`)**: Because CHIRPS satellite rainfall is provided on a 0.05° grid (~5.3 km resolution, resulting in 37 distinct pixels across Bengaluru), an audited spatial mapping table links each 500 m cell centroid (`lat`, `lon`) to its parent CHIRPS `pixel_id` (mean 81.8 cells per rain pixel).

### 5.3 Input Features and Hydrological Significance
The machine learning model ingests exactly **18 features** defined in `features.json`. Table 6 specifies each feature name, physical units, data types, empirical ranges across the Bengaluru grid, and hydrological significance.

**Table 6: Complete Feature Set (18 Input Variables)**

| Feature Name | Category | Unit | Data Type | Empirical Range | Hydrological & Terrain Significance |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **`rain_1d_mm`** | Dynamic | mm | `float64` | 0.0 – 82.5 | Cumulative 24-hour rainfall on observation day $d$. Captures immediate storm volume. |
| **`rain_3d_mm`** | Dynamic | mm | `float64` | 0.0 – 145.0 | Rolling 3-day sum: $\sum_{t=0}^2 \text{rain}(d-t)$. Measures short-term stormwater accumulation. |
| **`rain_7d_mm`** | Dynamic | mm | `float64` | 0.0 – 215.0 | Rolling 7-day cumulative rainfall. Measures topsoil saturation and waterbody rise. |
| **`rain_14d_mm`** | Dynamic | mm | `float64` | 0.0 – 285.0 | Rolling 14-day cumulative rainfall. Captures subsoil moisture and lake cascade exhaustion. |
| **`rain_30d_mm`** | Dynamic | mm | `float64` | 0.0 – 420.0 | Rolling 30-day cumulative rainfall. Seasonal antecedent saturation index. |
| **`rain_lag1_mm`** | Dynamic | mm | `float64` | 0.0 – 82.5 | Rainfall on day $d-1$. Captures immediate recession tail and delayed runoff. |
| **`rain_lag2_mm`** | Dynamic | mm | `float64` | 0.0 – 82.5 | Rainfall on day $d-2$. |
| **`rain_lag3_mm`** | Dynamic | mm | `float64` | 0.0 – 82.5 | Rainfall on day $d-3$. |
| **`elev_m`** | Static | m | `float64` | 767.1 – 951.7 | Mean elevation above sea level. Bengaluru slopes downward toward the SE and SW. |
| **`slope_deg`** | Static | deg | `float64` | 0.0 – 12.3 | Terrain gradient. Flat low-slope areas ($\le 1.5^\circ$) severely impede overland drainage. |
| **`twi`** | Static | index | `float64` | 4.8 – 13.1 | Topographic Wetness Index: $\ln(a / \tan \beta)$. High values denote natural ponding hollows. |
| **`hand_m`** | Static | m | `float64` | 0.0 – 58.5 | Height Above Nearest Drainage. Vertical elevation relative to channel. Low HAND = floodplain. |
| **`flow_acc`** | Static | km² | `float64` | 0.0 – 76.5 | Contributing upstream catchment area draining through the cell centroid. |
| **`imperv_frac`** | Static | [0, 1] | `float64` | 0.0 – 0.99 | Impervious land cover fraction. High built-up cover blocks rainwater infiltration. |
| **`dist_lake_m`** | Static | m | `float64` | $\ge 0.0$ | Euclidean distance to nearest lake boundary. Lake margins frequently backflow during floods. |
| **`dist_drain_m`** | Static | m | `float64` | $\ge 0.0$ | Euclidean distance to nearest primary stormwater drain (*rajakaluve*). |
| **`dist_road_m`** | Static | m | `float64` | $\ge 0.0$ | Distance to nearest major arterial road. Roads often act as artificial dams or flood channels. |
| **`lakes_within_1km`** | Static | count | `int64` | 0 – 11 | Number of distinct lakes within 1 km radius. Denotes density of the cascade chain. |

### 5.4 Data Preprocessing and Alignment
Data preprocessing enforced strict spatial alignment and zero-missing-value guarantees across the entire spatial skeleton:
1. **DEM Hydrology Processing**: SRTM elevation tiles were pit-filled to eliminate spurious sinks. Flow directions were derived using the D8 single-direction flow algorithm, from which upstream contributing area ($a$) and Topographic Wetness Index ($\text{TWI} = \ln(a / \tan \beta)$) were calculated. Height Above Nearest Drainage (HAND) was normalized against the OpenStreetMap vector hydrographic network.
2. **Impervious Surface Aggregation**: High-resolution 10 m ESA WorldCover pixels were aggregated to the 500 m grid, calculating the proportion of built-up/paved surface cover per cell.
3. **Data Integrity Auditing**: The compiled static dataset (`cells_static.csv`, 3,026 rows) contains exactly 0.0% missing values across all 10 features, verified by automated hash-guard validation tests (`test_backend.py`).

### 5.5 Feature Engineering
Dynamic rainfall feature engineering was executed by aggregating daily CHIRPS observations into cumulative multi-scale saturation windows:
- Rolling multi-day precipitation sums were computed over 3, 7, 14, and 30 calendar days to capture cascading soil saturation phases:
  $$\text{rain\\_kd}(d) = \sum_{t=0}^{k-1} \text{rain}(d - t)$$
- Antecedent daily lag values (`rain_lag1`, `rain_lag2`, `rain_lag3`) were isolated to provide the tree models with explicit gradient indicators of whether a storm was accelerating or receding.

### 5.6 Model Selection Rationale
The selection of **XGBoost (Extreme Gradient Boosting)** was governed by both empirical characteristics of urban flood data and established literature benchmarks [1], [2]:
1. **Handling Severe Multicollinearity**: Topographic indicators (such as elevation, HAND, and TWI) exhibit strong non-linear collinearity. Tree-based partitioning naturally accommodates correlated features without requiring dimensionality reduction (e.g. PCA) that would obscure physical interpretability.
2. **Extreme Class Imbalance Support**: XGBoost natively supports the `scale_pos_weight` parameter, adjusting the gradient and hessian calculations during tree split evaluations to prioritize sparse positive classes.
3. **Sub-Millisecond Inference Speed**: Precompiled decision trees in JSON format (`flood_xgb_holdout_E2022_09.json`) execute inference over 3,026 cell vectors in under 15 milliseconds, enabling real-time interactive web dashboard scrubbing.

### 5.7 Model Training Methodology
- **Training Matrix (`flood_dataset.parquet`)**: Comprises 1,764,158 cell-day records spanning 583 candidate stormy days across May–November in 2017, 2021, 2022, and 2023.
- **Candidate Stormy Day Rule**: Days are selected where the maximum 3-day rainfall across Bengaluru reaches at least 10 mm, plus all calendar days from 14 days before to 7 days after each confirmed flood event.
- **Historical Ground-Truth Events**: Exactly 6 documented historical flood events were geocoded and linked to 10 distinct seed cells. Because inundation extends over contiguous urban blocks, a $3 \times 3$ topological grid buffer (seed cell + 8 contiguous neighbors) expanded the 30 seed positives into **240 total positive cell-days** (overall positive prevalence: 0.0136%).

Table 7 details the historical event inventory, active dates, seed cells, and positive label allocations.

**Table 7: Historical Flood Events and Positive Label Breakdown**

| Event Identifier | Calendar Period | Active Days | Confirmed Flood Locations / Seed Cells | Seed Positives | Buffer Positives | Total Positives |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **`E2017_08`** | Aug 14–15, 2017 | 1 | Koramangala 4th Block (Cell 897) | 1 | 8 | 9 |
| **`E2017_09`** | Sep 7–8, 2017 | 2 | Bilekahalli / HSR Layout (Cells 774, 490) | 2 | 16 | 18 |
| **`E2021_11`** | Nov 20–22, 2021 | 1 | Kendriya Vihar, Yelahanka (Cell 2882) | 1 | 8 | 9 |
| **`E2022_05`** | May 17–19, 2022 | 1 | RBD Layout, Sarjapur Road (Cell 555) | 1 | 6 | 7 |
| **`E2022_09` (Holdout)**| Aug 22–Sep 14, 2022| 24 | Ecospace, Rainbow Drive, ORR (Cells 666, 847, 910, 977, 1444) | 24 | 164 | 188 |
| **`E2023_05`** | May 21–22, 2023 | 1 | KR Circle Underpass (Cell 1478) | 1 | 8 | 9 |
| **TOTAL** | — | **30** | **10 Distinct Seed Cells** | **30** | **210** | **240** |

Table 8 summarizes the operational hyperparameters applied during XGBoost model fitting.

**Table 8: XGBoost Hyperparameter Configuration**

| Hyperparameter | Parameter Value | Engineering Justification & Function |
| :--- | :---: | :--- |
| **Objective** | `binary:logistic` | Standard logistic loss objective for binary classification probability estimation. |
| **`scale_pos_weight`**| `89.1636429` | Weights sparse positive errors ~89× heavier based on negative-to-positive ratio in training split. |
| **`n_estimators`** | `100` | Number of gradient-boosted decision trees in the ensemble. |
| **`max_depth`** | `6` | Maximum tree depth, allowing up to 64 terminal leaf interactions without severe overfitting. |
| **`learning_rate`** | `0.1` | Step-size shrinkage factor preventing gradient divergence. |
| **`eval_metric`** | `logloss` | Evaluation metric monitored during split optimization. |
| **Input Features** | `18` | Strictly matching feature definitions in `features.json`. |

### 5.8 Inference and Spatial Ranking Formulation
In standard machine learning classification, predicted probabilities are thresholded at $P \ge 0.5$. However, when class imbalance is severe ($0.0136\%$), model probabilities mathematically compress into a narrow lower bound (rarely exceeding 0.25). An absolute threshold of 0.5 produces zero positive predictions, while an arbitrary threshold of 0.1 fluctuates uncontrollably between wet and dry days.

To solve this, the N²M framework formulates inference through **daily relative dense ranking**:
$$\text{Score}(c_i) = P\Big(\text{Flood} = 1 \mid \mathbf{x}_i, \mathbf{w}_{\text{XGB}}\Big)$$
$$\text{Rank}(c_i) = \text{DenseRank}\Big(\text{Score}(c_i)\Big), \quad \text{Rank } 1 = \max_{j} \Big(\text{Score}(c_j)\Big)$$

Figure 4 illustrates this inference and ranking workflow:

*(Refer to Figure 4: Daily Inference and Susceptibility Ranking Logic)*

### 5.9 Daily Risk Classification Protocol
Cells are assigned to priority tiers based strictly on their daily rank order. Table 9 defines the operational classification rules.

**Table 9: Daily Susceptibility Tier Thresholds**

| Susceptibility Priority Tier | Daily Rank Order Criterion | Nominal Cell Allocation | Approximate Urban Area Coverage | Operational Rationale & Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **High Priority (Tier 1)** | $\text{Rank} \in [1, 150]$ | Exactly 150 Cells | ~5.0% (~35.6 km²) | Highest physical susceptibility. Primary focus for emergency pump mobilization. |
| **Moderate Priority (Tier 2)**| $\text{Rank} \in [151, 300]$ | Exactly 150 Cells | ~5.0% (~35.6 km²) | Secondary susceptibility buffer. Monitored for potential spillover and ponding. |
| **Baseline Risk (Tier 3)** | $\text{Rank} \in [301, 3026]$ | Exactly 2,726 Cells | ~90.0% (~640.4 km²) | Nominal baseline urban risk under current meteorological conditions. |

### 5.10 Historical Simulation Framework
The historical simulation framework leverages the partitioned matrix `flood_replay_E2022_09.parquet` (72,624 rows = 3,026 cells × 24 calendar days from August 22 to September 14, 2022). For each replay date, the backend extracts the 3,026-cell slice, evaluates cell ranks, and compiles summary metrics (High count, Moderate count, Baseline count, citywide mean score, and top-ranked cell telemetry).

### 5.11 Evaluation Methodology and Metrics
- **Strict Out-of-Sample Holdout**: The evaluation model (`flood_xgb_holdout_E2022_09.json`) was strictly sequestered from the September 2022 event, providing a rigorous test of model generalization.
- **Precision-Recall AUC (PR-AUC)**: In severe class imbalance regimes, ROC-AUC can be misleadingly high (often >0.90) because the massive true negative rate dominates the denominator. PR-AUC evaluates precision against recall, where the random chance baseline equals positive prevalence ($P_{\text{base}} = 188 / 72,624 = 0.0013$).
- **Spatial Tier Hit Rate & Lift**:
  $$\text{Hit Rate}(\text{Tier}) = \frac{\text{Positives Captured in Tier}}{\text{Total Historical Positives in Event}}$$
  $$\text{Lift}(\text{Tier}) = \frac{\text{Hit Rate}(\text{Tier})}{\text{Random Spatial Expectation of Tier}}$$

Table 10 presents the empirical holdout validation results achieved on the September 2022 holdout benchmark.

**Table 10: Empirical Holdout Evaluation Metrics (September 2022 Holdout)**

| Evaluation Metric | Holdout Model Value | Random Chance Baseline | Empirical Lift / Enrichment Factor |
| :--- | :---: | :---: | :---: |
| **PR-AUC (Precision-Recall Area Under Curve)** | **0.0026** | **0.0013** | **2.0× Lift** |
| **High Tier Hit Rate (Top 150 Cells / Top 5%)** | **8.3%** | 5.0% | **1.66× Lift** |
| **Moderate + High Tier Hit Rate (Top 300 Cells / Top 10%)** | **25.0%** | 9.9% | **2.53× Lift** |

### 5.12 Methodological Limitations
1. **Severe Ground-Truth Sparsity**: With only ~10 verified seed flood locations across 6 historical events, the model's positive training signals are sparse.
2. **Coarse Precipitation Grids**: CHIRPS 0.05° (~5.3 km) pixels cannot resolve hyper-localized convective cloudbursts dropping 80 mm in 45 minutes over isolated street underpasses.
3. **Diagnostic Nowcasting Horizon**: The replay evaluates realized same-day rainfall concurrent with flooding. True 24-hour predictive forecasting requires numerical weather prediction quantitative precipitation forecasts (NWP QPF).

---

# CHAPTER 6 — PROJECT IMPLEMENTATION

### 6.1 Development Environment and Tooling
The N²M project was constructed using modern, open-source software engineering libraries. Table 11 details the development environment, versions, and functions.

**Table 11: Software Dependencies and Development Environment**

| Technology / Library | Version | Operational Function & Role in Architecture |
| :--- | :---: | :--- |
| **Python** | `3.10.12` / `3.9.6` | Core backend programming language runtime. |
| **FastAPI** | `0.128.8` | High-performance asynchronous REST API framework. |
| **Uvicorn** | `0.39.0` | Asynchronous Server Gateway Interface (ASGI) web server. |
| **XGBoost** | `2.1.4` (API `3.4.1`)| Gradient boosted decision tree ML inference engine. |
| **Pandas** | `2.3.3` | In-memory tabular data manipulation and slice extraction. |
| **PyArrow** | `21.0.0` | High-performance columnar Parquet deserialization. |
| **Pydantic** | `2.13.5` | Strict data validation and OpenAPI schema serialization. |
| **Node.js / npm** | `20.x` / `10.x` | Frontend JavaScript build runtime. |
| **React** | `18.3.1` | Declarative component UI library. |
| **Vite** | `5.4.10` | Next-generation frontend build tool and dev server. |
| **Leaflet** | `1.9.4` | Open-source mobile-friendly interactive mapping library. |
| **Lucide-React** | `0.453.0` | Cartographic and UI vector iconography. |
| **Pytest** | `8.4.2` | Automated backend testing framework (82 passing tests). |

### 6.2 Data Pipeline Implementation
The offline pipeline is implemented in modular Python scripts located in `pipeline/`:
- `pipeline/01_grid.py`: Discretizes the 198 BBMP wards into 3,026 cells, computing spatial bounding boxes and centroid coordinates.
- `pipeline/02_features.py`: Computes static terrain features (elevation, slope, TWI, HAND) and extracts Euclidean hydrographic distances via `shapely` and `geopandas`.
- `pipeline/03_rainfall.py`: Downloads CHIRPS daily precipitation NetCDF files, maps grid cells to the 37 native rain pixels, and computes multi-day rolling sums and antecedent lags.
- `pipeline/04_dataset.py`: Merges static and dynamic features with historical event labels, compiling `data/flood_dataset.parquet`.

### 6.3 Machine Learning Model Implementation
Model loading and inference are encapsulated in `handover_member3/score_cells.py`:
```python
def load(model_path="flood_xgb.json", features_path="features.json", rule_path="thresholds.json"):
    feats = json.load(open(features_path))
    rule = json.load(open(rule_path))
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    return model, feats, rule

def score_day(df, model, feats, rule, n_ref=3026):
    missing = [f for f in feats if f not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    out = df[["cell_id", "ward", "lat", "lon"]].copy()
    out["score"] = model.predict_proba(df[feats])[:, 1]
    out["rank"] = out["score"].rank(ascending=False, method="first").astype(int)
    high_k = rule["high_top_k"]      # 150
    mod_k = rule["moderate_top_k"]   # 300
    out["level"] = "None"
    out.loc[out["rank"] <= mod_k, "level"] = "Moderate"
    out.loc[out["rank"] <= high_k, "level"] = "High"
    return out.sort_values("rank")
```

### 6.4 Backend Implementation
The backend API is orchestrated in `backend/main.py`:
- Eagerly initializes `DataLoader`, caching static cell definitions and Parquet datasets in memory during application startup (`lifespan`).
- Implements comprehensive route handlers for spatial queries (`/api/risk`), historical date listings (`/api/dates`), summary statistics (`/api/summary`), and Telegram dispatch (`/api/telegram/send-demo`).
- Configures dynamic CORS middleware supporting both local development hosts and deployed Vercel subdomains via regular expression:
  ```python
  allow_origin_regex = r"^https:\/\/.*\.vercel\.app$"
  ```

### 6.5 Frontend Implementation
The frontend application is structured into decoupled components:
- `FloodMapPage.jsx`: Hosts the Leaflet map and the custom Canvas vector rendering layer.
- `LiveSimulationPage.jsx`: Renders the meteorological context panel, displaying Open-Meteo precipitation metrics and rolling sums.
- `TelegramPage.jsx`: Provides the private Telegram demonstration console, displaying bot status, command references, and the dispatch trigger button.
- `content.js`: Centralizes institutional credentials and team disclosures.

### 6.6 API Integration and Client Service
Frontend HTTP communication is centralized in `frontend/src/api/client.js`. All API calls pass through an asynchronous `fetchJson` wrapper that automatically prepends `VITE_API_BASE_URL`, strips trailing slashes, attaches JSON headers, and raises descriptive errors when non-200 responses occur.

### 6.7 Historical Replay Implementation
Replay sequencing in `FloodMapPage.jsx` uses an active date pointer state (`activeDate`) synchronized with a dropdown selector and playback stepper. When playback is engaged, an interval timer updates `activeDate` every 1,800 ms, triggering cached API queries and redrawing the 3,026 Canvas dots smoothly.

### 6.8 Telegram Demonstration Bot Implementation
The bot service (`backend/services/telegram_service.py`) manages communication with the Telegram Bot API:
- **Sanitized Credentials**: `clean_bot_token` strips whitespace, quotes, and redundant `bot` prefixes.
- **Whitelist Enforcement**: Incoming updates or demo dispatch requests check `is_authorized(chat_id)` against `TELEGRAM_AUTHORIZED_CHAT_IDS`.
- **Command Dispatcher**: Implements `/start`, `/help`, `/status`, and `/demo [YYYY-MM-DD]` commands.
- **Descriptive Error Handling**: Parses Telegram API error responses (e.g., HTTP 400 `chat not found`), returning actionable guidance instructing users to initiate conversation with the bot by tapping "Start".

### 6.9 Cloud Deployment Implementation
- **Frontend (Vercel)**: Configured via [frontend/vercel.json](file:///Users/nishanthgm/Documents/n2m-rain-predictive-model/frontend/vercel.json) with SPA rewrites (`/(.*)` $\rightarrow$ `/index.html`). Built using `npm run build` with `VITE_API_BASE_URL` pointing to the deployed Render backend.
- **Backend (Render)**: Configured via [render.yaml](file:///Users/nishanthgm/Documents/n2m-rain-predictive-model/render.yaml) as a Python 3 Web Service. Uvicorn starts with `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. Health monitoring is tied to `/health`.

### 6.10 Security, Privacy, and Credential Isolation
1. **Zero Secret Leakage**: The Telegram bot token is stored strictly in server-side environment variables (`TELEGRAM_BOT_TOKEN`) and is never committed to Git (`.gitignore` protects `.env`).
2. **Status Endpoint Masking**: `GET /api/telegram/status` returns boolean configuration flags (`token_configured: true`), completely redacting the secret token.
3. **Whitelist Restrictions**: The bot cannot be utilized to broadcast operational alarms; messages are confined to whitelisted research participants.
"""
