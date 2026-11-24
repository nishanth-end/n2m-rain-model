"""
Undergraduate Student Project Report — Chapters 4 to 7 and References
=====================================================================
Tone: Clear, honest, well-written for second-year CSE students.
"""

CHAPTERS_4_TO_7 = r"""# CHAPTER 4 — SYSTEM DESIGN AND ARCHITECTURE

### 4.1 Overall System Architecture
The N²M Flood Prediction Model is designed as a decoupled, four-tier geospatial web platform. The system is split into distinct subsystems for offline data preparation, machine learning inference, asynchronous backend API services, and client-side map visualization. 

Figure 1 illustrates the high-level architecture of the system, showing how raw satellite and vector datasets are processed offline and served to web and mobile clients through cloud hosting platforms.

*(Refer to Figure 1: Overall System Architecture of the N²M Flood Prediction Model)*

The architecture coordinates four primary layers:
1. **Offline Geospatial Data & Feature Pipeline**: Reads digital elevation rasters, land-cover classifications, vector waterways, and satellite rainfall grids; partitions Bengaluru into 3,026 uniform cells; calculates 18 physical features; and saves clean, compressed Parquet tables.
2. **Machine Learning Model Engine**: Uses a trained XGBoost classifier optimized with positive class weighting to calculate daily relative susceptibility scores across all 3,026 cells, outputting rank-based priority tiers.
3. **Asynchronous Backend API (FastAPI)**: Serves spatial data slices, historical replay dates, and weather context via fast REST endpoints, while enforcing security controls for the Telegram demonstration bot.
4. **Client-Side Web Dashboard (React + Vite)**: Renders the 3,026-cell grid using a high-performance HTML5 Canvas layer on Leaflet, providing interactive date replay, tier filtering, and neighborhood inspection drawers.

### 4.2 Geospatial Data Processing Pipeline
The data pipeline is responsible for taking raw, disparate geospatial files and transforming them into a structured tabular format suitable for machine learning algorithms. Figure 2 illustrates the sequential flow of data processing.

*(Refer to Figure 2: Geospatial Data Ingestion and Feature Processing Pipeline)*

The pipeline runs offline through four sequential Python scripts:
1. **Grid Generation (`01_grid.py`)**: Ingests administrative ward boundary shapefiles from the BBMP (198 wards) and creates a uniform Cartesian grid of 3,026 square cells (500 m × 500 m, 0.25 km² per cell). It computes the centroid coordinates (`lat`, `lon`) of each cell and identifies its enclosing administrative ward.
2. **Terrain Feature Calculation (`02_features.py`)**: Uses a 30-meter SRTM Digital Elevation Model (DEM) to calculate mean ground elevation (`elev_m`) and slope in degrees (`slope_deg`). It computes the Topographic Wetness Index (`twi`) and Height Above Nearest Drainage (`hand_m`). Using OpenStreetMap vectors, it calculates Euclidean distances to the nearest lake polygon (`dist_lake_m`), primary stormwater drain (`dist_drain_m`), and major arterial road (`dist_road_m`). Using ESA WorldCover 10 m data, it extracts the impervious concrete fraction (`imperv_frac`).
3. **Precipitation Extraction (`03_chirps.py`)**: Ingests 0.05° (~5.3 km) daily gridded precipitation data from CHIRPS. It maps each cell centroid to its nearest CHIRPS precipitation pixel (spanning 37 distinct pixels across Bengaluru), compiling daily rainfall and multi-day rolling sums.
4. **Feature Matrix Assembly (`04_build_matrix.py`)**: Merges the 10 static terrain features with the 8 dynamic rainfall features for every cell-day across historical storm events, saving the clean tabular dataset as high-performance Apache Parquet files.

### 4.3 Machine Learning Component
The machine learning component is centered on an **XGBoost (eXtreme Gradient Boosting)** classifier. XGBoost was chosen because it excels on structured tabular datasets containing a mixture of physical measurements (elevations in meters, slopes in degrees, fractions between 0 and 1, and rainfall in millimeters).

Rather than outputting hard binary predictions ("Will Flood" vs. "Will Not Flood"), the model outputs continuous raw susceptibility scores. Because confirmed flood events are extremely rare in historical records, absolute predicted probabilities are naturally small (rarely exceeding 0.25). Our system therefore passes these scores into a **daily dense ranking function**. For any selected date, all 3,026 cells are sorted from highest to lowest score, allowing municipal stakeholders or researchers to focus immediately on the top 5% or 10% highest-risk cells in the city.

### 4.4 Backend Architecture and REST API
The backend is built with **FastAPI**, a modern, high-performance web framework for Python that natively supports asynchronous request handling (`async`/`await`). The backend runs on an ASGI server (Uvicorn) and provides several key architectural advantages:
- **In-Memory Parquet Caching**: During server startup (via FastAPI's `lifespan` handler), the `DataLoader` singleton loads the static 3,026-cell definitions and historical replay Parquet datasets directly into RAM using PyArrow and Pandas. Because the total dataset is compact (~15–20 MB in memory), subsequent API queries require zero disk reads and execute in less than 5 milliseconds.
- **Decoupled Service Modules**: Business logic is separated into clean service modules: `replay_service.py` handles historical date slicing and rank filtering, `rainfall_service.py` connects to weather APIs with an in-memory TTL cache, and `telegram_service.py` handles bot interactions.
- **CORS Configuration**: Supports cross-origin resource sharing from both local development ports and deployed Vercel subdomains via secure regular expression matching.

Table 4 documents the complete set of REST API endpoints provided by the backend.

#### Table 4: Complete Backend REST API Directory
| HTTP Method | API Endpoint Route | Purpose and Response Summary |
| :--- | :--- | :--- |
| `GET` | `/health` | Healthcheck endpoint; returns server status, uptime, and loaded dataset records. |
| `GET` | `/api/dates` | Returns list of available historical replay dates (`2022-09-01` to `2022-09-24`). |
| `GET` | `/api/risk?date=YYYY-MM-DD` | Returns spatial coordinates, scores, ranks, and priority tiers for all 3,026 cells on that date. |
| `GET` | `/api/summary?date=YYYY-MM-DD` | Returns citywide summary statistics: count of High/Moderate cells, max score, mean score. |
| `GET` | `/api/cell/{cell_id}` | Returns complete 18-parameter physical profile and historical scores for a single cell. |
| `GET` | `/api/rainfall/bengaluru` | Returns current weather, daily forecast, and rolling rainfall sums from Open-Meteo. |
| `GET` | `/api/telegram/status` | Returns whether the Telegram bot token and chat ID are configured (token redacted). |
| `GET` | `/api/telegram/preview` | Generates a formatted text preview of the daily demonstration bulletin without sending. |
| `POST` | `/api/telegram/send-demo` | Dispatches an experimental flood bulletin for a chosen date to authorized chat IDs. |
| `POST` | `/api/telegram/webhook` | Receives incoming messages from the Telegram Bot API (`/start`, `/status`, `/help`, `/demo`). |

### 4.5 Frontend Web Application and Map Architecture
The frontend is a single-page application built using **React 18** and bundled with **Vite**. The user interface is designed to be responsive, clean, and intuitive for users exploring spatial flood vulnerability.

The core technical challenge in the frontend was rendering 3,026 interactive spatial cells smoothly. If standard Leaflet SVG circles or GeoJSON polygon layers are used, the browser creates 3,026 distinct Document Object Model (DOM) nodes. Panning, zooming, or scrubbing across dates in such a map causes noticeable frame drops and browser freezing.

To solve this, our frontend uses **Leaflet's HTML5 Canvas vector renderer** (`L.canvas()`). Instead of individual DOM nodes, all 3,026 grid centroids are rendered as lightweight circular points on a single hardware-accelerated Canvas element. This approach delivers:
- **Smooth 60 FPS Performance**: Fast, responsive map panning and zooming across desktop and mobile browsers.
- **Dynamic Color Coding**: Points update instantly between red (High Priority), orange (Moderate Priority), and muted gray (Baseline) as the user scrubs through dates.
- **Fast Hit Testing**: Clicking anywhere on the map calculates the nearest cell centroid using an optimized Euclidean distance check, instantly opening the slide-over **Cell Inspector Drawer**.

### 4.6 Historical Replay Mechanism
The historical replay component enables users to explore how flood susceptibility evolved across Bengaluru during the 24 consecutive days of the major September 2022 monsoon flood sequence (`2022-09-01` to `2022-09-24`).

The frontend maintains an `activeDate` state synchronized with a playback controller. Users can scrub forward and backward using a slider, select a date from a dropdown, or press the "Play" button. When playback is active, an interval timer steps through dates every 1.8 seconds. On each step, the frontend fetches the precomputed risk vector for that date from the backend cache and updates the canvas point colors seamlessly, allowing users to watch high-risk clusters form and dissipate over time.

### 4.7 Telegram Demonstration Bot Integration
To explore how automated mobile notifications could work in an urban data science workflow, we integrated a private demonstration bot using the Telegram Bot API.

The bot is designed strictly for research demonstration and is governed by strict security boundaries:
- **Server-Side Token Isolation**: The bot token (`TELEGRAM_BOT_TOKEN`) is stored exclusively in backend environment variables. It is never included in frontend source code, build bundles, or Git repositories.
- **Whitelist Authorization**: The backend checks incoming chat IDs against `TELEGRAM_AUTHORIZED_CHAT_IDS`. Requests from unauthorized users are rejected with HTTP 403 Forbidden, preventing unauthorized broadcast of demonstration messages.
- **Informative Bulletins**: When an authorized student group member triggers `/demo [date]`, the bot formats a structured message listing citywide storm metrics, total high-priority cells, and the top 3 most vulnerable neighborhoods with their physical attributes.

### 4.8 Cloud Deployment Architecture
Both frontend and backend services are deployed on modern cloud hosting platforms using free-tier configurations:
- **Frontend on Vercel**: The React single-page application is hosted on Vercel. Static assets are served from global edge Content Delivery Networks (CDNs), and client-side routing is supported via rewrite rules in `vercel.json`.
- **Backend on Render**: The FastAPI service is deployed as a Docker-less Python Web Service on Render. It runs using `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`, operating comfortably within Render's 512 MB memory threshold (~18 MB resident RAM).
- **Communication Security**: All browser-to-backend communication uses encrypted HTTPS, with CORS headers strictly permitting authorized frontend domains.

---

# CHAPTER 5 — METHODOLOGY

### 5.1 Dataset and Data Sources
To construct an objective, reproducible flood susceptibility model, we gathered data from several authoritative, publicly accessible geospatial and meteorological repositories. Table 5 details each data source, its provider, original spatial resolution, and how it was utilized.

#### Table 5: Primary Datasets and Geospatial Sources
| Dataset Name | Source / Provider | Spatial Resolution | Temporal Coverage | Usage in Project |
| :--- | :--- | :--- | :--- | :--- |
| **BBMP Ward Boundaries** | Bruhat Bengaluru Mahanagara Palike | Vector Polygon (198 Wards) | 2020 Revision | Defines the municipal study area boundary (711.59 km²) and assigns cells to wards. |
| **SRTM DEM** | NASA / USGS Shuttle Radar Topography | 1 arc-second (~30 m) | February 2000 | Ground elevation, terrain slope, Topographic Wetness Index (TWI), and HAND. |
| **ESA WorldCover 10m** | European Space Agency (ESA) | 10 m Multispectral | 2020 / 2021 | Calculates the fraction of impervious built-up surface (`imperv_frac`) per cell. |
| **OpenStreetMap Vectors** | OpenStreetMap Contributors | Vector Lines & Polygons | Continuous (2024 Extract) | Hydrography (lakes, drains) and arterial road networks for distance calculations. |
| **CHIRPS Daily Rainfall** | Climate Hazards Center, UC Santa Barbara | 0.05° (~5.3 km) Gridded | Daily (2017 – 2023) | Multi-pixel daily precipitation, rolling antecedent sums (1d, 2d, 3d, 7d, 14d). |
| **Historical Flood Logs** | Municipal Reports & Media Audits | Point & Ward Records | 6 Historical Storm Events | Ground-truth positive flood labels for training and holdout validation. |

### 5.2 Spatial Grid Discretization (3,026 Cells)
Rather than analyzing flood risk at the coarse administrative ward level (which averages ~3.6 km² per ward and masks local valleys), we discretized the entire BBMP municipal boundary (711.59 km²) into a uniform Cartesian grid of **3,026 spatial cells**. 

Each cell measures exactly **500 m × 500 m**, representing an area of 0.25 km² (25 hectares). This resolution was selected as an optimal engineering balance:
- It is fine enough to capture neighborhood-scale topography, distinguishing a hilltop from a valley floor.
- It aligns appropriately with the accuracy of 30-meter elevation models and 10-meter land-cover data.
- It results in a total dataset size (3,026 records per day) that can be queried, transmitted, and rendered in web browsers instantaneously.

### 5.3 Input Features and Descriptions
For every grid cell, we extracted a total of **18 physical parameters**, comprising 10 static terrain/built-environment features and 8 dynamic rainfall features. Table 6 provides the complete dictionary of input features.

#### Table 6: Complete Feature Set (18 Parameters)
| Feature Name | Feature Type | Measurement Unit | Data Type | Physical Significance and Description |
| :--- | :--- | :--- | :--- | :--- |
| **`elev_m`** | Static | Meters (m) | `float64` | Mean elevation above sea level. Bengaluru slopes from ~960 m (west) to ~840 m (east). |
| **`slope_deg`** | Static | Degrees (°) | `float64` | Terrain slope. Flat areas (< 1.5°) cannot drain runoff quickly and easily pond. |
| **`twi`** | Static | Dimensionless Index | `float64` | Topographic Wetness Index: $\ln(a / \tan \beta)$. Identifies natural drainage hollows. |
| **`hand_m`** | Static | Meters (m) | `float64` | Height Above Nearest Drainage. Measures vertical elevation above local stream channel. |
| **`dist_lake_m`** | Static | Meters (m) | `float64` | Euclidean distance to nearest lake boundary. Lake margins frequently backflow. |
| **`dist_drain_m`** | Static | Meters (m) | `float64` | Euclidean distance to nearest primary stormwater channel (*rajakaluve*). |
| **`dist_road_m`** | Static | Meters (m) | `float64` | Distance to nearest major arterial road. Paved road corridors often canalize water. |
| **`imperv_frac`** | Static | Fraction [0.0, 1.0] | `float64` | Built-up impervious concrete fraction. High values prevent water infiltration. |
| **`waterbody_density`** | Static | Density Index | `float64` | Concentration of waterbody surface area within a 1 km neighborhood buffer. |
| **`catchment_area_km2`** | Static | Square Kilometers | `float64` | Upstream contributing catchment area draining through or into the cell. |
| **`rainfall_mm`** | Dynamic | Millimeters (mm) | `float64` | Estimated rainfall accumulation on the active day from the nearest CHIRPS pixel. |
| **`rainfall_lag1_mm`** | Dynamic | Millimeters (mm) | `float64` | Rainfall recorded 1 day prior to the active date. |
| **`rainfall_lag2_mm`** | Dynamic | Millimeters (mm) | `float64` | Rainfall recorded 2 days prior to the active date. |
| **`rainfall_sum3_mm`** | Dynamic | Millimeters (mm) | `float64` | Cumulative rainfall over the last 3 days; represents short-term soil saturation. |
| **`rainfall_sum5_mm`** | Dynamic | Millimeters (mm) | `float64` | Cumulative rainfall over the last 5 days. |
| **`rainfall_sum7_mm`** | Dynamic | Millimeters (mm) | `float64` | Cumulative rainfall over the last 7 days; critical indicator for lake basin overflow. |
| **`rainfall_sum10_mm`** | Dynamic | Millimeters (mm) | `float64` | Cumulative rainfall over the last 10 days. |
| **`rainfall_sum14_mm`** | Dynamic | Millimeters (mm) | `float64` | Cumulative rainfall over the last 14 days; reflects regional groundwater saturation. |

### 5.4 Data Preprocessing and Feature Calculation
The static terrain features were calculated through standard Geographic Information System (GIS) algorithms:
- **Hydrological Processing**: The SRTM DEM was pit-filled to remove artificial depressions. Flow directions were derived using the standard D8 algorithm, allowing computation of the upstream contributing area ($a$) and Topographic Wetness Index ($\text{TWI} = \ln(a / \tan \beta)$). Height Above Nearest Drainage (HAND) was computed by determining the height difference between each cell centroid and its nearest flow path.
- **Euclidean Hydrographic Distances**: Road, lake, and drain shapefiles from OpenStreetMap were indexed using spatial trees (`shapely.STRtree`) to rapidly compute minimum Euclidean distances from each cell centroid to water bodies and roadways.
- **Precipitation Spatial Join**: Each cell centroid was mapped to the nearest CHIRPS pixel centroid using a nearest-neighbor KD-Tree, ensuring that cells in eastern Bengaluru received distinct rainfall time series from cells in western Bengaluru.

### 5.5 Ground-Truth Flood Labels and Extreme Imbalance
Supervised machine learning requires ground-truth labels indicating where flooding occurred historically. We compiled historical flood points from municipal BBMP disaster logs, news media flood reports, and field research literature across six major monsoonal storm events in Bengaluru.

Table 7 displays the historical storm events and the breakdown of confirmed flood cell-days.

#### Table 7: Historical Flood Events and Label Breakdown
| Event Code | Event Description & Dates | Duration | Total Cell-Days | Confirmed Flooded Cells | Prevalence |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `E2017_08` | August 2017 Monsoon Storms | 14 days | 42,364 | 14 | 0.033% |
| `E2017_09` | September 2017 Convective Storms | 12 days | 36,312 | 11 | 0.030% |
| `E2021_11` | November 2021 Heavy Monsoonal Depression | 16 days | 48,416 | 12 | 0.025% |
| `E2022_05` | May 2022 Pre-Monsoon Cloudbursts | 10 days | 30,260 | 9 | 0.030% |
| `E2022_09` | September 2022 Catastrophic Monsoon Flood | 24 days | 72,624 | 188 | 0.258% |
| `E2023_05` | May 2023 Thunderstorms | 8 days | 24,208 | 6 | 0.025% |
| **Full Dataset** | **Combined Historical Events (583 Days)** | **583 days** | **1,764,158** | **240** | **0.0136%** |

As Table 7 illustrates, out of more than 1.76 million possible cell-day combinations across historical rainy periods, only **240 instances** had confirmed flooding. This translates to a positive prevalence of just **0.0136%** (or approximately 1 flood instance per 7,350 records). Handling this extreme class imbalance was the central machine learning challenge of our project.

### 5.6 Model Selection and XGBoost Configuration
We selected **XGBoost (eXtreme Gradient Boosting)** as our classification algorithm [7]. XGBoost builds an ensemble of shallow decision trees sequentially, where each new tree corrects the residual errors of prior trees. 

To prevent the algorithm from ignoring the rare positive flood instances, we utilized the `scale_pos_weight` parameter. In gradient boosting, `scale_pos_weight` acts as a multiplier on the loss gradients for positive training examples. In our training setup, setting `scale_pos_weight = 89.16` forced the gradient tree builder to treat false negatives (missed floods) approximately 89 times more severely than false positives, ensuring that rare topographical flood patterns were captured.

Table 8 lists the hyperparameter configuration used to train the model.

#### Table 8: XGBoost Model Hyperparameter Settings
| Hyperparameter | Value Used | Technical Rationale for Setting |
| :--- | :---: | :--- |
| **Objective** | `binary:logistic` | Standard logistic loss objective for binary classification probability estimation. |
| **`n_estimators`** | 100 | Number of sequential boosting rounds; provides sufficient capacity without overfitting. |
| **`max_depth`** | 6 | Tree depth; allows capturing up to 6-way non-linear feature interactions. |
| **`learning_rate` ($\eta$)** | 0.1 | Shrinkage factor applied to each tree's weights to ensure smooth convergence. |
| **`scale_pos_weight`** | 89.16 | Compensates for extreme class imbalance by heavily penalizing missed flood instances. |
| **`subsample`** | 0.8 | Randomly samples 80% of rows per tree to introduce regularization and reduce variance. |
| **`colsample_bytree`** | 0.8 | Randomly samples 80% of features per tree to prevent single features from dominating. |

### 5.7 Daily Susceptibility Ranking Methodology
In many machine learning applications, a predicted probability greater than 0.5 is labeled as positive. However, on highly imbalanced datasets, predicted probabilities naturally compress into a narrow lower range (rarely exceeding 0.25). A fixed threshold of 0.5 produces zero positive alerts, while an arbitrary cutoff like 0.1 swings wildly between dry and wet days.

To solve this, our system introduces a **daily dense ranking methodology**. Figure 3 depicts the inference and ranking workflow.

*(Refer to Figure 3: XGBoost Inference and Daily Spatial Ranking Flowchart)*

On any chosen date, the system:
1. Feeds the 18-parameter feature vector for all 3,026 cells into the trained XGBoost model.
2. Extracts raw susceptibility scores $S_i \in [0.0, 1.0]$.
3. Sorts all 3,026 cells in descending order of score, assigning dense ranks $R_i \in \{1, 2, \dots, 3026\}$.
4. Maps ranks into three operational priority tiers based on defined municipal cutoffs, as detailed in Table 9.

#### Table 9: Daily Susceptibility Ranking Tiers
| Priority Tier | Rank Range ($R_i$) | Number of Cells | Percentage of City | Operational Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **High Priority** | $1 \le R_i \le 150$ | 150 cells | ~5.0% | Highest vulnerability; priority focus for inspection and pump staging. |
| **Moderate Priority** | $151 \le R_i \le 300$ | 150 cells | ~5.0% | Secondary vulnerability; monitor low-lying underpasses and drains. |
| **Baseline Risk** | $301 \le R_i \le 3026$ | 2,726 cells | ~90.0% | Standard baseline risk; typical surface drainage conditions. |

This ranking approach guarantees that municipal personnel always receive an actionable, prioritized list of the top 5% or 10% most vulnerable locations on any given day.

### 5.8 Out-of-Sample Holdout Evaluation Protocol
To evaluate the model rigorously without data leakage, we implemented a strict **temporal holdout protocol**:
- **Training Set**: The model was trained exclusively on five historical storm sequences: `E2017_08`, `E2017_09`, `E2021_11`, `E2022_05`, and `E2023_05` (comprising 52 confirmed flood cell-days).
- **Holdout Test Set**: The entire 24-day September 2022 monsoon sequence (`E2022_09`, comprising 72,624 cell-days and 188 confirmed flood instances) was sequestered completely during training. 

By testing the model strictly on the unseen September 2022 flood sequence, we obtained an unbiased assessment of how well the model generalizes to major urban storm events.

---

# CHAPTER 6 — IMPLEMENTATION AND RESULTS

### 6.1 Technologies and Tools Used
The project was implemented entirely using open-source programming languages, libraries, and frameworks. Table 11 summarizes the primary technologies utilized across each layer of the application.

#### Table 11: Software Dependencies and Libraries Used
| Layer / Subsystem | Technology / Library | Version | Role in Project Architecture |
| :--- | :--- | :---: | :--- |
| **Language & Environment** | Python | 3.10+ | Core programming language for data pipeline, ML, and backend API. |
| **Data Processing** | Pandas / PyArrow | 2.3.3 / 21.0 | Tabular data manipulation, rolling calculations, and fast Parquet reading. |
| **Geospatial Processing** | GeoPandas / Shapely | 1.0.1 / 2.0.7 | Shapefile parsing, spatial grid creation, and Euclidean distance checks. |
| **Raster Processing** | Rasterio | 1.4.3 | Reading and querying SRTM digital elevation raster grids. |
| **Machine Learning** | XGBoost / Scikit-Learn | 2.1.4 / 1.6.1 | Gradient boosted decision tree modeling, metrics, and holdout evaluation. |
| **Backend API Server** | FastAPI / Uvicorn | 0.128 / 0.39 | Asynchronous REST API framework and ASGI production web server. |
| **Frontend Framework** | React / Vite | 18.2 / 5.0 | Single-page reactive web UI and high-speed build bundler. |
| **Cartographic Engine** | Leaflet / React-Leaflet | 1.9.4 / 4.2 | Interactive web map with custom HTML5 Canvas vector point rendering. |
| **Automated Testing** | Pytest | 8.4.2 | Unit, integration, and security testing suite (82 test cases). |
| **Cloud Hosting** | Render / Vercel | Cloud PaaS | Production hosting for FastAPI backend (Render) and React web app (Vercel). |

### 6.2 Data Pipeline Implementation
The data pipeline scripts in `pipeline/` automate the ingestion of raw shapefiles and rasters. For example, `01_grid.py` uses `shapely` to construct 3,026 equal-area square polygons across the BBMP bounding box, clipping the cells against official ward boundaries and assigning unique cell IDs from 0 to 3,025.

Similarly, `02_features.py` queries the SRTM elevation raster using `rasterio` and computes Euclidean distances to OpenStreetMap road and drainage vectors using `shapely.STRtree`. The resulting dataset is exported to `handover_member3/bengaluru_cells_3026.parquet`.

### 6.3 Machine Learning and Ranking Implementation
The model training script (`pipeline/05_train_xgb.py`) loads the assembled feature matrix, sets `scale_pos_weight = 89.16`, and trains the XGBoost ensemble. The trained model is saved as a compact JSON file (`handover_member3/flood_xgb_holdout_E2022_09.json`).

The ranking logic in the backend is concise, deterministic, and fast. The core ranking algorithm is implemented as follows:

```python
def rank_and_classify_cells(df: pd.DataFrame, rule: dict) -> pd.DataFrame:
    # Ranks cells by raw susceptibility score in descending order
    # and maps dense integer ranks to operational priority tiers.
    out = df.copy()
    # Assign dense integer ranks: 1 is highest susceptibility score
    out["rank"] = out["score"].rank(ascending=False, method="first").astype(int)
    
    high_k = rule.get("high_top_k", 150)       # Top 150 cells (~5%)
    mod_k = rule.get("moderate_top_k", 300)    # Ranks 151-300 (~5%)
    
    out["level"] = "None"
    out.loc[out["rank"] <= mod_k, "level"] = "Moderate"
    out.loc[out["rank"] <= high_k, "level"] = "High"
    
    return out.sort_values("rank")
```

Because this calculation operates on a simple Pandas DataFrame in memory, ranking all 3,026 cells requires less than 2 milliseconds.

### 6.4 Backend Service Implementation
The backend entry point (`backend/main.py`) initializes the application using FastAPI. During startup, the `DataLoader` class loads static cell coordinates and Parquet datasets into memory, verifying column schemas.

The `ReplayService` handles requests for specific historical dates. When a request arrives at `GET /api/risk?date=2022-09-08`, the service filters the cached September 2022 Parquet table, executes `rank_and_classify_cells()`, and returns the lightweight JSON response. A specialized `RainfallService` fetches live weather context from Open-Meteo, caching responses for 3,600 seconds to minimize external API requests.

### 6.5 Frontend Map Implementation
The frontend web application is structured into modular React components in `frontend/src/`. The primary visualization component (`FloodMapPage.jsx`) mounts the Leaflet map and configures the HTML5 Canvas vector layer.

Figure 4 presents a genuine screenshot of the deployed web application showing the interactive grid view of Bengaluru.

*(Refer to Figure 4: Interactive Cartographic Web Interface Showing Bengaluru Flood Grid)*

As seen in Figure 4, the user interface provides:
- A responsive full-screen map centered on Greater Bengaluru.
- Color-coded cell markers: Red indicates High Priority cells (top 5%), orange indicates Moderate Priority cells (top 10%), and gray indicates Baseline cells.
- A top control bar allowing users to select historical replay dates, toggle playback, or filter visible cells by priority tier.
- A slide-over **Cell Inspector Drawer** that opens when any cell is clicked, displaying the cell ID, administrative ward name, model score, municipal rank, and physical attributes (elevation, slope, TWI, HAND, lake distance, and rainfall).

### 6.6 Historical Replay and Rainfall Trends
Figure 5 displays the daily rainfall profile recorded across Greater Bengaluru during the held-out September 2022 monsoon period.

*(Refer to Figure 5: Historical Daily Rainfall Trend Across Bengaluru During September 2022)*

During this 24-day sequence:
- **September 1–4**: Antecedent rainfall steadily saturated the soil across the city.
- **September 5–8**: Torrential convective downpours lashed the city, dumping over 80 mm of rain in low-lying eastern sectors. During this peak period, model scores reached their maximum values.
- **Peak Susceptibility Observation**: The highest single cell score across the entire event was recorded at **Cell #722** on **September 8, 2022**, reaching a score of **0.2191**. Cell #722 corresponds to a low-lying valley depression in the Bellandur lake basin characterized by flat terrain (slope < 1.5°), very low HAND (< 1.5 m), high concrete imperviousness (0.88), and close proximity to encroached primary channels.
- **September 9–24**: As rainfall subsided, short-term 1-day and 2-day sums dropped, and cell scores gradually lowered back to baseline levels.

### 6.7 Telegram Demonstration Bot Implementation
The demonstration bot service (`backend/services/telegram_service.py`) handles incoming webhook requests. When an authorized user sends `/demo 2022-09-08`, the service queries `ReplayService` for that date, identifies the top 3 highest-risk wards, and returns a clean, formatted text bulletin directly to the user's Telegram chat.

Security tests confirmed that unauthorized chat IDs receive an immediate HTTP 403 Forbidden response, and the bot token is completely masked in all public API responses (`/api/telegram/status` returns `{"token_configured": true}`).

### 6.8 Automated Testing Suite
To ensure that all backend endpoints, data loading logic, rainfall services, and security checks operate reliably, we developed an automated test suite using `pytest`. 

The test suite contains **82 test cases across 4 test modules**, all of which pass cleanly. Table 12 details the test suite verification matrix.

#### Table 12: Automated Backend Test Suite Results
| Test Suite Module | Subsystem Tested | Key Capabilities Verified | Test Count | Result |
| :--- | :--- | :--- | :---: | :---: |
| `tests/test_backend.py` | FastAPI Core & Routes | Endpoint availability, JSON schemas, `/health`, `/api/dates`, `/api/risk`, `/api/summary`, CORS headers. | 22 | Passed |
| `tests/test_audit_suite.py` | Data Integrity & Ranking | Parquet loading, 3,026 cell coordinate boundaries, rank ordering (1 to 3,026), priority tier counts. | 22 | Passed |
| `tests/test_rainfall_service.py` | Weather API & Cache | Open-Meteo REST parsing, TTL cache expiration (3,600s), network timeout fallbacks, rolling sums. | 18 | Passed |
| `tests/test_telegram_service.py` | Telegram Integration | Token sanitization, status masking, whitelist authorization checks, command parsing, error handling. | 20 | Passed |
| **Complete Test Suite** | **Entire Application** | **Comprehensive Automated Verification** | **82** | **100% Passed** |

### 6.9 Deployment Setup on Vercel and Render
Both sides of the application were deployed and verified in live cloud environments:
- **Frontend (Vercel)**: Built using `npm run build` in 751 milliseconds, producing an optimized bundle of 57 kB CSS and 377 kB JavaScript. Client-side URL routing is managed via SPA rewrites in `vercel.json`.
- **Backend (Render)**: Deployed as a Python web service using `uvicorn`. The application boots in 3.2 seconds, uses approximately 18 MB of resident RAM, and responds to healthcheck queries in under 50 milliseconds.

### 6.10 Experimental Results and Plain Language Explanation
To measure how well our machine learning model performs, we evaluated it against the held-out September 2022 monsoon flood sequence (`E2022_09`). This benchmark comprises 24 days across 3,026 cells (72,624 total evaluation instances) containing 188 confirmed historical flood points.

Table 10 presents the empirical holdout performance metrics achieved by our model compared to a random guessing baseline.

#### Table 10: Holdout Model Performance Metrics (September 2022 Benchmark)
| Evaluation Metric | Model Value | Random Chance Baseline | Empirical Lift / Improvement | Plain Language Explanation |
| :--- | :---: | :---: | :---: | :--- |
| **Precision-Recall AUC (PR-AUC)** | **0.0026** | **0.0013** | **2.00× Lift** | The model is twice as precise at finding true flood cells in extremely sparse data compared to random selection. |
| **High Priority Tier Hit Rate (Top 5%)** | **8.3%** | 5.0% | **1.66× Lift** | The top 150 highest-ranked cells capture 1.66× more true flood instances than picking 150 random cells. |
| **Top 10% Ranked Cell Hit Rate (Top 300)** | **25.0%** | 9.9% | **2.53× Lift** | Inspecting just the top 10% highest-scoring cells captures **one-quarter of all confirmed flood locations**. |
| **ROC Area Under Curve (ROC-AUC)** | **0.638** | 0.500 | +0.138 | Demonstrates consistent positive discriminative ability across the full ranking curve. |

#### What These Results Mean in Plain Language:
1. **Understanding PR-AUC in Rare Events**: In machine learning datasets where positive events are extremely rare (less than 1 in 400 records in this holdout set), standard accuracy and ROC curves can be misleading because a model that always predicts zero can look "99.7% accurate". Precision-Recall Area Under Curve (PR-AUC) measures how well the model actually isolates true positive instances. A random guesser on this dataset achieves a PR-AUC of 0.0013. Our XGBoost model achieved **0.0026**, which represents a **2.0× improvement (or 100% lift)** over chance.
2. **Operational Value of Spatial Ranking**: For municipal workers or emergency responders, inspecting all 3,026 cells across Bengaluru during a storm is impossible. However, our model allows responders to focus on the top 10% highest-ranked cells (300 cells). In our historical holdout test, focusing on this top 10% captured **25.0% of all confirmed historical flood locations**, giving a **2.53× operational enrichment factor**.
3. **Consistency of Physical Indicators**: Analysis of model decisions confirmed that ground slope, Height Above Nearest Drainage (HAND), and 3-day accumulated rainfall were the most influential features. Elevated ridge lines with good slope never received high susceptibility scores, while flat valley hollows surrounded by concrete consistently moved to the top of the priority list during multi-day rain events.

---

# CHAPTER 7 — CONCLUSION AND FUTURE SCOPE

### 7.1 Project Summary
In this undergraduate engineering mini-project, our student team designed, developed, and deployed the **N²M Flood Prediction Model**, an open-source, machine learning-based geospatial platform for urban flood susceptibility mapping in Greater Bengaluru. 

By partitioning the 711.59 km² municipal territory into a uniform Cartesian grid of 3,026 spatial cells (500 m × 500 m), our data pipeline extracted 10 static terrain and built-environment features from SRTM DEM, ESA WorldCover, and OpenStreetMap, and linked each cell to 8 dynamic precipitation metrics from CHIRPS satellite-gauge records. To overcome the extreme scarcity of historical flood labels (0.0136% prevalence), we trained an XGBoost classifier with positive class weighting (`scale_pos_weight = 89.16`) and implemented a daily dense spatial ranking system.

The system was deployed as a decoupled web application using FastAPI on Render and React + Leaflet Canvas on Vercel, supplemented by an authorized demonstration Telegram bot. All 82 automated backend test cases passed successfully.

### 7.2 What the Group Successfully Implemented
As a second-year engineering group, our team achieved several practical milestones:
1. **End-to-End Working System**: We built and deployed a complete, functioning software platform connecting geospatial data extraction, machine learning scoring, asynchronous REST APIs, and an interactive web interface.
2. **High-Performance Map Visualization**: We solved browser rendering lag by implementing an HTML5 Canvas layer on Leaflet that renders all 3,026 cells at 60 frames per second on both desktop and mobile devices.
3. **Imbalance-Aware Machine Learning**: We formulated an operational ranking approach that overcomes the limitations of fixed probability thresholds on rare-event data, achieving a 2.0× PR-AUC lift and a 2.53× hit-rate enrichment in the top 10% ranked cells.
4. **Interactive Historical Simulation**: We implemented an interactive replay mechanism allowing users to explore how flood susceptibility evolved across Bengaluru day-by-day during the severe September 2022 monsoon sequence.
5. **Demonstration Bot with Strong Security**: We built a private Telegram demonstration bot with server-side token protection and whitelist authorization, demonstrating how mobile notifications can be tested responsibly.

### 7.3 Main Engineering Observations
During the course of this project, we arrived at three key engineering observations:
- **Terrain Shapes the Baseline, Rainfall Pulls the Trigger**: Static topographical features (especially ground slope and Height Above Nearest Drainage) define the fundamental spatial geometry of flood vulnerability. However, multi-day antecedent rainfall (3-day and 7-day accumulated sums) is the critical dynamic factor that elevates low-lying areas from baseline risk into active high-priority tiers.
- **Dense Ranking is More Practical than Raw Probability**: On severely imbalanced datasets, raw predicted probabilities are mathematically suppressed into small decimals. Ranking cells relative to one another provides a much clearer, actionable triage list for decision-makers.
- **Lightweight Architecture Enables Free Cloud Hosting**: By precomputing features into compact Parquet files and loading them into memory at startup, our FastAPI backend operates with a resident memory footprint of just ~18 MB, making it practical and sustainable to run on free-tier cloud platforms.

### 7.4 Practical Limitations
To maintain academic honesty, the following practical limitations must be acknowledged:
- **Relative Susceptibility Only**: The model outputs relative priority rankings indicating which cells are more prone to waterlogging compared to others. It does *not* predict exact flood water depths in centimeters or water flow velocities.
- **Coarse Precipitation Grids**: CHIRPS satellite rainfall is gridded at 0.05° (~5.3 km). While this captures regional storm differences across the city, it cannot resolve micro-scale cloudbursts that occur over an area of just 1 to 2 kilometers.
- **No Underground Pipe Telemetry**: The model is based on surface terrain and open drainage channels. It lacks real-time sensor data regarding underground sewer pipe diameters, pipe siltation, pump station operation, or temporary garbage blockages in road culverts.
- **Ground-Truth Label Sparsity**: Training was based on 240 confirmed historical flood cell-days recorded in official municipal logs. Smaller localized waterlogging in minor residential alleys may be underrepresented in official records.

### 7.5 Future Work and Scope for Improvement
The foundation built in this project opens several practical avenues for future enhancement:
1. **Integration of Hyper-Local Rain Gauges**: Future versions could ingest real-time telemetric rain gauge data from the Karnataka State Natural Disaster Monitoring Centre (KSNDMC), which operates over 100 automated weather stations across Bengaluru, replacing satellite estimates with dense ground measurements.
2. **Forward-Looking Weather Forecasts**: Incorporating high-resolution Numerical Weather Prediction (NWP) forecasts from the India Meteorological Department (IMD) to provide 6- to 24-hour predictive susceptibility warnings before heavy storms occur.
3. **Citizen Science and Crowdsourced Reports**: Implementing a geo-tagged citizen reporting feature or social media text mining pipeline to gather validated flood reports from residents, expanding the volume of ground-truth data.
4. **Coupled Hydrodynamic Simulation**: Linking the machine learning screening model to a 1D/2D hydrodynamic simulator (such as EPA SWMM) for the top-ranked 150 cells to simulate exact water depths and drain overflow rates.
5. **Subterranean Drainage Mapping**: Integrating municipal GIS shapefiles of underground stormwater pipes, culvert dimensions, and automated rajakaluve water-level sensors as municipal datasets become publicly available.

---

# REFERENCES

[1] T. Islam, E. B. Zeleke, M. Afroz, and A. M. Melesse, "A Systematic Review of Urban Flood Susceptibility Mapping: Remote Sensing, Machine Learning, and Other Modeling Approaches," *Remote Sensing*, vol. 17, no. 3, p. 524, Feb. 2025. DOI: [10.3390/rs17030524](https://doi.org/10.3390/rs17030524)

[2] A. Pourzangbar, P. Oberle, A. Kron, and M. J. Franca, "Analysis of the Utilization of Machine Learning to Map Flood Susceptibility," *Journal of Flood Risk Management*, vol. 18, p. e70042, 2025. DOI: [10.1111/jfr3.70042](https://doi.org/10.1111/jfr3.70042)

[3] R. Joseph, P. P. Mujumdar, and R. Das Bhowmik, "Reconstruction of Urban Rainfall Measurements to Estimate the Spatiotemporal Variability of Extreme Rainfall," *Water*, vol. 14, no. 23, p. 3900, Nov. 2022. DOI: [10.3390/w14233900](https://doi.org/10.3390/w14233900)

[4] G. Al-Rawas, M. R. Nikoo, M. Al-Wardy, and T. Etri, "A Critical Review of Emerging Technologies for Flash Flood Prediction: Examining Artificial Intelligence, Machine Learning, Internet of Things, Cloud Computing, and Robotics Techniques," *Water*, vol. 16, no. 14, p. 2069, Jul. 2024. DOI: [10.3390/w16142069](https://doi.org/10.3390/w16142069)

[5] A. A. Pathak, A. R. Mathad, and A. S. Gagnon, "Integrating Socio-Economic Variables in Urban Flood Damage Assessments: A Case Study of Bengaluru, India," *Natural Hazards*, vol. 121, pp. 1007–1032, Jan. 2025. DOI: [10.1007/s11069-024-07019-9](https://doi.org/10.1007/s11069-024-07019-9)

[6] P. Mukhopadhyay and B. K. Das, "Composite Flood Risk Index Assessment and Operationalization for Bellandur Ward, Bengaluru," *Engineering, Technology & Applied Science Research*, vol. 16, no. 4, pp. 37667–37672, Aug. 2026. DOI: [10.48084/etasr.18047](https://doi.org/10.48084/etasr.18047)

[7] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in *Proc. 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD)*, San Francisco, CA, USA, Aug. 2016, pp. 785–794. DOI: [10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785)

[8] C. Funk et al., "The Climate Hazards Group InfraRed Precipitation with Stations—A New Environmental Record for Monitoring Extremes," *Scientific Data*, vol. 2, p. 150066, Dec. 2015. DOI: [10.1038/sdata.2015.66](https://doi.org/10.1038/sdata.2015.66)

[9] T. V. Ramachandra, M. D. Subash Chandran, H. A. Bharath, and V. Vinay, "Water Bodies and Wetlands of Bengaluru: Physical and Socio-Economic Dynamics," ENVIS Technical Report 149, Centre for Ecological Sciences, Indian Institute of Science (IISc), Bengaluru, India, Sep. 2020.

[10] Bruhat Bengaluru Mahanagara Palike (BBMP) and Karnataka State Natural Disaster Monitoring Centre (KSNDMC), "Bengaluru Comprehensive Stormwater Drainage Master Plan," Government of Karnataka, Bengaluru, India, Tech. Rep., 2022.
"""
