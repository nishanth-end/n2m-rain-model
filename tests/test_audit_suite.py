"""
Exhaustive Audit Test Suite for N²M Flood Prediction Model
Validates the complete historical replay sequence (all 24 dates),
3,026-cell hydrological mesh, spatial integrity, attribute schemas,
filtering, ranking monotonicity, search stability, and safety disclosures.
"""

import pytest
from fastapi import HTTPException
from backend.data_loader import data_loader
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

TOTAL_CELLS = 3026
HIGH_COUNT = 150
MODERATE_COUNT = 150
BASELINE_COUNT = 2726

BENGALURU_LAT_BOUNDS = (12.80, 13.25)
BENGALURU_LON_BOUNDS = (77.40, 77.85)

EXPECTED_DATES = [
    "2022-08-22", "2022-08-23", "2022-08-24", "2022-08-25",
    "2022-08-26", "2022-08-27", "2022-08-28", "2022-08-29",
    "2022-08-30", "2022-08-31", "2022-09-01", "2022-09-02",
    "2022-09-03", "2022-09-04", "2022-09-05", "2022-09-06",
    "2022-09-07", "2022-09-08", "2022-09-09", "2022-09-10",
    "2022-09-11", "2022-09-12", "2022-09-13", "2022-09-14",
]


@pytest.fixture(scope="module", autouse=True)
def setup_data():
    """Ensure data loader is initialized before tests."""
    data_loader.load_all()


class TestFullSequenceAudit:
    """Verifies that all 24 historical replay dates are present and adhere to data invariants."""

    def test_all_24_dates_present_in_dates_endpoint(self):
        data = get_dates()
        assert data.total_dates == 24
        assert data.dates == EXPECTED_DATES
        assert data.min_date == "2022-08-22"
        assert data.max_date == "2022-09-14"
        assert data.mode == "historical_replay"

    @pytest.mark.parametrize("date_str", EXPECTED_DATES)
    def test_daily_replay_invariants_and_spatial_mesh(self, date_str):
        """Audits every single day in the September 2022 holdout replay."""
        resp = get_risk(date=date_str, level=None, limit=None)

        assert resp["date"] == date_str
        assert resp["total_cells"] == TOTAL_CELLS
        assert len(resp["cells"]) == TOTAL_CELLS

        cells = resp["cells"]

        # Check ranking monotonicity
        ranks = [c["rank"] for c in cells]
        assert ranks == list(range(1, TOTAL_CELLS + 1)), f"Ranks on {date_str} must be 1..{TOTAL_CELLS}"

        # Check score descending order
        scores = [c["score"] for c in cells]
        assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1)), f"Scores on {date_str} must descend"

        # Check tier counts
        high_cells = [c for c in cells if c["level"] == "High"]
        mod_cells = [c for c in cells if c["level"] == "Moderate"]
        none_cells = [c for c in cells if c["level"] == "None"]

        assert len(high_cells) == HIGH_COUNT, f"High count on {date_str} must be {HIGH_COUNT}"
        assert len(mod_cells) == MODERATE_COUNT, f"Moderate count on {date_str} must be {MODERATE_COUNT}"
        assert len(none_cells) == BASELINE_COUNT, f"Baseline count on {date_str} must be {BASELINE_COUNT}"

        # Check geographic boundaries and schema fields on sample of cells
        for c in (cells[0], cells[149], cells[299], cells[-1]):
            assert BENGALURU_LAT_BOUNDS[0] <= c["lat"] <= BENGALURU_LAT_BOUNDS[1]
            assert BENGALURU_LON_BOUNDS[0] <= c["lon"] <= BENGALURU_LON_BOUNDS[1]
            assert 0.0 <= c["score"] <= 1.0
            assert "cell_id" in c
            assert "ward" in c


