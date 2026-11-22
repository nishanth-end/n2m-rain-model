import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.config import settings
from backend.data_loader import data_loader
from backend.services.replay_service import replay_service
from backend.services.telegram_service import telegram_service
from backend.services.pipeline_scaffold import live_pipeline_scaffold
from backend.services.rainfall_service import rainfall_service
from backend.schemas.responses import (
    RootResponse,
    AboutResponse,
    DatesResponse,
    RiskResponse,
    SummaryResponse,
    TelegramPreviewResponse,
    ValidationStats
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bengaluru-flood-api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Eagerly initialize and verify data loader on startup
    logger.info("Initializing ML models, static cells, and historical replay dataset...")
    try:
        data_loader.load_all()
        logger.info(
            f"Successfully loaded {len(data_loader.get_available_dates())} replay dates "
            f"and {len(data_loader.features)} model features."
        )
    except Exception as e:
        logger.error(f"Critical error loading assets during startup: {e}")
        # Allow server to start so health/root diagnostics can report issue if needed
    yield
    logger.info("Shutting down API server.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description=(
        "Backend API serving historical replay flood susceptibility rankings for Bengaluru. "
        "Intended for experimental research and decoupled frontend consumption (React/Leaflet)."
    ),
    lifespan=lifespan
)

# Configure CORS for local development and deployed cloud frontends (e.g. Vercel)
cors_raw = settings.CORS_ORIGINS.strip()
if cors_raw and cors_raw != "*":
    allowed_origins = [orig.strip() for orig in cors_raw.split(",") if orig.strip()]
    for dev_orig in ("http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"):
        if dev_orig not in allowed_origins:
            allowed_origins.append(dev_orig)
    allow_credentials = True
    allow_origin_regex = r"^https:\/\/.*\.vercel\.app$"
elif cors_raw == "*":
    allowed_origins = ["*"]
    allow_credentials = False
    allow_origin_regex = None
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    allow_credentials = True
    allow_origin_regex = r"^https:\/\/.*\.vercel\.app$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.get(
    "/",
    response_model=RootResponse,
    summary="API Health and Routing Information",
    tags=["Root"]
)
def get_root():
    """Returns project metadata, service status, active mode, and available endpoints."""
    return RootResponse(
        project=settings.PROJECT_NAME,
        status="ok",
        available_routes=[
            "/",
            "/health",
            "/api/about",
            "/api/dates",
            "/api/risk",
            "/api/risk/latest",
            "/api/summary",
            "/api/telegram/demo-preview",
            "/api/telegram/status",
            "/api/telegram/webhook",
            "/api/telegram/send-demo",
            "/api/pipeline/status",
            "/api/rainfall/latest",
            "/api/rainfall/status",
        ],
        mode=settings.MODE,
        model="flood_xgb_holdout_E2022_09.json (September 2022 Holdout Replay Model)",
        version=settings.API_VERSION
    )

@app.get(
    "/health",
    summary="Lightweight Health Check Probe for Cloud Deployments",
    tags=["Root"]
)
def get_health():
    """Returns simple status payload for hosting platform load balancer probes (Render, Vercel, Docker)."""
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.API_VERSION}

@app.get(
    "/api/about",
    response_model=AboutResponse,
    summary="Model Metadata, Nature of Output, and Validation Limitations",
    tags=["Metadata"]
)
def get_about():
    """
    Exposes project limitations, model training context, and validation benchmarks.
    Clearly establishes that outputs are relative susceptibility rankings, NOT flood forecasts.
    """
    return AboutResponse(
        project_title="Bengaluru Experimental Flood Susceptibility Model",
        description=(
            "An experimental spatial ranking system prioritizing 3,026 Bengaluru grid cells "
            "by relative flood susceptibility based on terrain features and antecedent rainfall."
        ),
        nature_of_output=(
            "Relative priority / susceptibility scores. Scores must NOT be presented "
            "as predicted flood probabilities."
        ),
        operational_warnings=[
            "This is NOT a flood forecast or early warning system.",
            "This is NOT an emergency management or life-safety alert system.",
            "The model is NOT validated or certified for operational civic deployment.",
            "Historical replay utilizes the dedicated September 2022 holdout model (flood_xgb_holdout_E2022_09.json).",
            "Do not substitute live weather feeds without complete distributional recalibration."
        ],
        model_details={
            "architecture": "XGBoost Classifier (binary:logistic)",
            "total_grid_cells": settings.N_REFERENCE_CELLS,
            "feature_count": len(data_loader.features) if data_loader.features else 18,
            "features": data_loader.features if data_loader.features else [],
            "ranking_rule": "Rank-based per day (Top 150 High, Ranks 151-300 Moderate, Remaining None)",
            "historical_replay_model": "flood_xgb_holdout_E2022_09.json"
        },
        validation_limitations=ValidationStats(
            labelled_places_count=10,
            historical_events_count=6,
            spatial_resolution_km=5.0,
            holdout_event="September 2022 (E2022_09)",
            pr_auc=0.0026,
            random_chance_auc=0.0013,
            high_hit_rate_pct=8.3,
            high_random_baseline_pct=5.0,
            moderate_high_hit_rate_pct=25.0,
            moderate_high_random_baseline_pct=9.9
        ),
        guidance_notes=[
            "Sparse label ground truth: Approximately 10 verified locations across 6 historical events.",
            "Spatial label assumption: Positive labels were assumed for neighboring cells (3x3 grid around reported points).",
            "Rainfall resolution limitation: CHIRPS daily ~5 km rainfall data cannot detect hyper-local, short-duration cloudbursts.",
            "Statistical interpretation: PR-AUC (0.0026 vs 0.0013 baseline) demonstrates ~2x lift over random chance, but remains very low in absolute terms.",
            "Indicative use only: Treat rankings as an exploratory research prototype."
        ]
    )

