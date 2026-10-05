# Predictive Flood Alert System — Bengaluru Prototype

> **Team N²M · 1BCP308 Community Project**  
> An end-to-end, connected predictive flood hazard system coupling high-resolution urban terrain features with rainfall forecasts through a trained XGBoost machine learning model.

---

## Overview

During monsoon events in Bengaluru (such as the severe storms of September 2022 and May 2022), flood impacts vary drastically across neighborhoods due to micro-topography, culvert dimensions, and stormwater drain (*rajakaluve*) configurations. 

This platform connects:
1. **Interactive Geospatial Map (`/index.html`)**: Dynamically visualizes 8 documented Bengaluru flood and contrast zones on a Leaflet map. Live 10-day rainfall series drives real-time hazard scoring, comparing predicted risk bands (fill color) against documented historical ground truth (outer ring color).
2. **Machine Learning Intelligence (`/ml.html`)**: Detailed architecture pipeline (responsive inline SVG), dual temporal (Leave-One-Event-Out) and spatial (Ward-Grouped 5-Fold) cross-validation reports, feature importance rankings, and an interactive SHAP contribution analyzer.
3. **Data Transparency (`/data.html`)**: Complete data provenance audit, column specification dictionary from Member 1's specification, summary statistics, and server-side paginated observation explorer with CSV download.
4. **Project Information (`/about.html`)**: Context, architecture, maintainers grid with clear placeholders, community reporting workflows, and ethical considerations.

---

## Project Structure

```text
n2m-rain-predictive-model/
├── backend/
│   ├── app.py                  # FastAPI server (predictions, data APIs, static hosting)
│   ├── zone_features.json      # Nearest mock-cell mappings for 8 Bengaluru zones
│   └── requirements.txt        # Pinned Python package dependencies
├── data/
│   ├── flood_dataset.csv       # Observation dataset (cell-day matrix)
│   ├── DATA_STATUS.json        # Synthetic/real data mode indicator & audit note
│   └── events.csv              # Historical storm events
├── model/
│   ├── make_mock_dataset.py    # Generates synthetic demonstration dataset
│   ├── train_real.py           # Trains XGBoost and evaluates leave-one-out & spatial CV
│   ├── flood_xgb_real.json     # Trained XGBoost model artifact
│   ├── features.json           # Ordered feature list expected by model
│   └── model_report.json       # Exported metrics, hyperparameters, and feature importances
├── docs/                       # Frontend application (pure vanilla JS + HTML/CSS)
│   ├── index.html              # Interactive map & rainfall scoring console
│   ├── ml.html                 # Pipeline diagram, evaluation metrics & live explainer
│   ├── data.html               # Data provenance, dictionary, stats & paginated table
│   ├── about.html              # Project overview, team grid & ethics
│   ├── css/
│   │   └── app.css             # Dark theme styles (Georgia font, responsive)
│   └── js/
│       └── common.js           # API client, persistent banner, rainfall component
└── README.md                   # Setup and execution guide
```

---

## Quickstart: Step-by-Step Instructions

### 1. Prerequisites
- **Python 3.9+**
- On macOS: OpenMP runtime (installed automatically with Homebrew via `brew install libomp`)

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Pinned Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Generate Mock Dataset
```bash
python model/make_mock_dataset.py
mv flood_dataset.csv data/flood_dataset.csv
```

### 5. Train the Model & Export Metrics
```bash
python model/train_real.py data/flood_dataset.csv
```
This produces `model/flood_xgb_real.json`, `model/features.json`, and `model/model_report.json`.

### 6. Launch Backend Server
Run the FastAPI application with Uvicorn. This serves both the API endpoints and the frontend pages:
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Open the Web Application
Open your web browser and navigate to:
- **Map & Real-Time Scorer**: [http://localhost:8000/](http://localhost:8000/) or [http://localhost:8000/index.html](http://localhost:8000/index.html)
- **ML Pipeline & Performance**: [http://localhost:8000/ml.html](http://localhost:8000/ml.html)
- **Data Transparency & Download**: [http://localhost:8000/data.html](http://localhost:8000/data.html)
- **About & Team**: [http://localhost:8000/about.html](http://localhost:8000/about.html)

---

## Swapping in Real Data (Zero Code Changes)

When Member 1 delivers the real `flood_dataset.csv` derived from CHIRPS precipitation, Copernicus DEM, and Sentinel-1 SAR imagery:
1. Replace `data/flood_dataset.csv` with the real file.
2. In `data/DATA_STATUS.json`, set `"is_synthetic": false`.
3. Retrain the model:
   ```bash
   python model/train_real.py data/flood_dataset.csv
   ```
4. Restart the server:
   ```bash
   uvicorn backend.app:app --port 8000
   ```
The frontend persistent warning banner will automatically disappear, and all pages will reflect real model predictions without changing a single line of backend or UI code.

---

## API Documentation

Interactive Swagger documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

Key endpoints:
- `GET  /api/health` — Service readiness and data status.
- `GET  /api/zones` — 8 Bengaluru zones with nearest grid-cell terrain features.
- `POST /api/predict` — Score risk and SHAP contributions for a single zone with 10-day rainfall.
- `POST /api/predict_all` — City-wide 10-day rainfall applied across all 8 zones.
- `GET  /api/model_report` — Comprehensive model evaluation metrics and hyperparameters.
- `GET  /api/data` — Paginated and filterable rows from `flood_dataset.csv`.
- `GET  /api/data/summary` — Aggregate dataset statistics, date spans, and column profiles.
- `GET  /api/data/columns` — Specification column dictionary.
- `GET  /download/flood_dataset.csv` — Raw dataset download.

---

## Team & Academic Citation

Developed for **1BCP308 Community Project** by **Team N²M**.
