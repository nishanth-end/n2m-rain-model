# N²M Flood Prediction Model — System Architecture

This document provides a comprehensive technical overview of the system architecture, frontend and backend implementations, in-memory data structures, scoring execution, and geospatial rendering pipelines for the **N²M Flood Prediction Model**.

---

## 1. High-Level Architectural Overview

The system is organized into a clean, decoupled three-tier topology:
1. **Data & Artifact Layer**: Pre-computed static GIS files, historical event feature archives (Apache Parquet), and trained XGBoost boosters.
2. **Backend Engine (FastAPI)**: Asynchronous REST API service providing in-memory caching, vectorized scoring, rank-based tier partitioning, and simulation scaffolding.
3. **Frontend Cartographic Interface (React 18 + Leaflet)**: Single-page application rendering an urban mesh of 3,026 spatial cells on a GPU-accelerated HTML5 Canvas with interactive historical replay controls.

---

## 2. Diagram 1: System Architecture

The following diagram illustrates the relationship between all components across the frontend, backend, and data storage layers:

```mermaid
flowchart TD
    subgraph Data_Storage ["Data & Artifact Storage (handover_member3 / delivery)"]
        PARQUET[("flood_replay_E2022_09.parquet<br/>72,624 rows (24 days × 3,026 cells)")]
        STATIC_CSV[("cells_static.csv<br/>3,026 cells × 10 terrain features")]
        PIXEL_MAP[("cell_pixel_map.csv<br/>Linkage to 37 CHIRPS pixels")]
        XGB_HOLDOUT["flood_xgb_holdout_E2022_09.json<br/>XGBoost Holdout Model (scale_pos_weight=89.16)"]
        THRESHOLDS["thresholds.json<br/>High: Top 150 (5%), Moderate: Top 300 (10%)"]
    end

    subgraph Backend_Service ["FastAPI Backend Engine (Python 3.9+ :8000)"]
        subgraph Data_Access ["Data Access Layer"]
            LOADER["data_loader.py<br/>• In-memory Parquet cache<br/>• Static feature joining<br/>• Date index construction"]
        end

        subgraph Core_Services ["Domain Services"]
            SCORE_ENGINE["handover_member3/score_cells.py<br/>• Feature extraction & matrix building<br/>• XGBoost booster prediction<br/>• Daily rank & level assignment"]
            REPLAY_SVC["backend/services/replay_service.py<br/>• Date filtering (2022-08-22 to 2022-09-14)<br/>• Score caching & summary statistics<br/>• Query filtering (level, limit)"]
            SCAFFOLD_SVC["backend/services/pipeline_scaffold.py<br/>• Feature compatibility validation<br/>• Isolated live rainfall stub (disabled)"]
            TELEGRAM_SVC["backend/services/telegram_service.py<br/>• In-memory alert payload formatter<br/>• Prominent disclaimer injection"]
        end

        subgraph API_Layer ["HTTP / OpenAPI Routing (backend/main.py)"]
            ROUTES["FastAPI Routes:<br/>• GET /api/dates<br/>• GET /api/risk<br/>• GET /api/risk/latest<br/>• GET /api/summary<br/>• GET /api/about<br/>• GET /api/pipeline/status<br/>• GET /api/telegram/demo-preview"]
            CORS["CORSMiddleware<br/>Allows local frontend origins"]
            SCHEMAS["backend/schemas/responses.py<br/>Pydantic strict response models"]
        end
    end

    subgraph Frontend_App ["Cartographic Frontend Application (React 18 + Vite :5173)"]
        subgraph State_Management ["Client State & Networking"]
            HTTP_CLIENT["frontend/src/api/client.js<br/>Axios client with base URL http://127.0.0.1:8000"]
            APP_STATE["App.jsx<br/>Active tab routing (Home, Map, Sim, TG, Team)"]
            CONTENT_CFG["frontend/src/config/content.js<br/>Centralized academic text & [ADD ...] placeholders"]
        end

        subgraph Presentation_Views ["Views & Cartographic Canvas"]
            NAV["Navigation.jsx (Header + Live API indicator)"]
            MAP_VIEW["FloodMapPage.jsx<br/>• OpenStreetMap standard raster tiles (No API key)<br/>• Leaflet L.circleMarker with Canvas renderer<br/>• 24-day stepper & Play/Pause replay state machine<br/>• Interactive cell click & bottom telemetry drawer"]
            SIM_VIEW["LiveSimulationPage.jsx (Rainfall context + Slider lab)"]
            TG_VIEW["TelegramPage.jsx (Bot alert dispatch sandbox)"]
            HOME_VIEW["HomePage.jsx (Academic problem statement & model stats)"]
            TEAM_VIEW["CreatorsPage.jsx (Maintainers & dataset attribution)"]
        end
    end

    PARQUET --> LOADER
    STATIC_CSV --> LOADER
    PIXEL_MAP --> LOADER
    XGB_HOLDOUT --> SCORE_ENGINE
    THRESHOLDS --> SCORE_ENGINE

    LOADER --> REPLAY_SVC
    SCORE_ENGINE --> REPLAY_SVC
    REPLAY_SVC --> ROUTES
    SCAFFOLD_SVC --> ROUTES
    TELEGRAM_SVC --> ROUTES
    SCHEMAS --> ROUTES

    ROUTES <-->|HTTP / JSON :8000| HTTP_CLIENT
    HTTP_CLIENT --> MAP_VIEW
    HTTP_CLIENT --> SIM_VIEW
    HTTP_CLIENT --> TG_VIEW
    CONTENT_CFG --> HOME_VIEW
    CONTENT_CFG --> TEAM_VIEW
    CONTENT_CFG --> TG_VIEW
    CONTENT_CFG --> SIM_VIEW
```