@app.get(
    "/api/dates",
    response_model=DatesResponse,
    summary="List Available Historical Replay Dates",
    tags=["Replay"]
)
def get_dates():
    """Returns all available dates in the historical replay dataset, sorted chronologically."""
    try:
        res = replay_service.get_available_dates()
        return DatesResponse(**res)
    except Exception as e:
        logger.error(f"Error retrieving replay dates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to retrieve replay dates: {str(e)}"
        )

@app.get(
    "/api/risk",
    response_model=RiskResponse,
    summary="Get Susceptibility Rankings for a Specific Replay Date",
    tags=["Replay"]
)
def get_risk(
    date: str = Query(..., description="Replay date in YYYY-MM-DD format (e.g. 2022-09-08)"),
    level: Optional[str] = Query(None, description="Optional level filter: High, Moderate, or None"),
    limit: Optional[int] = Query(None, ge=1, description="Optional limit for returned cells")
):
    """
    Returns ranked flood susceptibility records for all cells (or filtered by level/limit)
    on the selected historical date using the holdout model.
    """
    lvl = level if isinstance(level, str) else None
    lmt = limit if isinstance(limit, int) else None
    try:
        return replay_service.get_risk_records(date_str=date, level=lvl, limit=lmt, is_latest=False)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Scoring error on date {date}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to score replay date '{date}': {str(e)}"
        )

@app.get(
    "/api/risk/latest",
    response_model=RiskResponse,
    summary="Get Susceptibility Rankings for the Latest Replay Date",
    tags=["Replay"]
)
def get_latest_risk(
    level: Optional[str] = Query(None, description="Optional level filter: High, Moderate, or None"),
    limit: Optional[int] = Query(None, ge=1, description="Optional limit for returned cells")
):
    """
    Returns susceptibility rankings for the most recent date available in the historical replay dataset.
    Explicitly flagged as historical replay data, NOT live data.
    """
    lvl = level if isinstance(level, str) else None
    lmt = limit if isinstance(limit, int) else None
    try:
        return replay_service.get_latest_risk(level=lvl, limit=lmt)
    except Exception as e:
        logger.error(f"Error retrieving latest replay risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest replay date: {str(e)}"
        )

@app.get(
    "/api/summary",
    response_model=SummaryResponse,
    summary="Get Statistical Summary for a Replay Date",
    tags=["Replay"]
)
def get_summary(
    date: str = Query(..., description="Replay date in YYYY-MM-DD format (e.g. 2022-09-08)")
):
    """
    Returns aggregated metrics for a replay date: total cells scored, count per alert level,
    highest susceptibility cell, and average score.
    """
    try:
        return replay_service.get_summary(date_str=date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Summary computation error on date {date}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary for date '{date}': {str(e)}"
        )

