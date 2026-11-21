import os
import pytest
from pathlib import Path
import pandas as pd
from fastapi import HTTPException

from backend.config import settings
from backend.data_loader import data_loader, DataLoader
from backend.services.replay_service import replay_service
from backend.services.telegram_service import telegram_service
from backend.services.pipeline_scaffold import live_pipeline_scaffold
from backend.main import (
    get_root,
    get_about,
    get_dates,
    get_risk,
    get_latest_risk,
    get_summary,
    preview_telegram_demo,
    get_pipeline_status
)
from handover_member3.score_cells import load as load_model_assets, score_day

@pytest.fixture(scope="module", autouse=True)
def setup_data():
    """Ensure data loader is initialized before tests."""
    data_loader.load_all()

# -----------------------------------------------------------------------------
# 1. Supplied Handover Test & Baseline Reproduction
# -----------------------------------------------------------------------------

def test_supplied_handover_reproduction():
    """Validates that test_handover.py logic reproduces expected output exactly."""
    model, feats, rule = load_model_assets(
        model_path=str(settings.HOLDOUT_MODEL_PATH),
        features_path=str(settings.FEATURES_PATH),
        rule_path=str(settings.THRESHOLDS_PATH)
    )
    df = pd.read_parquet(settings.PARQUET_PATH)
    d = df[df["date"] == "2022-09-08"]
    assert len(d) == 3026

    out = score_day(d, model, feats, rule).set_index("cell_id")
    # Verify the specific check cells from test_handover.py
    check_cells = [555, 666, 847, 910, 977, 1444]
    for cid in check_cells:
        assert cid in out.index
    
    # Check alert levels
    counts = out["level"].value_counts()
    assert counts["High"] == 150
    assert counts["Moderate"] == 150
    assert counts["None"] == 2726

# -----------------------------------------------------------------------------
# 2. API Startup & Root Endpoint
# -----------------------------------------------------------------------------

def test_api_startup():
    """Verifies that the DataLoader initializes all assets correctly."""
    assert data_loader.is_initialized
    assert data_loader.model is not None
    assert len(data_loader.features) == 18
    assert data_loader.threshold_rules["high_top_k"] == 150
    assert data_loader.threshold_rules["moderate_top_k"] == 300
    assert len(data_loader.get_available_dates()) == 24

def test_root_endpoint():
    """Verifies GET / returns status, mode, and available routes."""
    res = get_root()
    assert res.status == "ok"
    assert res.mode == "historical_replay"
    assert "flood_xgb_holdout_E2022_09.json" in res.model
    assert "/" in res.available_routes
    assert "/api/about" in res.available_routes
    assert "/api/dates" in res.available_routes
    assert "/api/risk" in res.available_routes
    assert "/api/summary" in res.available_routes

# -----------------------------------------------------------------------------
# 3. About Endpoint & Limitations Verification
# -----------------------------------------------------------------------------

def test_about_endpoint_metadata_and_warnings():
    """Verifies GET /api/about clearly states limitations, warnings, and holdout metrics."""
    res = get_about()
    assert "experimental" in res.project_title.lower()
    assert "NOT be presented as predicted flood probabilities" in res.nature_of_output

    warnings_text = " ".join(res.operational_warnings)
    assert "NOT a flood forecast" in warnings_text
    assert "NOT an emergency management" in warnings_text
    assert "flood_xgb_holdout_E2022_09.json" in warnings_text

    stats = res.validation_limitations
    assert stats.labelled_places_count == 10
    assert stats.historical_events_count == 6
    assert stats.spatial_resolution_km == 5.0
    assert stats.pr_auc == 0.0026
    assert stats.random_chance_auc == 0.0013
    assert stats.high_hit_rate_pct == 8.3
    assert stats.high_random_baseline_pct == 5.0
    assert stats.moderate_high_hit_rate_pct == 25.0
    assert stats.moderate_high_random_baseline_pct == 9.9

# -----------------------------------------------------------------------------
# 4. Dates Retrieval Endpoint
# -----------------------------------------------------------------------------

def test_dates_retrieval():
    """Verifies GET /api/dates returns sorted, deduplicated dates."""
    res = get_dates()
    assert res.total_dates == 24
    assert res.min_date == "2022-08-22"
    assert res.max_date == "2022-09-14"
    assert len(res.dates) == len(set(res.dates))
    assert res.dates == sorted(res.dates)
    assert "2022-09-08" in res.dates

# -----------------------------------------------------------------------------
# 5. Risk Scoring & Rank Classification
# -----------------------------------------------------------------------------