---

## 3. Diagram 2: Data Flow Pipeline

The following diagram tracks the lifecycle of spatial and meteorological data, from spaceborne acquisition to client-side vector rendering:

```mermaid
flowchart LR
    subgraph S1 ["1. Spaceborne & Civic Ingestion"]
        CHIRPS["CHIRPS 0.05°<br/>Daily Precipitation Grid (~5.3km)"]
        DEM["NASA / Copernicus<br/>30m Digital Elevation Model"]
        OSM["OpenStreetMap<br/>Roads, Drains, Lakes"]
    end

    subgraph S2 ["2. Spatial Preprocessing & Hydrology"]
        MESH["Bengaluru Urban Mesh<br/>3,026 equal-area cells (~500m)"]
        TERRAIN["Terrain Feature Extraction<br/>• Elevation & Slope<br/>• TWI: ln(a / tan β)<br/>• HAND: Height above drainage<br/>• Flow accumulation<br/>• Built impervious fraction"]
        HYDRO["Proximity Graphs<br/>• dist_lake_m<br/>• dist_drain_m<br/>• dist_road_m<br/>• lakes_within_1km"]
        PIXEL_LINK["Spatial Spatial Join<br/>Map cell centroid to CHIRPS pixel ID"]
    end

    subgraph S3 ["3. Dynamic Feature Assembly"]
        RAIN_MAT["Antecedent Rainfall Matrix<br/>• rain_1d_mm (observation day)<br/>• rain_3d, 7d, 14d, 30d (rolling sums)<br/>• rain_lag1, lag2, lag3 (preceding days)"]
        JOIN["Feature Matrix<br/>10 Static + 8 Dynamic Features<br/>(18 features per cell)"]
    end

    subgraph S4 ["4. XGBoost Holdout Scoring"]
        MODEL["XGBoost Holdout Model<br/>binary:logistic, scale_pos_weight=89.16"]
        SCORES["Continuous Susceptibility Index<br/>Score ∈ [0, 1] per cell"]
        RANK_SORT["Dense Rank Sort<br/>Sort descending by score"]
        TIERS["Rank-Based Partitioning:<br/>• Rank 1–150: High (Top 5%)<br/>• Rank 151–300: Moderate (Next 5%)<br/>• Rank 301–3026: Baseline (Remaining 90%)"]
    end

    subgraph S5 ["5. Client-Side GPU Rendering"]
        JSON_PAYLOAD["FastAPI JSON Response<br/>3,026 records with coords, score, rank, tier"]
        CANVAS["Leaflet Canvas Renderer<br/>Single HTML5 &lt;canvas&gt; layer<br/>Color-coded circle markers at 60 FPS"]
    end

    CHIRPS --> PIXEL_LINK
    DEM --> TERRAIN
    OSM --> HYDRO
    MESH --> TERRAIN
    MESH --> HYDRO
    MESH --> PIXEL_LINK

    TERRAIN --> JOIN
    HYDRO --> JOIN
    PIXEL_LINK --> RAIN_MAT
    RAIN_MAT --> JOIN

    JOIN --> MODEL
    MODEL --> SCORES
    SCORES --> RANK_SORT
    RANK_SORT --> TIERS

    TIERS --> JSON_PAYLOAD
    JSON_PAYLOAD --> CANVAS
```

---