@app.get(
    "/api/telegram/demo-preview",
    response_model=TelegramPreviewResponse,
    summary="Preview Telegram Demonstration Message Formatting",
    tags=["Telegram Demo"]
)
def preview_telegram_demo(
    date: str = Query(..., description="Replay date in YYYY-MM-DD format to preview")
):
    """
    Renders the exact formatted text of a Telegram demonstration message without making network calls.
    Allows developers to verify message content and prominent experimental disclaimers.
    """
    try:
        summary = replay_service.get_summary(date_str=date)
        risk = replay_service.get_risk_records(date_str=date, limit=5)
        formatted = telegram_service.format_demo_message(
            date_str=date,
            summary=summary,
            top_cells=risk["cells"]
        )
        return TelegramPreviewResponse(
            date=date,
            status="preview_only",
            enabled=settings.TELEGRAM_ENABLED,
            formatted_message=formatted,
            note="Telegram delivery is disabled by default. This preview renders formatting without sending any message."
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

class TelegramSendDemoRequest(BaseModel):
    date: str = Field("2022-09-08", description="Replay date in YYYY-MM-DD format")
    chat_id: Optional[str] = Field(None, description="Optional target authorized chat ID")

@app.get(
    "/api/telegram/status",
    summary="Get Private Demonstration Bot Configuration Status",
    tags=["Telegram Demo"]
)
def get_telegram_status():
    """Returns safe, non-sensitive configuration status for the demonstration bot."""
    return telegram_service.get_public_status()

@app.post(
    "/api/telegram/webhook",
    summary="Handle Incoming Telegram Update for Private Demo Bot",
    tags=["Telegram Demo"]
)
def handle_telegram_webhook(update: Dict[str, Any]):
    """Processes incoming Telegram updates and dispatches bot commands (/start, /help, /status, /demo)."""
    def replay_fn(d_str):
        summary = replay_service.get_summary(date_str=d_str)
        risk = replay_service.get_risk_records(date_str=d_str, limit=5)
        return summary, risk["cells"]

    rf_status = rainfall_service.get_live_rainfall(force_refresh=False)
    result = telegram_service.process_incoming_update(
        update=update,
        replay_service_fn=replay_fn,
        rainfall_status=rf_status
    )
    if settings.TELEGRAM_ENABLED and result.get("status") in ("success", "unauthorized"):
        cid = result.get("chat_id")
        text = result.get("response_text")
        if cid and text:
            telegram_service.dispatch_telegram_message(chat_id=cid, text=text)

    return result

@app.post(
    "/api/telegram/send-demo",
    summary="Trigger Dispatch of a Private Demonstration Alert Message",
    tags=["Telegram Demo"]
)
def send_telegram_demo(req: TelegramSendDemoRequest):
    """Dispatches a demonstration alert message to an authorized tester."""
    try:
        summary = replay_service.get_summary(date_str=req.date)
        risk = replay_service.get_risk_records(date_str=req.date, limit=5)
        formatted = telegram_service.format_demo_message(
            date_str=req.date,
            summary=summary,
            top_cells=risk["cells"]
        )
        target_chat = req.chat_id or settings.TELEGRAM_CHAT_ID
        clean_target = str(target_chat or "").strip().strip('"').strip("'")
        if not clean_target:
            return {
                "sent": False,
                "status": "missing_target_chat",
                "reason": "No target chat ID configured. Set TELEGRAM_CHAT_ID in Render Environment Variables (or .env locally) or provide chat_id in request.",
                "formatted_message": formatted
            }

        dispatch_res = telegram_service.dispatch_telegram_message(
            chat_id=clean_target,
            text=formatted
        )
        return {
            "sent": dispatch_res.get("sent", False),
            "chat_id": "[AUTHORIZED_CHAT_REDACTED]" if dispatch_res.get("sent") else clean_target,
            "reason": dispatch_res.get("reason"),
            "error": dispatch_res.get("error"),
            "formatted_message": formatted
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get(
    "/api/pipeline/status",
    summary="Status of Experimental Rainfall Ingestion Scaffolding",
    tags=["Pipeline Scaffolding"]
)
def get_pipeline_status():
    """Returns the operational and isolation status of experimental rainfall ingestion scaffolding."""
    return live_pipeline_scaffold.get_pipeline_status()

@app.get(
    "/api/rainfall/latest",
    summary="Get Latest Retrieved Rainfall Context for Bengaluru",
    tags=["Rainfall Ingestion"]
)
def get_latest_rainfall(
    force_refresh: bool = Query(False, description="Bypass cache and force immediate provider fetch")
):
    """
    Fetches actual observed and short-term forecast rainfall data from Open-Meteo for Bengaluru.
    Returns normalized daily series, computed rolling features, and scientific metadata.
    """
    return rainfall_service.get_live_rainfall(force_refresh=force_refresh)

@app.get(
    "/api/rainfall/status",
    summary="Get Rainfall Ingestion Provider Status & Provenance",
    tags=["Rainfall Ingestion"]
)
def get_rainfall_status():
    """Returns configuration and metadata for the external rainfall observation provider."""
    live_data = rainfall_service.get_live_rainfall(force_refresh=False)
    return {
        "status": live_data.get("status", "unknown"),
        "is_live": live_data.get("is_live", False),
        "cached": live_data.get("cached", False),
        "provider": live_data.get("provider", {}),
        "summary": live_data.get("summary", {})
    }