def test_valid_replay_date_risk():
    """Verifies GET /api/risk returns complete, valid rankings for a historical date."""
    res = get_risk(date="2022-09-08")
    assert res["date"] == "2022-09-08"
    assert res["total_cells"] == 3026
    assert res["high_count"] == 150
    assert res["moderate_count"] == 150
    assert res["none_count"] == 2726
    assert res["mode"] == "historical_replay"
    assert len(res["cells"]) == 3026

    # Verify first row structure
    first_cell = res["cells"][0]
    expected_keys = {"cell_id", "date", "lat", "lon", "ward", "score", "rank", "level"}
    assert expected_keys.issubset(first_cell.keys())
    assert first_cell["rank"] == 1
    assert first_cell["level"] == "High"
    assert first_cell["date"] == "2022-09-08"

def test_risk_level_filtering_and_limit():
    """Verifies filtering by alert level and applying limit works correctly."""
    high_cells = get_risk(date="2022-09-08", level="High", limit=10)
    assert len(high_cells["cells"]) == 10
    for c in high_cells["cells"]:
        assert c["level"] == "High"
        assert c["rank"] <= 150

    mod_cells = get_risk(date="2022-09-08", level="Moderate")
    assert len(mod_cells["cells"]) == 150
    for c in mod_cells["cells"]:
        assert c["level"] == "Moderate"
        assert 151 <= c["rank"] <= 300

    none_cells = get_risk(date="2022-09-08", level="None")
    assert len(none_cells["cells"]) == 2726
    for c in none_cells["cells"]:
        assert c["level"] == "None"
        assert c["rank"] > 300

def test_risk_invalid_level_filter():
    """Verifies that an unknown level filter raises 400 Bad Request."""
    with pytest.raises(HTTPException) as exc_info:
        get_risk(date="2022-09-08", level="Catastrophic")
    assert exc_info.value.status_code == 400
    assert "Invalid level filter" in exc_info.value.detail

def test_risk_cell_ordering_and_ranks():
    """Verifies strict monotonic ascending rank order and descending score order."""
    res = get_risk(date="2022-09-08")
    cells = res["cells"]
    ranks = [c["rank"] for c in cells]
    scores = [c["score"] for c in cells]

    assert ranks == list(range(1, 3027))
    # Scores should be non-increasing
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1]

# -----------------------------------------------------------------------------
# 6. Latest Replay Date Endpoint
# -----------------------------------------------------------------------------

def test_latest_replay_date():
    """Verifies GET /api/risk/latest returns the most recent historical date."""
    res = get_latest_risk()
    assert res["date"] == "2022-09-14"
    assert res["is_latest_replay"] is True
    assert res["is_live"] is False
    assert res["mode"] == "historical_replay"
    assert res["total_cells"] == 3026

# -----------------------------------------------------------------------------
# 7. Error Handling: Invalid & Nonexistent Dates
# -----------------------------------------------------------------------------

def test_invalid_date_format():
    """Verifies malformed date strings return 400 Bad Request."""
    bad_dates = ["invalid", "2022-9-8", "2022/09/08", "2022-13-01", "2022-09-32"]
    for bad_dt in bad_dates:
        with pytest.raises(HTTPException) as exc_info:
            get_risk(date=bad_dt)
        assert exc_info.value.status_code == 400
        assert "Invalid" in exc_info.value.detail

def test_nonexistent_replay_date():
    """Verifies date outside replay dataset returns 404 Not Found."""
    with pytest.raises(HTTPException) as exc_info:
        get_risk(date="2023-09-08")
    assert exc_info.value.status_code == 404
    assert "not found in historical replay dataset" in exc_info.value.detail

# -----------------------------------------------------------------------------
# 8. Summary Endpoint
# -----------------------------------------------------------------------------

def test_summary_endpoint():
    """Verifies GET /api/summary returns accurate statistical aggregates."""
    res = get_summary(date="2022-09-08")
    assert res["date"] == "2022-09-08"
    assert res["total_cells_scored"] == 3026
    assert res["high_count"] == 150
    assert res["moderate_count"] == 150
    assert res["none_count"] == 2726
    assert res["data_mode"] == "historical_replay"

    top = res["top_ranked_cell"]
    assert top is not None
    assert top["rank"] == 1
    assert top["level"] == "High"
    assert top["score"] == res["max_score"]
    assert res["min_score"] <= res["average_score"] <= res["max_score"]

def test_summary_invalid_and_nonexistent_dates():
    """Verifies summary endpoint error handling."""
    with pytest.raises(HTTPException) as exc_bad:
        get_summary(date="not-a-date")
    assert exc_bad.value.status_code == 400

    with pytest.raises(HTTPException) as exc_404:
        get_summary(date="2021-01-01")
    assert exc_404.value.status_code == 404

# -----------------------------------------------------------------------------
# 9. Full Cell Coverage Across Dates
# -----------------------------------------------------------------------------