## 4. Diagram 3: Historical Replay Workflow

The historical replay engine allows users to observe the evolution of flood susceptibility during the benchmark September 2022 monsoon event. The diagram below illustrates the replay cycle, state transitions, and caching:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser as React Frontend (FloodMapPage)
    participant Client as API Client (client.js)
    participant Backend as FastAPI Server (:8000)
    participant Service as ReplayService (In-Memory Cache)
    participant Canvas as Leaflet HTML5 Canvas Layer

    User->>Browser: Select Replay Tab / Click Date Stepper (e.g. 2022-09-08)
    Browser->>Client: getRiskByDate("2022-09-08")
    Client->>Backend: GET /api/risk?date=2022-09-08
    
    alt Date in Memory Cache
        Backend->>Service: Query cached scored DataFrame for 2022-09-08
        Service-->>Backend: Return pre-computed 3,026 ranked records
    else Date not yet scored
        Backend->>Service: Slice flood_replay_E2022_09.parquet for date
        Service->>Service: Call score_day(df, model, feats, rule)
        Service->>Service: Sort descending, assign ranks 1..3026, assign High/Moderate/None
        Service->>Service: Store in _score_cache["2022-09-08"]
        Service-->>Backend: Return scored records
    end

    Backend-->>Client: 200 OK (JSON with 3,026 cell items, tier counts, summary)
    Client-->>Browser: Resolve Promise with cell array
    
    Browser->>Canvas: Clear previous frame markers
    Browser->>Canvas: Batch draw 3,026 circle markers via Canvas renderer:
    Note over Browser,Canvas: High (Red, radius 6px)<br/>Moderate (Amber, radius 5px)<br/>Baseline (Grey dot, radius 2px)
    Canvas-->>User: Visual map update completed (rendered within < 50ms)

    opt User Clicks a Grid Cell (e.g. Cell 722)
        User->>Browser: Click cell marker on Canvas
        Browser->>Browser: Set selectedCell = cellData
        Browser-->>User: Open Telemetry Drawer (Show Elevation, TWI, HAND, Rain)
    end

    opt User Activates Automated Replay
        User->>Browser: Click "▶ Replay" button
        loop Every 2000 ms until Day 24
            Browser->>Browser: Advance date index (i -> i + 1)
            Browser->>Client: Fetch next day risk
            Client-->>Browser: Receive day payload
            Browser->>Canvas: Redraw Canvas markers
        end
        Note over Browser: Reaching Day 24 (2022-09-14) stops playback gracefully
    end
```

---

## 5. Component Breakdown & Implementation Details

### 5.1 Data Access Layer (`backend/data_loader.py`)
- **Initialization**: Loads `cells_static.csv`, `cell_pixel_map.csv`, and `flood_replay_E2022_09.parquet` into RAM on application startup (`@app.on_event("startup")`).
- **Memory Footprint**: ~15 MB RAM consumed by cached DataFrames.
- **Access Pattern**: $O(1)$ dictionary lookup on partitioned date slices.

### 5.2 Replay Service (`backend/services/replay_service.py`)
- **Preserved Scoring Core**: Calls `handover_member3/score_cells.py::score_day` without altering model evaluation logic.
- **Caching Mechanism**: Maintains a dictionary `_score_cache[date_str]` storing the fully ranked Pandas DataFrame. Subsequent requests for the same date return instantly ($< 5\text{ ms}$).
- **Query Filtering**: Supports `level` (`High`, `Moderate`, `None`) and `limit` ($N \ge 1$) query parameters, executed as fast Pandas vector operations.

### 5.3 Frontend Cartography & High-FPS Canvas Renderer (`frontend/src/pages/FloodMapPage.jsx`)
- **Basemap**: OpenStreetMap standard raster tiles (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`). Requires no commercial API tokens.
- **Canvas Acceleration**: Leaflet is initialized with `preferCanvas: true`. Rather than instantiating 3,026 distinct SVG `<path>` DOM elements, all markers are composited on a single HTML5 `<canvas>` context.
- **CSS Constraint Handling**: Leaflet internally relies on `L.canvas` having unrestricted dimensional padding (`padding: 0.5`). Global CSS resets containing `canvas { max-width: 100%; }` are overridden via `.leaflet-container canvas { max-width: none !important; }` to maintain accurate pixel-to-geographic coordinate transformations.
- **Replay State Machine**: Controlled via `isPlaying`, `selectedDate`, and a `useRef` timer. Autoplay evaluates `currentIndex < dates.length - 1` on each tick and halts automatically at `2022-09-14` without looping.
