# N²M Flood Prediction Model — REST API Documentation

This document provides complete, definitive documentation for the asynchronous REST API powering the **N²M Flood Prediction Model**.

The API is implemented in Python 3.9+ using **FastAPI** and is served via **Uvicorn** at `http://127.0.0.1:8000`.

Interactive Swagger documentation is available locally at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:8000/openapi.json`

---

## 1. Global API Conventions

### Base URL
```
http://127.0.0.1:8000
```

### Content Type
All endpoints return responses formatted as `application/json` with UTF-8 character encoding.

### Cross-Origin Resource Sharing (CORS)
The API includes permissive CORS middleware allowing requests from local development servers (e.g. `http://127.0.0.1:5173`, `http://localhost:5173`).

### Common HTTP Status Codes
| Status Code | Description | Meaning |
|:---|:---|:---|
| **`200 OK`** | Success | Request succeeded; payload returned in body. |
| **`400 Bad Request`** | Client Error | Malformed parameters (e.g. invalid date string, illegal level filter). |
| **`404 Not Found`** | Not Found | Requested date not found in the historical replay dataset. |
| **`500 Internal Error`** | Server Error | Uncaught server exception or internal data processing failure. |

---

## 2. Endpoint Index

| Method | Endpoint | Category | Description |
|:---:|:---|:---:|:---|
| `GET` | [`/`](#1-service-information---get-) | Service Metadata | API health status, available routes, and active model description. |
| `GET` | [`/api/about`](#2-scientific-metadata--disclaimers---get-apiabout) | Documentation | Project overview, operational warnings, and PR-AUC validation stats. |
| `GET` | [`/api/dates`](#3-available-replay-dates---get-apidates) | Replay Index | Chronological list of all 24 available September 2022 replay dates. |
| `GET` | [`/api/risk`](#4-daily-susceptibility-rankings---get-apirisk) | Replay Data | Full ranked cell records for a selected date with optional level/limit filters. |
| `GET` | [`/api/risk/latest`](#5-latest-replay-date-risk---get-apirisklatest) | Replay Data | Ranked susceptibility records for the final available replay date. |
| `GET` | [`/api/summary`](#6-daily-statistical-summary---get-apisummary) | Replay Summary | Aggregated metrics, tier counts, score distributions, and top cell. |
| `GET` | [`/api/pipeline/status`](#7-live-pipeline-scaffolding-status---get-apipipelinestatus) | Scaffolding | Operational status and safety guards for experimental rainfall ingestion. |
| `GET` | [`/api/rainfall/latest`](#9-latest-retrieved-rainfall---get-apirainfalllatest) | Rainfall Ingestion | Actual retrieved daily precipitation from Open-Meteo, rolling features, and status. |
| `GET` | [`/api/rainfall/status`](#10-rainfall-provider-status---get-apirainfallstatus) | Rainfall Ingestion | External provider configuration, cache freshness, and spatial comparison notes. |
| `GET` | [`/api/telegram/status`](#11-telegram-bot-configuration-status---get-apitelegramstatus) | Demo Integration | Non-sensitive private bot configuration, mode, and authorized chats count. |
| `GET` | [`/api/telegram/demo-preview`](#8-telegram-demonstration-preview---get-apitelegramdemo-preview) | Demo Integration | In-memory formatted alert message preview with safety notices. |
| `POST` | [`/api/telegram/webhook`](#12-telegram-bot-webhook-handler---post-apitelegramwebhook) | Demo Integration | Ingests Telegram updates, checks authorization, and runs /start, /help, /status, /demo. |
| `POST` | [`/api/telegram/send-demo`](#13-trigger-private-telegram-demo-alert---post-apitelegramsend-demo) | Demo Integration | Dispatches a demonstration message to authorized private chat ID. |

---

## 3. Endpoint Reference

---

### 1. Service Information — `GET /`

Returns the operational status, API version, active model name, and a directory of available routes.

#### Request
- **Method**: `GET`
- **Path**: `/`
- **Parameters**: None

#### Response (`200 OK`)
```json
{
  "project": "Bengaluru Experimental Flood Susceptibility Model",
  "status": "operational",
  "available_routes": [
    "/api/about",
    "/api/dates",
    "/api/risk",
    "/api/risk/latest",
    "/api/summary",
    "/api/pipeline/status",
    "/api/telegram/demo-preview"
  ],
  "mode": "historical_replay",
  "model": "XGBoost Classifier (Holdout E2022_09)",
  "version": "1.0.0"
}
```

---

### 2. Scientific Metadata & Disclaimers — `GET /api/about`

Provides academic disclosures, operational warnings, feature inventories, and holdout validation metrics.

#### Request
- **Method**: `GET`
- **Path**: `/api/about`
- **Parameters**: None

#### Response (`200 OK`)
```json
{
  "project_title": "Bengaluru Experimental Flood Susceptibility Model",
  "description": "An experimental spatial ranking system prioritizing 3,026 Bengaluru grid cells by relative flood susceptibility based on terrain features and antecedent rainfall.",
  "nature_of_output": "Relative priority / susceptibility scores. Scores must NOT be presented as predicted flood probabilities.",
  "operational_warnings": [
    "This is NOT a flood forecast or early warning system.",
    "This is NOT an emergency management or life-safety alert system.",
    "The model is NOT validated or certified for operational civic deployment.",
    "Historical replay utilizes the dedicated September 2022 holdout model (flood_xgb_holdout_E2022_09.json).",
    "Do not substitute live weather feeds without complete distributional recalibration."
  ],
  "model_details": {
    "architecture": "XGBoost Classifier (binary:logistic)",
    "total_grid_cells": 3026,
    "feature_count": 18,
    "features": [
      "rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "rain_14d_mm", "rain_30d_mm",
      "rain_lag1_mm", "rain_lag2_mm", "rain_lag3_mm", "elev_m", "slope_deg",
      "twi", "hand_m", "flow_acc", "imperv_frac", "dist_lake_m",
      "dist_drain_m", "dist_road_m", "lakes_within_1km"
    ],
    "ranking_rule": "Rank-based per day (Top 150 High, Ranks 151-300 Moderate, Remaining None)",
    "historical_replay_model": "flood_xgb_holdout_E2022_09.json"
  },
  "validation_limitations": {
    "labelled_places_count": 10,
    "historical_events_count": 6,
    "spatial_resolution_km": 5.0,
    "holdout_event": "September 2022 (E2022_09)",
    "pr_auc": 0.0026,
    "random_chance_auc": 0.0013,
    "high_hit_rate_pct": 8.3,
    "high_random_baseline_pct": 5.0,
    "moderate_high_hit_rate_pct": 25.0,
    "moderate_high_random_baseline_pct": 9.9
  },
  "guidance_notes": [
    "Sparse label ground truth: Approximately 10 verified locations across 6 historical events.",
    "Spatial label assumption: Positive labels were assumed for neighboring cells (3x3 grid around reported points).",
    "Rainfall resolution limitation: CHIRPS daily ~5 km rainfall data cannot detect hyper-local, short-duration cloudbursts.",
    "Statistical interpretation: PR-AUC (0.0026 vs 0.0013 baseline) demonstrates ~2x lift over random chance, but remains very low in absolute terms.",
    "Indicative use only: Treat rankings as an exploratory research prototype."
  ]
}
```

---

### 3. Available Replay Dates — `GET /api/dates`

Returns the chronologically sorted sequence of all 24 available dates for the September 2022 holdout replay.

#### Request
- **Method**: `GET`
- **Path**: `/api/dates`
- **Parameters**: None

#### Response (`200 OK`)
```json
{
  "dates": [
    "2022-08-22", "2022-08-23", "2022-08-24", "2022-08-25",
    "2022-08-26", "2022-08-27", "2022-08-28", "2022-08-29",
    "2022-08-30", "2022-08-31", "2022-09-01", "2022-09-02",
    "2022-09-03", "2022-09-04", "2022-09-05", "2022-09-06",
    "2022-09-07", "2022-09-08", "2022-09-09", "2022-09-10",
    "2022-09-11", "2022-09-12", "2022-09-13", "2022-09-14"
  ],
  "total_dates": 24,
  "min_date": "2022-08-22",
  "max_date": "2022-09-14",
  "mode": "historical_replay"
}
```

---

### 4. Daily Susceptibility Rankings — `GET /api/risk`

Scores and returns the susceptibility ranking for all 3,026 cells on a selected replay date, with optional level filtering and limit controls.

#### Request
- **Method**: `GET`
- **Path**: `/api/risk`
- **Query Parameters**:
  - `date` (`string`, **required**): Date in `YYYY-MM-DD` format (e.g. `2022-09-08`).
  - `level` (`string`, *optional*): Case-insensitive level filter. Allowed values: `High`, `Moderate`, `None`.
  - `limit` (`integer`, *optional*): Maximum records to return ($\ge 1$).

#### Response (`200 OK`)
```json
{
  "date": "2022-09-08",
  "total_cells": 3026,
  "high_count": 150,
  "moderate_count": 150,
  "none_count": 2726,
  "mode": "historical_replay",
  "is_latest_replay": false,
  "is_live": false,
  "disclaimer": "EXPERIMENTAL RANKING ONLY. Scores indicate relative susceptibility, NOT flood probabilities.",
  "cells": [
    {
      "cell_id": 722,
      "date": "2022-09-08",
      "lat": 12.9234,
      "lon": 77.6841,
      "ward": 150,
      "score": 0.2191,
      "rank": 1,
      "level": "High"
    },
    {
      "cell_id": 783,
      "date": "2022-09-08",
      "lat": 12.9279,
      "lon": 77.6841,
      "ward": 150,
      "score": 0.2106,
      "rank": 2,
      "level": "High"
    }
  ]
}
```

#### Error Responses
- **`400 Bad Request`**: Malformed date string (e.g. `20220908` instead of `2022-09-08`) or invalid `level` value.
  ```json
  { "detail": "Date '20220908' is not in expected YYYY-MM-DD format." }
  ```
- **`404 Not Found`**: Date out of available replay range.
  ```json
  { "detail": "Date '2025-01-01' not found in historical replay dataset. Available range is 2022-08-22 to 2022-09-14." }
  ```

---

### 5. Latest Replay Date Risk — `GET /api/risk/latest`

Convenience route returning ranked risk records for the final available replay date (`2022-09-14`).

#### Request
- **Method**: `GET`
- **Path**: `/api/risk/latest`
- **Query Parameters**: Same optional `level` and `limit` parameters as `/api/risk`.

#### Response (`200 OK`)
Identical structure to `/api/risk`, with `is_latest_replay: true` and `date: "2022-09-14"`.

---

### 6. Daily Statistical Summary — `GET /api/summary`

Returns aggregated statistics, total cells scored, counts per tier, score range, and the top-ranked cell for a selected date.

#### Request
- **Method**: `GET`
- **Path**: `/api/summary`
- **Query Parameters**:
  - `date` (`string`, **required**): Date in `YYYY-MM-DD` format.

#### Response (`200 OK`)
```json
{
  "date": "2022-09-08",
  "total_cells_scored": 3026,
  "high_count": 150,
  "moderate_count": 150,
  "none_count": 2726,
  "top_ranked_cell": {
    "cell_id": 722,
    "ward": 150,
    "score": 0.2191,
    "rank": 1,
    "level": "High",
    "lat": 12.9234,
    "lon": 77.6841
  },
  "average_score": 0.0198,
  "min_score": 0.0001,
  "max_score": 0.2191,
  "data_mode": "historical_replay",
  "disclaimer": "EXPERIMENTAL RESEARCH SUMMARY. Ranks indicate relative spatial priority, not flood occurrence probabilities."
}
```

---

### 7. Live Pipeline Scaffolding Status — `GET /api/pipeline/status`

Inspects the operational status and safety boundaries of the experimental live rainfall ingestion scaffolding.

#### Request
- **Method**: `GET`
- **Path**: `/api/pipeline/status`
- **Parameters**: None

#### Response (`200 OK`)
```json
{
  "status": "disabled",
  "is_operational": false,
  "connected_to_alerts": false,
  "required_source": "CHIRPS Gridded Daily Rainfall (~5km, UCSB/CHG)",
  "required_features": [
    "rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "rain_14d_mm", "rain_30d_mm",
    "rain_lag1_mm", "rain_lag2_mm", "rain_lag3_mm"
  ],
  "static_mapping_file": "cell_pixel_map.csv",
  "static_features_file": "cells_static.csv",
  "compatibility_warning": "Do not substitute weather sources (e.g. Open-Meteo, IMD points) without re-evaluating feature distributions against the original training dataset.",
  "safety_rule": "Under no circumstances should this pipeline trigger public alerts."
}
```

---

### 8. Telegram Demonstration Preview — `GET /api/telegram/demo-preview`

Renders the formatted text of an automated spatial intelligence alert message in-memory without making live bot API calls.

#### Request
- **Method**: `GET`
- **Path**: `/api/telegram/demo-preview`
- **Query Parameters**:
  - `date` (`string`, **required**): Date in `YYYY-MM-DD` format.

#### Response (`200 OK`)
```json
{
  "date": "2022-09-08",
  "status": "preview_only",
  "enabled": false,
  "formatted_message": "⚠️ EXPERIMENTAL DEMO — HISTORICAL/SIMULATED SUSCEPTIBILITY RANKING.\nNOT A FLOOD FORECAST OR EMERGENCY WARNING.\nRelative susceptibility ranking only; not flood probabilities.\n--------------------------------------------------\n📅 Historical Replay Date: 2022-09-08\nMode: historical_replay\nGrid Cells Scored: 3026\n\n📊 Relative Alert Levels (Rank-Based Thresholds):\n  • High (Top 150 cells): 150\n  • Moderate (Ranks 151-300): 150\n  • None (Remaining): 2726\n\n📍 Highest Susceptibility Cell: Cell #722 (Ward 150), Score: 0.2191\n📈 Average Score: 0.0198\n--------------------------------------------------\nNotice: This demonstration uses historical data from September 2022. Never use this model for operational flood warning or life safety decisions.\n\nTop 5 Cells:\n  Rank #1: Cell 722 (Ward 150) - Score 0.2191\n  Rank #2: Cell 783 (Ward 150) - Score 0.2106\n  Rank #3: Cell 658 (Ward 174) - Score 0.2025\n  Rank #4: Cell 607 (Ward 150) - Score 0.1772\n  Rank #5: Cell 844 (Ward 150) - Score 0.1728",
  "note": "Telegram delivery is disabled by default. This preview renders formatting without sending any message."
}
```

---

### 9. Latest Retrieved Rainfall — `GET /api/rainfall/latest`

Retrieves actual observed precipitation and short-term numerical forecast context from Open-Meteo for Bengaluru. Normalizes daily sequences, computes 8 rolling-window features, and caches results.

#### Request
- **Method**: `GET`
- **Path**: `/api/rainfall/latest`
- **Query Parameters**:
  - `force_refresh` (`boolean`, *optional*, default: `false`): When `true`, bypasses cache and re-queries the remote provider.

#### Response (`200 OK` — Online / Cached)
```json
{
  "status": "success",
  "is_live": true,
  "cached": false,
  "fetch_timestamp": "2026-11-22T04:15:00.000000+00:00",
  "provider": {
    "name": "Open-Meteo Weather API",
    "api_endpoint": "https://api.open-meteo.com/v1/forecast",
    "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
    "spatial_resolution": "~0.1° (~11 km)",
    "temporal_resolution": "Daily aggregate (00:00 - 23:59 Asia/Kolkata)",
    "city_target": "Bengaluru, Karnataka, India",
    "coordinates": {
      "latitude": 12.9716,
      "longitude": 77.5946
    }
  },
  "summary": {
    "total_days_retrieved": 18,
    "past_observation_days": 15,
    "forecast_days": 3,
    "latest_daily_rain_mm": 0.0,
    "latest_7d_sum_mm": 4.2
  },
  "computed_features": {
    "reference_date": "2026-11-22",
    "rain_1d_mm": 0.0,
    "rain_3d_mm": 1.2,
    "rain_7d_mm": 4.2,
    "rain_14d_mm": 18.5,
    "rain_30d_mm": 52.0,
    "rain_lag1_mm": 0.0,
    "rain_lag2_mm": 1.2,
    "rain_lag3_mm": 0.0
  },
  "daily_series": [
    {
      "date": "2026-11-21",
      "precipitation_mm": 0.0,
      "category": "observation_historical",
      "label": "Retrieved Observation",
      "unit": "mm"
    },
    {
      "date": "2026-11-22",
      "precipitation_mm": 0.0,
      "category": "observation_current",
      "label": "Current Observation (Accumulating)",
      "unit": "mm"
    },
    {
      "date": "2026-11-23",
      "precipitation_mm": 2.1,
      "category": "forecast",
      "label": "Numerical Weather Forecast",
      "unit": "mm"
    }
  ],
  "disclaimer": "RESEARCH CONTEXT ONLY. Live retrieved meteorological data is for observational research and manual sensitivity demonstration. NOT an operational flood forecast."
}
```

#### Response (`200 OK` — Graceful Offline Degradation)
When running in an isolated environment or if the remote provider is unreachable:
```json
{
  "status": "offline",
  "is_live": false,
  "cached": false,
  "fetch_timestamp": "2026-11-22T04:15:00.000000+00:00",
  "provider": { ... },
  "error_details": {
    "error_type": "URLError",
    "message": "<urlopen error [Errno 8] nodename nor servname provided, or not known>",
    "diagnostic": "Backend is offline or remote API is unreachable. No synthetic data was generated."
  },
  "daily_series": [],
  "computed_features": null,
  "disclaimer": "OFFLINE DEMONSTRATION. External rainfall observation stream is currently unreachable. The platform does not fabricate unverified weather data."
}
```

---

### 10. Rainfall Provider Status — `GET /api/rainfall/status`

Returns lightweight connectivity status, cache freshness, and provider configuration.

#### Request
- **Method**: `GET`
- **Path**: `/api/rainfall/status`
- **Parameters**: None

#### Response (`200 OK`)
```json
{
  "status": "success",
  "is_live": true,
  "cached": true,
  "provider": {
    "name": "Open-Meteo Weather API",
    "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
    "spatial_resolution": "~0.1° (~11 km)",
    "coordinates": {
      "latitude": 12.9716,
      "longitude": 77.5946
    }
  },
  "summary": {
    "total_days_retrieved": 18,
    "latest_daily_rain_mm": 0.0,
    "latest_7d_sum_mm": 4.2
  }
}
```

---

### 11. Telegram Bot Configuration Status — `GET /api/telegram/status`

Returns non-sensitive configuration status for the private academic demonstration bot. **Tokens are never exposed in responses.**

#### Request
- **Method**: `GET`
- **Path**: `/api/telegram/status`
- **Parameters**: None

#### Response (`200 OK`)
```json
{
  "enabled": false,
  "configured": false,
  "token_configured": false,
  "bot_username": "N2M_Flood_Demo_Bot",
  "authorized_chats_count": 0,
  "mode": "private_academic_demo",
  "safety_rule": "Private demonstration only. Automated operational emergency alerts are strictly forbidden.",
  "available_commands": [
    "/start",
    "/help",
    "/status",
    "/demo [YYYY-MM-DD]"
  ]
}
```

---

### 12. Telegram Bot Webhook Handler — `POST /api/telegram/webhook`

Ingests incoming Telegram updates, validates that the sender's chat ID is in the authorized list, runs the requested command (`/start`, `/help`, `/status`, `/demo`), and dispatches replies.

#### Request
- **Method**: `POST`
- **Path**: `/api/telegram/webhook`
- **Body**: Standard Telegram update object:
```json
{
  "update_id": 10001,
  "message": {
    "message_id": 42,
    "from": { "id": 12345678, "first_name": "Evaluator" },
    "chat": { "id": 12345678, "type": "private" },
    "text": "/demo 2022-09-08"
  }
}
```

#### Response (`200 OK` — Authorized User)
```json
{
  "status": "success",
  "chat_id": "12345678",
  "command": "/demo",
  "response_text": "⚠️ EXPERIMENTAL DEMO — HISTORICAL/SIMULATED SUSCEPTIBILITY RANKING.\nNOT A FLOOD FORECAST OR EMERGENCY WARNING.\n...\n📅 Historical Replay Date: 2022-09-08\n..."
}
```

#### Response (`200 OK` — Unauthorized User)
```json
{
  "status": "unauthorized",
  "chat_id": "99999999",
  "response_text": "⛔ Access Restricted:\nThis bot is a private academic research prototype for the N²M Flood Prediction Model. Interaction is restricted to explicitly authorized project evaluators."
}
```

---

### 13. Trigger Private Telegram Demo Alert — `POST /api/telegram/send-demo`

Dispatches a formatted demonstration alert message for a selected replay date to an authorized evaluator's private chat.

#### Request
- **Method**: `POST`
- **Path**: `/api/telegram/send-demo`
- **Body**:
```json
{
  "date": "2022-09-08",
  "chat_id": null
}
```

#### Response (`200 OK`)
```json
{
  "sent": false,
  "chat_id": "null",
  "reason": "Telegram integration is disabled by default. Set TELEGRAM_ENABLED=true in .env to enable.",
  "error": null,
  "formatted_message": "⚠️ EXPERIMENTAL DEMO — HISTORICAL/SIMULATED SUSCEPTIBILITY RANKING.\nNOT A FLOOD FORECAST OR EMERGENCY WARNING.\n..."
}
```