class TestFilteringAndSearchIntegrity:
    """Tests query parameter filtering, limits, and cell search integrity."""

    def test_filter_high_tier(self):
        resp = get_risk(date="2022-09-08", level="High", limit=None)
        assert len(resp["cells"]) == HIGH_COUNT
        assert resp["high_count"] == HIGH_COUNT
        assert all(c["level"] == "High" for c in resp["cells"])
        assert resp["cells"][0]["rank"] == 1
        assert resp["cells"][-1]["rank"] == HIGH_COUNT

    def test_filter_moderate_tier(self):
        resp = get_risk(date="2022-09-08", level="Moderate", limit=None)
        assert len(resp["cells"]) == MODERATE_COUNT
        assert resp["moderate_count"] == MODERATE_COUNT
        assert all(c["level"] == "Moderate" for c in resp["cells"])
        assert resp["cells"][0]["rank"] == HIGH_COUNT + 1
        assert resp["cells"][-1]["rank"] == HIGH_COUNT + MODERATE_COUNT

    def test_filter_none_tier(self):
        resp = get_risk(date="2022-09-08", level="None", limit=None)
        assert len(resp["cells"]) == BASELINE_COUNT
        assert resp["none_count"] == BASELINE_COUNT
        assert all(c["level"] == "None" for c in resp["cells"])

    def test_filter_with_limit(self):
        resp = get_risk(date="2022-09-08", level="High", limit=15)
        assert len(resp["cells"]) == 15
        assert resp["cells"][0]["rank"] == 1
        assert resp["cells"][-1]["rank"] == 15

    def test_target_cell_722_across_dates(self):
        """Cell 722 is a key benchmark cell in the Eastern corridor. Verify existence and stability."""
        for test_date in ["2022-08-25", "2022-09-05", "2022-09-08", "2022-09-14"]:
            resp = get_risk(date=test_date, level=None, limit=None)
            matching = [c for c in resp["cells"] if c["cell_id"] == 722]
            assert len(matching) == 1, f"Cell 722 must exist exactly once on {test_date}"
            c722 = matching[0]
            assert c722["cell_id"] == 722
            assert BENGALURU_LAT_BOUNDS[0] <= c722["lat"] <= BENGALURU_LAT_BOUNDS[1]
            assert BENGALURU_LON_BOUNDS[0] <= c722["lon"] <= BENGALURU_LON_BOUNDS[1]
            assert c722["rank"] >= 1
            assert c722["level"] in ["High", "Moderate", "None"]


class TestSummaryAndMetadataEndpoints:
    """Verifies summary statistics, pipeline status, and scientific metadata."""

    def test_summary_statistics_payload(self):
        resp = get_summary(date="2022-09-08")
        assert resp["date"] == "2022-09-08"
        assert resp["total_cells_scored"] == TOTAL_CELLS
        assert resp["high_count"] == HIGH_COUNT
        assert resp["moderate_count"] == MODERATE_COUNT
        assert resp["none_count"] == BASELINE_COUNT
        assert resp["max_score"] >= resp["average_score"]
        assert resp["top_ranked_cell"]["rank"] == 1

    def test_about_endpoint_disclaimers(self):
        resp = get_about()
        assert resp.project_title == "Bengaluru Experimental Flood Susceptibility Model"
        assert "not be presented as predicted flood probabilities" in resp.nature_of_output.lower()
        assert resp.validation_limitations.holdout_event == "September 2022 (E2022_09)"
        assert resp.validation_limitations.pr_auc == 0.0026

    def test_pipeline_status_reporting(self):
        resp = get_pipeline_status()
        assert resp["status"] == "disabled"
        assert resp["is_operational"] is False
        assert resp["connected_to_alerts"] is False
        assert "CHIRPS" in resp["required_source"]
        assert "safety_rule" in resp

    def test_telegram_demo_preview_safety(self):
        resp = preview_telegram_demo(date="2022-09-08")
        assert resp.date == "2022-09-08"
        assert resp.enabled is False
        assert "preview_only" in resp.status
        assert "EXPERIMENTAL DEMO" in resp.formatted_message
        assert "not a flood forecast" in resp.formatted_message.lower()


class TestErrorHandlingAndValidation:
    """Verifies graceful HTTP errors for malformed inputs."""

    def test_invalid_date_format_400(self):
        with pytest.raises(HTTPException) as exc:
            get_risk(date="20220908", level=None, limit=None)
        assert exc.value.status_code == 400
        assert "YYYY-MM-DD" in exc.value.detail

    def test_out_of_range_date_404(self):
        with pytest.raises(HTTPException) as exc:
            get_risk(date="2025-01-01", level=None, limit=None)
        assert exc.value.status_code == 404
        assert "not found in historical replay dataset" in exc.value.detail

    def test_invalid_level_filter_400(self):
        with pytest.raises(HTTPException) as exc:
            get_risk(date="2022-09-08", level="Critical", limit=None)
        assert exc.value.status_code == 400
        assert "Invalid level" in exc.value.detail
