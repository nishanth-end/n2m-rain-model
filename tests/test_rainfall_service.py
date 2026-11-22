"""
Automated Test Suite for Rainfall Ingestion Service
===================================================
Verifies Open-Meteo data ingestion, response validation, timestamp handling,
observation vs forecast classification, rolling-window calculations,
in-memory caching, graceful offline degradation, and API endpoints.
"""

import pytest
import time
from datetime import datetime, timedelta
from backend.main import app, get_latest_rainfall, get_rainfall_status
from backend.services.rainfall_service import RainfallIngestionService, rainfall_service
from backend.config import Settings


def make_mock_open_meteo_response(base_date_str: str = "2026-11-20", values=None):
    """Generates a synthetic Open-Meteo payload for deterministic unit testing."""
    base_dt = datetime.strptime(base_date_str, "%Y-%m-%d")
    dates = [(base_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(10)]
    if values is None:
        values = [0.0, 5.2, 12.4, 0.0, 8.5, 24.1, 4.0, 0.0, 1.2, 3.5]
    return {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "generationtime_ms": 0.12,
        "utc_offset_seconds": 19800,
        "timezone": "Asia/Kolkata",
        "timezone_abbreviation": "IST",
        "elevation": 920.0,
        "daily_units": {
            "time": "iso8601",
            "precipitation_sum": "mm"
        },
        "daily": {
            "time": dates,
            "precipitation_sum": values
        }
    }


class TestRainfallValidationAndNormalization:
    """Verifies schema validation and data integrity checks."""

    def test_valid_response_normalization(self):
        svc = RainfallIngestionService()
        raw = make_mock_open_meteo_response()
        records = svc.validate_and_normalize(raw)

        assert len(records) == 10
        assert records[0]["unit"] == "mm"
        assert all("date" in r and "precipitation_mm" in r for r in records)
        assert all("category" in r and "label" in r for r in records)
        # Check non-negative
        assert all(r["precipitation_mm"] >= 0.0 for r in records)

    def test_missing_daily_raises_value_error(self):
        svc = RainfallIngestionService()
        with pytest.raises(ValueError, match="'daily' object missing"):
            svc.validate_and_normalize({"latitude": 12.97})

    def test_length_mismatch_raises_value_error(self):
        svc = RainfallIngestionService()
        raw = {
            "daily": {
                "time": ["2026-11-20", "2026-11-21"],
                "precipitation_sum": [10.0]  # Only 1 item
            }
        }
        with pytest.raises(ValueError, match="Array length mismatch"):
            svc.validate_and_normalize(raw)

    def test_negative_precipitation_raises_value_error(self):
        svc = RainfallIngestionService()
        raw = {
            "daily": {
                "time": ["2026-11-20"],
                "precipitation_sum": [-5.0]
            }
        }
        with pytest.raises(ValueError, match="Negative precipitation"):
            svc.validate_and_normalize(raw)

    def test_invalid_date_format_raises_value_error(self):
        svc = RainfallIngestionService()
        raw = {
            "daily": {
                "time": ["20-11-2026"],  # Non ISO YYYY-MM-DD
                "precipitation_sum": [5.0]
            }
        }
        with pytest.raises(ValueError, match="Invalid date format"):
            svc.validate_and_normalize(raw)


class TestRollingFeatureCalculations:
    """Verifies rolling sum and antecedent lag feature generation."""

    def test_rolling_sums_and_lags(self):
        svc = RainfallIngestionService()
        # 7 known daily precipitation values
        series = [
            {"date": "2026-11-10", "precipitation_mm": 10.0, "category": "observation_historical"},
            {"date": "2026-11-11", "precipitation_mm": 20.0, "category": "observation_historical"},
            {"date": "2026-11-12", "precipitation_mm": 30.0, "category": "observation_historical"},
            {"date": "2026-11-13", "precipitation_mm": 40.0, "category": "observation_historical"},
            {"date": "2026-11-14", "precipitation_mm": 50.0, "category": "observation_historical"},
        ]

        # Calculate features targeting 2026-11-14 (index 4)
        feats = svc.compute_rolling_features(series, target_date="2026-11-14")

        assert feats["reference_date"] == "2026-11-14"
        assert feats["rain_1d_mm"] == 50.0
        assert feats["rain_lag1_mm"] == 40.0
        assert feats["rain_lag2_mm"] == 30.0
        assert feats["rain_lag3_mm"] == 20.0

        # 3-day sum: day 4 (50) + day 3 (40) + day 2 (30) = 120.0
        assert feats["rain_3d_mm"] == 120.0

        # 7-day sum (all 5 available = 10+20+30+40+50 = 150.0)
        assert feats["rain_7d_mm"] == 150.0


class TestCachingAndOfflineHandling:
    """Verifies in-memory caching TTL and graceful offline behavior without data fabrication."""

    def test_mock_fetch_and_caching(self):
        svc = RainfallIngestionService()
        mock_raw = make_mock_open_meteo_response()
        call_count = [0]

        def custom_fetch(url):
            call_count[0] += 1
            return mock_raw

        svc._custom_fetcher = custom_fetch

        # 1. First fetch
        res1 = svc.get_live_rainfall(force_refresh=False)
        assert res1["status"] == "success"
        assert res1["is_live"] is True
        assert res1["cached"] is False
        assert call_count[0] == 1

        # 2. Second fetch within TTL must hit cache
        res2 = svc.get_live_rainfall(force_refresh=False)
        assert res2["cached"] is True
        assert call_count[0] == 1  # No new network call

        # 3. Force refresh bypasses cache
        res3 = svc.get_live_rainfall(force_refresh=True)
        assert res3["cached"] is False
        assert call_count[0] == 2

    def test_graceful_offline_degradation_without_fabrication(self):
        svc = RainfallIngestionService()

        def failing_fetch(url):
            raise ConnectionError("Simulated DNS resolution failure / Offline sandbox")

        svc._custom_fetcher = failing_fetch

        res = svc.get_live_rainfall(force_refresh=True)
        assert res["status"] == "offline"
        assert res["is_live"] is False
        assert res["daily_series"] == []
        assert res["computed_features"] is None
        assert "error_details" in res
        assert "ConnectionError" in res["error_details"]["error_type"]
        assert "does not fabricate unverified weather data" in res["disclaimer"]


class TestRainfallAPIEndpoints:
    """Tests FastAPI HTTP endpoint responses."""

    def test_get_rainfall_latest_endpoint(self):
        # Direct function call
        res = get_latest_rainfall(force_refresh=False)
        assert "status" in res
        assert "provider" in res
        assert "name" in res["provider"]
        assert "coordinates" in res["provider"]
        assert res["provider"]["city_target"] == "Bengaluru, Karnataka, India"

    def test_get_rainfall_status_endpoint(self):
        res = get_rainfall_status()
        assert "status" in res
        assert "is_live" in res
        assert "provider" in res
        assert "name" in res["provider"]