def test_full_cell_coverage_all_dates():
    """Verifies that every single date in the replay dataset has all 3026 cells."""
    dates = data_loader.get_available_dates()
    for dt in dates:
        day_data = data_loader.get_replay_data_for_date(dt)
        assert len(day_data) == 3026, f"Date {dt} has {len(day_data)} cells, expected 3026."

# -----------------------------------------------------------------------------
# 10. Data Integrity & Missing Feature Behavior
# -----------------------------------------------------------------------------

def test_missing_features_raises_value_error():
    """Verifies that score_day raises ValueError if required features are absent."""
    df_missing = pd.DataFrame({
        "cell_id": [1, 2],
        "rain_1d_mm": [10.0, 5.0]
        # Missing other 17 features
    })
    with pytest.raises(ValueError) as exc_info:
        score_day(
            df=df_missing,
            model=data_loader.model,
            feats=data_loader.features,
            rule=data_loader.threshold_rules
        )
    assert "Missing feature columns" in str(exc_info.value)

def test_model_loading_nonexistent_path():
    """Verifies that DataLoader raises FileNotFoundError when configured with nonexistent model path."""
    bad_cfg = settings.model_copy(update={"HOLDOUT_MODEL_PATH": Path("nonexistent_model.json")})
    bad_loader = DataLoader(bad_cfg)
    with pytest.raises(FileNotFoundError) as exc_info:
        bad_loader.load_all()
    assert "Holdout Model file not found" in str(exc_info.value)

# -----------------------------------------------------------------------------
# 11. Replay Isolation & Offline Execution
# -----------------------------------------------------------------------------

def test_replay_isolation_no_network():
    """
    Verifies that the historical replay service executes entirely from local files
    and cached data structures without making any external API or socket calls.
    """
    scored = replay_service.score_date("2022-08-25")
    assert len(scored) == 3026
    assert "level" in scored.columns
    assert "rank" in scored.columns
    assert "score" in scored.columns

# -----------------------------------------------------------------------------
# 12. Telegram Demo Sandbox & Safety
# -----------------------------------------------------------------------------

def test_telegram_demo_preview_and_safety():
    """Verifies Telegram demo formatting, disclaimers, and disabled-by-default behavior."""
    preview = preview_telegram_demo("2022-09-08")
    assert preview.enabled is False
    assert preview.status == "preview_only"
    assert "EXPERIMENTAL DEMO" in preview.formatted_message
    assert "NOT A FLOOD FORECAST OR EMERGENCY WARNING" in preview.formatted_message
    assert "Rank #1: Cell 722" in preview.formatted_message

    # Test send_demo_message when disabled
    summary = replay_service.get_summary("2022-09-08")
    send_result = telegram_service.send_demo_message(date_str="2022-09-08", summary=summary)
    assert send_result["sent"] is False
    assert "disabled by default" in send_result["reason"]

# -----------------------------------------------------------------------------
# 13. Live Rainfall Pipeline Scaffolding Safety
# -----------------------------------------------------------------------------

def test_live_rainfall_pipeline_scaffolding_safety():
    """Verifies that experimental live pipeline scaffolding is strictly disabled by default."""
    status = get_pipeline_status()
    assert status["status"] == "disabled"
    assert status["is_operational"] is False
    assert status["connected_to_alerts"] is False

    with pytest.raises(RuntimeError) as exc_info:
        live_pipeline_scaffold.ingest_and_build_features("2022-09-08")
    assert "DISABLED by default" in str(exc_info.value)

# -----------------------------------------------------------------------------
# 14. Full ASGI Pipeline Integration Test
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_full_asgi_request_pipeline():
    """Verifies that FastAPI processes HTTP requests through the ASGI pipeline."""
    import json
    from backend.main import app

    async def make_asgi_request(method: str, path: str):
        query_str = path.split("?")[1].encode() if "?" in path else b""
        raw_path = path.split("?")[0].encode()
        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path.split("?")[0],
            "raw_path": raw_path,
            "query_string": query_str,
            "headers": [(b"host", b"testserver")],
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 80),
        }
        body, status_code = [], None

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                body.append(message.get("body", b""))

        await app(scope, receive, send)
        resp_body = b"".join(body).decode()
        return status_code, json.loads(resp_body) if resp_body else {}

    code_root, data_root = await make_asgi_request("GET", "/")
    assert code_root == 200
    assert data_root["status"] == "ok"

    code_risk, data_risk = await make_asgi_request("GET", "/api/risk?date=2022-09-08&limit=3")
    assert code_risk == 200
    assert len(data_risk["cells"]) == 3

    code_400, data_400 = await make_asgi_request("GET", "/api/risk?date=bad-format")
    assert code_400 == 400

    code_404, data_404 = await make_asgi_request("GET", "/api/risk?date=2025-01-01")
    assert code_404 == 404

