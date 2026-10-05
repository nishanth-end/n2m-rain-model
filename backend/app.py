"""
Backend API for Predictive Flood Alert System.
Serves ML predictions, dataset queries, and static frontend pages.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Union
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
import xgboost as xgb

# ---------------------------------------------------------
# Configuration & Paths
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "model")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DATASET_PATH = os.path.join(DATA_DIR, "flood_dataset.csv")
DATA_STATUS_PATH = os.path.join(DATA_DIR, "DATA_STATUS.json")
MODEL_PATH = os.path.join(MODEL_DIR, "flood_xgb_real.json")
FEATURES_PATH = os.path.join(MODEL_DIR, "features.json")
REPORT_PATH = os.path.join(MODEL_DIR, "model_report.json")
ZONE_FEATURES_PATH = os.path.join(BASE_DIR, "backend", "zone_features.json")

app = FastAPI(
    title="Predictive Flood Alert System API",
    description="API for real-time flood risk scoring using XGBoost and Bengaluru terrain features",
    version="1.0.0"
)

# Enable CORS for external / decoupled frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory cache
MODEL: Optional[xgb.XGBClassifier] = None
FEATURES: List[str] = []
MODEL_REPORT: Dict[str, Any] = {}
DATA_STATUS: Dict[str, Any] = {}
ZONES_DATA: List[Dict[str, Any]] = []
DATA_DF: Optional[pd.DataFrame] = None
BEST_CSI_THR: float = 0.65
MIN_RAIN_3D: float = 10.0

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return R * c

def calculate_risk_band(score: float, thr: float) -> str:
    """
    Classify uncalibrated risk score into 4 intuitive bands based on best-CSI threshold T:
    - Low: score < 0.5 * T
    - Moderate: 0.5 * T <= score < T
    - High: T <= score < T + 0.5 * (1 - T)
    - Severe: score >= T + 0.5 * (1 - T)
    """
    t_mod = 0.5 * thr
    t_sev = thr + 0.5 * (1.0 - thr)
    if score < t_mod:
        return "Low"
    elif score < thr:
        return "Moderate"
    elif score < t_sev:
        return "High"
    else:
        return "Severe"

def load_or_generate_zone_features(df: pd.DataFrame) -> List[Dict[str, Any]]:
    default_zones = [
        { "id": 1, "name": "RBD Layout (Sarjapur Road)", "lat": 12.901, "lon": 77.700, "flooded": 1, "catchment": 10.1,
          "cause": "Layout built on/near rajakaluve; raised road levels created a locked low pocket",
          "event": "2022-09-05 (also flooded 2022-05-05)", "confidence": "high" },
        { "id": 2, "name": "Wipro Campus (Sarjapur Road)", "lat": 12.900, "lon": 77.696, "flooded": 1, "catchment": 11.5,
          "cause": "Road divider + tech park construction blocked natural discharge path",
          "event": "2022-09-05", "confidence": "high" },
        { "id": 3, "name": "Outer Ring Road (RMZ Ecospace / Saul Kere)", "lat": 12.927, "lon": 77.693, "flooded": 1, "catchment": 27.9,
          "cause": "Metro rail median wall blocked natural overland spill route",
          "event": "2022-09-05", "confidence": "high" },
        { "id": 4, "name": "Epsilon Layout / Yemalur Road", "lat": 12.933, "lon": 77.687, "flooded": 1, "catchment": 191.0,
          "cause": "Bridge undersized; wetland filled for STP construction removed a discharge channel",
          "event": "2022-09-05", "confidence": "high" },
        { "id": 5, "name": "Borewell Road (Whitefield)", "lat": 12.969, "lon": 77.750, "flooded": 1, "catchment": 3.3,
          "cause": "Lake breach + demolition of informal stop wall during anti-encroachment drive",
          "event": "2022-09-07", "confidence": "high" },
        { "id": 6, "name": "Panathur-Balagere Road", "lat": 12.939, "lon": 77.699, "flooded": 1, "catchment": 209.0,
          "cause": "New bridge undersized for ~28% of city's runoff; barricade blocked overland spill",
          "event": "2022-09-05", "confidence": "high" },
        { "id": 7, "name": "Malleswaram (contrast)", "lat": 13.0068, "lon": 77.5709, "flooded": 0, "catchment": None,
          "cause": "Older, higher-elevation core-city area; not reported as significantly affected",
          "event": "2022-09-05 (same storm, no flooding reported)", "confidence": "general knowledge — verify" },
        { "id": 8, "name": "Jayanagar (contrast)", "lat": 12.9308, "lon": 77.5838, "flooded": 0, "catchment": None,
          "cause": "Older, higher-elevation core-city area; not reported as significantly affected",
          "event": "2022-09-05 (same storm, no flooding reported)", "confidence": "general knowledge — verify" },
    ]
    
    unique_cells = df.drop_duplicates(subset=["cell_id"]).copy()
    terrain_cols = [
        "elev_m", "slope_deg", "twi", "hand_m", "flow_acc", "imperv_frac",
        "dist_lake_m", "dist_drain_m", "dist_road_m", "lakes_within_1km"
    ]
    
    matched_zones = []
    for z in default_zones:
        dists = haversine_km(z["lat"], z["lon"], unique_cells["lat"].values, unique_cells["lon"].values)
        idx = int(np.argmin(dists))
        best_cell = unique_cells.iloc[idx]
        dist_km = float(dists[idx])
        
        terrain_features = {
            col: float(best_cell[col]) for col in terrain_cols if col in best_cell and pd.notna(best_cell[col])
        }
        
        mz = dict(z)
        mz["matched_cell_id"] = int(best_cell["cell_id"])
        mz["distance_km"] = round(dist_km, 3)
        mz["distance_m"] = round(dist_km * 1000.0, 1)
        mz["matched_cell_lat"] = round(float(best_cell["lat"]), 4)
        mz["matched_cell_lon"] = round(float(best_cell["lon"]), 4)
        mz["terrain_features"] = terrain_features
        matched_zones.append(mz)

    with open(ZONE_FEATURES_PATH, "w") as f:
        json.dump(matched_zones, f, indent=2)
        
    return matched_zones

# ---------------------------------------------------------
# Application Startup Event
# ---------------------------------------------------------
@app.on_event("startup")
def startup_event():
    global MODEL, FEATURES, MODEL_REPORT, DATA_STATUS, ZONES_DATA, DATA_DF, BEST_CSI_THR, MIN_RAIN_3D
    
    # 1. Load Model
    if os.path.exists(MODEL_PATH):
        MODEL = xgb.XGBClassifier()
        MODEL.load_model(MODEL_PATH)
        print(f"Loaded XGBoost model from {MODEL_PATH}")
    else:
        print(f"WARNING: Model file not found at {MODEL_PATH}")

    # 2. Load Features list
    if os.path.exists(FEATURES_PATH):
        with open(FEATURES_PATH, "r") as f:
            FEATURES = json.load(f)
        print(f"Loaded {len(FEATURES)} features: {FEATURES}")
    else:
        print(f"WARNING: Features file not found at {FEATURES_PATH}")

    # 3. Load Model Report
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r") as f:
            MODEL_REPORT = json.load(f)
        MIN_RAIN_3D = float(MODEL_REPORT.get("min_rain_3d", 10.0))
        # Best-CSI threshold from leave-one-event-out or spatial-cv
        loo = MODEL_REPORT.get("leave_one_event_out", {})
        if loo and "best_threshold" in loo:
            BEST_CSI_THR = float(loo["best_threshold"].get("thr", 0.65))
        print(f"Loaded model report: MIN_RAIN_3D={MIN_RAIN_3D}, BEST_CSI_THR={BEST_CSI_THR}")
    else:
        print(f"WARNING: Model report not found at {REPORT_PATH}")

    # 4. Load Data Status
    if os.path.exists(DATA_STATUS_PATH):
        with open(DATA_STATUS_PATH, "r") as f:
            DATA_STATUS = json.load(f)
    else:
        DATA_STATUS = {"is_synthetic": True, "note": "Status file missing; synthetic assumed."}

    # 5. Load Dataset & Zone Features
    if os.path.exists(DATASET_PATH):
        DATA_DF = pd.read_csv(DATASET_PATH)
        print(f"Loaded dataset: {len(DATA_DF):,} rows, {len(DATA_DF.columns)} columns")
        
        if os.path.exists(ZONE_FEATURES_PATH):
            with open(ZONE_FEATURES_PATH, "r") as f:
                ZONES_DATA = json.load(f)
        else:
            ZONES_DATA = load_or_generate_zone_features(DATA_DF)
    else:
        print(f"WARNING: Dataset file not found at {DATASET_PATH}")
        if os.path.exists(ZONE_FEATURES_PATH):
            with open(ZONE_FEATURES_PATH, "r") as f:
                ZONES_DATA = json.load(f)

# ---------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------
class PredictRequest(BaseModel):
    zone_id: Union[int, str]
    rainfall_10d: List[float] = Field(
        ...,
        description="List of exactly 10 rainfall values in mm from Day -9 to Today"
    )
    rain_max_1h_mm: Optional[float] = None

    @field_validator("rainfall_10d")
    def validate_rainfall_10d(cls, v):
        if len(v) != 10:
            raise ValueError(f"rainfall_10d must contain exactly 10 values, but got {len(v)}.")
        for i, val in enumerate(v):
            if val < 0.0 or val > 500.0:
                raise ValueError(f"Rainfall values must be between 0.0 and 500.0 mm. Day index {i} has value {val}.")
        return v

class PredictAllRequest(BaseModel):
    rainfall_10d: List[float] = Field(
        ...,
        description="List of exactly 10 rainfall values in mm from Day -9 to Today applied city-wide"
    )
    rain_max_1h_mm: Optional[float] = None

    @field_validator("rainfall_10d")
    def validate_rainfall_10d(cls, v):
        if len(v) != 10:
            raise ValueError(f"rainfall_10d must contain exactly 10 values, but got {len(v)}.")
        for i, val in enumerate(v):
            if val < 0.0 or val > 500.0:
                raise ValueError(f"Rainfall values must be between 0.0 and 500.0 mm. Day index {i} has value {val}.")
        return v

# ---------------------------------------------------------
# Core Prediction Logic
# ---------------------------------------------------------
def run_prediction_for_zone(zone_dict: Dict[str, Any], rainfall_10d: List[float], rain_max_1h_mm: Optional[float] = None) -> Dict[str, Any]:
    if MODEL is None or not FEATURES:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning model is not loaded or configured."
        )

    # 1. Derive rain features
    # rainfall_10d is ordered oldest -> newest: rainfall_10d[-1] is today
    rain_1d_mm = float(rainfall_10d[-1])
    rain_3d_mm = float(sum(rainfall_10d[-3:]))
    rain_7d_mm = float(sum(rainfall_10d[-7:]))

    derived_rain = {
        "rain_1d_mm": round(rain_1d_mm, 2),
        "rain_3d_mm": round(rain_3d_mm, 2),
        "rain_7d_mm": round(rain_7d_mm, 2),
    }
    if rain_max_1h_mm is not None:
        derived_rain["rain_max_1h_mm"] = round(float(rain_max_1h_mm), 2)

    # 2. Build feature vector dynamically from features.json
    feature_vector_dict = {}
    missing_features = []
    terrain = zone_dict.get("terrain_features", {})

    for feat in FEATURES:
        if feat in derived_rain:
            feature_vector_dict[feat] = derived_rain[feat]
        elif feat in terrain:
            feature_vector_dict[feat] = terrain[feat]
        elif feat == "rain_max_1h_mm":
            feature_vector_dict[feat] = 0.0
        else:
            missing_features.append(feat)

    if missing_features:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot construct feature vector: missing features {missing_features}"
        )

    df_row = pd.DataFrame([feature_vector_dict])[FEATURES]

    # 3. Model score
    raw_prob = float(MODEL.predict_proba(df_row)[:, 1][0])
    risk_score = round(raw_prob, 4)
    risk_band = calculate_risk_band(risk_score, BEST_CSI_THR)

    # 4. Feature contributions (SHAP / pred_contribs)
    booster = MODEL.get_booster()
    dmat = xgb.DMatrix(df_row)
    contribs = booster.predict(dmat, pred_contribs=True)[0]
    
    # Last entry is the bias term
    feat_contribs = {feat: round(float(c), 4) for feat, c in zip(FEATURES, contribs[:-1])}
    bias = round(float(contribs[-1]), 4)

    # Top 3 positive and top contributing features
    sorted_contribs = sorted(feat_contribs.items(), key=lambda kv: abs(kv[1]), reverse=True)
    top_3 = [{"feature": k, "contribution": v} for k, v in sorted_contribs[:3]]

    # 5. Check out-of-training-range
    out_of_range = rain_3d_mm < MIN_RAIN_3D
    warning_msg = (
        f"3-day rainfall ({rain_3d_mm:.1f} mm) is below the training threshold ({MIN_RAIN_3D} mm). "
        "The model was trained exclusively on wet days; predictions here represent low-rain extrapolations."
        if out_of_range else None
    )

    return {
        "zone_id": zone_dict.get("id"),
        "zone_name": zone_dict.get("name"),
        "lat": zone_dict.get("lat"),
        "lon": zone_dict.get("lon"),
        "flooded_ground_truth": zone_dict.get("flooded"),
        "matched_cell_id": zone_dict.get("matched_cell_id"),
        "distance_m": zone_dict.get("distance_m"),
        "risk_score": risk_score,
        "risk_band": risk_band,
        "threshold_used": BEST_CSI_THR,
        "out_of_training_range": out_of_range,
        "warning": warning_msg,
        "derived_rain": derived_rain,
        "features_sent": {k: round(float(v), 4) for k, v in feature_vector_dict.items()},
        "contributions": feat_contribs,
        "bias": bias,
        "top_contributions": top_3,
        "terrain_features": terrain
    }

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get("/api/health")
def get_health():
    return {
        "status": "ok",
        "model_loaded": MODEL is not None,
        "features_loaded": len(FEATURES) > 0,
        "dataset_loaded": DATA_DF is not None,
        "zone_count": len(ZONES_DATA),
        "is_synthetic": DATA_STATUS.get("is_synthetic", True)
    }

@app.get("/api/zones")
def get_zones():
    """
    Returns the 8 zones with original metadata plus nearest mock cell mapping and terrain features.
    """
    return {
        "zones": ZONES_DATA,
        "data_status": DATA_STATUS
    }

@app.post("/api/predict")
def predict(req: PredictRequest):
    """
    Predict flood risk for a specific zone with 10-day rainfall series.
    """
    target_zone = None
    for z in ZONES_DATA:
        if str(z.get("id")) == str(req.zone_id) or z.get("name") == str(req.zone_id):
            target_zone = z
            break
            
    if target_zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone with ID '{req.zone_id}' not found. Valid IDs: {[z['id'] for z in ZONES_DATA]}"
        )

    res = run_prediction_for_zone(target_zone, req.rainfall_10d, req.rain_max_1h_mm)
    return res

@app.post("/api/predict_all")
def predict_all(req: PredictAllRequest):
    """
    Apply city-wide 10-day rainfall series across all 8 zones.
    """
    if not ZONES_DATA:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Zones are not initialized.")
        
    results = [
        run_prediction_for_zone(z, req.rainfall_10d, req.rain_max_1h_mm)
        for z in ZONES_DATA
    ]
    return {
        "predictions": results,
        "rainfall_10d": req.rainfall_10d,
        "data_status": DATA_STATUS
    }

@app.get("/api/model_report")
def get_model_report():
    """
    Serves model_report.json generated during model training.
    """
    if not MODEL_REPORT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model report not found.")
    return MODEL_REPORT

@app.get("/api/data")
def get_data(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    flood_label: Optional[int] = Query(None, description="Filter by flood_label: 0 or 1"),
    date: Optional[str] = Query(None, description="Filter by exact date string YYYY-MM-DD"),
    ward: Optional[str] = Query(None, description="Filter by ward ID or name")
):
    """
    Server-side paginated, filterable rows of flood_dataset.csv.
    """
    if DATA_DF is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Dataset not loaded.")
        
    filtered = DATA_DF
    if flood_label is not None:
        filtered = filtered[filtered["flood_label"] == flood_label]
    if date:
        filtered = filtered[filtered["date"].astype(str).str.startswith(date)]
    if ward is not None and ward != "":
        try:
            w_int = int(ward)
            filtered = filtered[filtered["ward"] == w_int]
        except ValueError:
            filtered = filtered[filtered["ward"].astype(str) == ward]

    total_rows = len(filtered)
    total_pages = max(1, int(np.ceil(total_rows / page_size)))
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_slice = filtered.iloc[start_idx:end_idx].replace({np.nan: None})
    
    return {
        "total": total_rows,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "data_status": DATA_STATUS,
        "rows": page_slice.to_dict(orient="records")
    }

@app.get("/api/data/summary")
def get_data_summary():
    """
    Returns aggregate dataset statistics, label breakdowns, and per-column metrics.
    """
    if DATA_DF is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Dataset not loaded.")

    total_rows = int(len(DATA_DF))
    min_date = str(DATA_DF["date"].min())
    max_date = str(DATA_DF["date"].max())
    flood_rate = round(float(DATA_DF["flood_label"].mean()), 4) if "flood_label" in DATA_DF else 0.0
    positive_count = int(DATA_DF["flood_label"].sum()) if "flood_label" in DATA_DF else 0

    # Source breakdown
    source_counts = DATA_DF["label_source"].value_counts(dropna=False).to_dict() if "label_source" in DATA_DF else {}
    source_breakdown = {str(k): int(v) for k, v in source_counts.items()}

    # Confidence breakdown
    conf_counts = DATA_DF["label_confidence"].value_counts(dropna=False).to_dict() if "label_confidence" in DATA_DF else {}
    conf_breakdown = {str(k): int(v) for k, v in conf_counts.items()}

    # Per-column statistics
    column_stats = {}
    for col in DATA_DF.columns:
        series = DATA_DF[col]
        missing_count = int(series.isna().sum())
        stats: Dict[str, Any] = {
            "name": col,
            "missing": missing_count,
            "missing_pct": round(missing_count / max(total_rows, 1) * 100.0, 2),
            "dtype": str(series.dtype)
        }
        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            stats["min"] = round(float(valid.min()), 3) if len(valid) else None
            stats["max"] = round(float(valid.max()), 3) if len(valid) else None
            stats["mean"] = round(float(valid.mean()), 3) if len(valid) else None
        else:
            stats["unique_values"] = int(series.nunique())
        column_stats[col] = stats

    return {
        "row_count": total_rows,
        "date_range": {"min": min_date, "max": max_date},
        "flood_rate": flood_rate,
        "positives": positive_count,
        "label_source_breakdown": source_breakdown,
        "label_confidence_breakdown": conf_breakdown,
        "column_stats": column_stats,
        "data_status": DATA_STATUS
    }

@app.get("/api/data/columns")
def get_data_columns():
    """
    Column dictionary built directly from the Member 1 Dataset Specification document.
    """
    spec_columns = [
        { "name": "cell_id", "type": "integer", "unit": "id", "description": "Grid cell ID, stable in all files", "used_in_model": False, "priority": "MUST" },
        { "name": "date", "type": "string (ISO)", "unit": "YYYY-MM-DD", "description": "Calendar day described by the observation row", "used_in_model": False, "priority": "MUST" },
        { "name": "lat", "type": "float", "unit": "degrees N", "description": "Cell centroid latitude in WGS84 (EPSG:4326)", "used_in_model": False, "priority": "MUST" },
        { "name": "lon", "type": "float", "unit": "degrees E", "description": "Cell centroid longitude in WGS84 (EPSG:4326)", "used_in_model": False, "priority": "MUST" },
        { "name": "ward", "type": "text/int", "unit": "ward code", "description": "BBMP administrative ward containing centroid. Used for spatial CV.", "used_in_model": False, "priority": "MUST" },
        { "name": "rain_pixel_id", "type": "integer", "unit": "id", "description": "ID of gridded rainfall pixel supplying precipitation data", "used_in_model": False, "priority": "MUST" },
        { "name": "rain_1d_mm", "type": "float", "unit": "mm", "description": "Rainfall on day d (same-day accumulation)", "used_in_model": True, "priority": "MUST" },
        { "name": "rain_3d_mm", "type": "float", "unit": "mm", "description": "Rolling sum of rainfall on days d-2, d-1, and d", "used_in_model": True, "priority": "MUST" },
        { "name": "rain_7d_mm", "type": "float", "unit": "mm", "description": "Rolling sum of rainfall on days d-6 through d", "used_in_model": True, "priority": "MUST" },
        { "name": "rain_14d_mm", "type": "float", "unit": "mm", "description": "Rolling sum of rainfall on days d-13 through d", "used_in_model": False, "priority": "SHOULD" },
        { "name": "rain_30d_mm", "type": "float", "unit": "mm", "description": "Antecedent wetness rainfall rolling sum on days d-29 through d", "used_in_model": False, "priority": "SHOULD" },
        { "name": "rain_max_1h_mm", "type": "float", "unit": "mm/h", "description": "Peak 1-hour rainfall intensity on day d", "used_in_model": "rain_max_1h_mm" in FEATURES, "priority": "MAY" },
        { "name": "soil_moisture_pre", "type": "float", "unit": "m³/m³", "description": "ERA5-Land top-layer soil moisture on day d-1", "used_in_model": False, "priority": "MAY" },
        { "name": "elev_m", "type": "float", "unit": "metres", "description": "Mean digital elevation model (DEM) surface height in cell", "used_in_model": True, "priority": "MUST" },
        { "name": "slope_deg", "type": "float", "unit": "degrees", "description": "Mean terrain slope in degrees", "used_in_model": True, "priority": "MUST" },
        { "name": "twi", "type": "float", "unit": "index", "description": "Topographic Wetness Index ln(a/tan beta) - higher where water ponds", "used_in_model": True, "priority": "MUST" },
        { "name": "hand_m", "type": "float", "unit": "metres", "description": "Height Above Nearest Drainage - relative elevation above nearest drainage line", "used_in_model": "hand_m" in FEATURES, "priority": "MUST" },
        { "name": "flow_acc", "type": "float", "unit": "cells / km²", "description": "Upstream contributing catchment drainage accumulation area", "used_in_model": True, "priority": "MUST" },
        { "name": "imperv_frac", "type": "float", "unit": "fraction (0-1)", "description": "Built-up and paved impervious surface coverage fraction", "used_in_model": True, "priority": "MUST" },
        { "name": "dist_lake_m", "type": "float", "unit": "metres", "description": "Straight-line distance from centroid to nearest lake/kere boundary", "used_in_model": "dist_lake_m" in FEATURES, "priority": "MUST" },
        { "name": "dist_drain_m", "type": "float", "unit": "metres", "description": "Distance to nearest stormwater drain or rajakaluve channel", "used_in_model": True, "priority": "MUST" },
        { "name": "dist_road_m", "type": "float", "unit": "metres", "description": "Distance to nearest major arterial transport corridor", "used_in_model": True, "priority": "SHOULD" },
        { "name": "lakes_within_1km", "type": "integer", "unit": "count", "description": "Count of water bodies and lakes within 1 km radius", "used_in_model": True, "priority": "MUST" },
        { "name": "flood_label", "type": "binary (0/1)", "unit": "boolean", "description": "1 = flooding/waterlogging observed in cell on date d, 0 = no flooding observed", "used_in_model": False, "priority": "MUST" },
        { "name": "label_source", "type": "text", "unit": "category", "description": "Evidence origin: sar, hotspot_pdf, news, civic_report, none", "used_in_model": False, "priority": "MUST" },
        { "name": "label_confidence", "type": "text", "unit": "category", "description": "Confidence level in label: high, medium, low", "used_in_model": False, "priority": "MUST" },
        { "name": "event_id", "type": "text", "unit": "event code", "description": "Storm event identifier grouping contiguous event days", "used_in_model": False, "priority": "MUST" },
        { "name": "day_sampling_weight", "type": "float", "unit": "weight (>=1)", "description": "Inverse probability weight for non-event candidate days", "used_in_model": False, "priority": "MUST" },
    ]
    return {
        "columns": spec_columns,
        "features_in_active_model": FEATURES,
        "data_status": DATA_STATUS
    }

@app.get("/download/flood_dataset.csv")
def download_dataset():
    """
    Direct download of flood_dataset.csv.
    """
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset file not found.")
    return FileResponse(
        path=DATASET_PATH,
        filename="flood_dataset.csv",
        media_type="text/csv"
    )

# ---------------------------------------------------------
# Static Files & Documentation UI
# ---------------------------------------------------------
# Ensure docs directory exists
os.makedirs(DOCS_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=DOCS_DIR, html=True), name="docs")
