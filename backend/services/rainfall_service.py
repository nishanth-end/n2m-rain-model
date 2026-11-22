"""
Rainfall Ingestion Service
==========================
Handles external rainfall observation and forecast retrieval for Bengaluru.
Integrates Open-Meteo REST API data as research context for the frontend.

CRITICAL RESEARCH GUARDRAILS:
1. Live retrieved rainfall is for meteorological context and manual simulation experimentation.
2. It must NEVER trigger automated civic alarms or operational flood warnings.
3. Observations and numerical weather forecasts are explicitly labeled.
4. If the provider is unreachable, returns structured diagnostic status without fabricating fake numbers.
"""

import time
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from backend.config import Settings, settings

logger = logging.getLogger(__name__)


class RainfallIngestionService:
    """
    Manages live rainfall retrieval, validation, rolling-window calculations,
    and in-memory caching for Bengaluru coordinates.
    """

    def __init__(self, cfg: Settings = settings):
        self.cfg = cfg
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: float = 0.0
        self._custom_fetcher = None  # Hook for deterministic unit testing

    def _get_kolkata_today(self) -> str:
        """Returns today's date string in Asia/Kolkata timezone (UTC+5:30)."""
        kolkata_offset = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(kolkata_offset).strftime("%Y-%m-%d")

    def _build_request_url(self, past_days: int = 14, forecast_days: int = 3) -> str:
        """Constructs the Open-Meteo REST API URL."""
        base = self.cfg.RAINFALL_API_URL
        params = (
            f"?latitude={self.cfg.RAINFALL_CITY_LAT}"
            f"&longitude={self.cfg.RAINFALL_CITY_LON}"
            f"&daily=precipitation_sum"
            f"&timezone={urllib.parse_quote(self.cfg.RAINFALL_TIMEZONE) if hasattr(urllib, 'parse_quote') else 'Asia%2FKolkata'}"
            f"&past_days={past_days}"
            f"&forecast_days={forecast_days}"
        )
        return f"{base}{params}"

    def _execute_http_fetch(self, url: str) -> Dict[str, Any]:
        """Executes an HTTP GET request with timeout and User-Agent headers."""
        if self._custom_fetcher:
            return self._custom_fetcher(url)

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "N2M-Flood-Prediction-Model/1.0 (Academic Research; Bengaluru, India)"
            }
        )
        with urllib.request.urlopen(req, timeout=self.cfg.RAINFALL_TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise RuntimeError(f"Provider returned HTTP {response.status}")
            raw_bytes = response.read()
            return json.loads(raw_bytes.decode("utf-8"))

    def validate_and_normalize(self, raw_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validates the raw response structure and normalizes daily values into
        structured records with distinct observation vs. forecast classifications.
        """
        daily = raw_json.get("daily")
        if not isinstance(daily, dict):
            raise ValueError("Malformed response: 'daily' object missing.")

        dates = daily.get("time")
        precip = daily.get("precipitation_sum")

        if not isinstance(dates, list) or not isinstance(precip, list):
            raise ValueError("Malformed response: 'time' or 'precipitation_sum' array missing.")

        if len(dates) != len(precip):
            raise ValueError(f"Array length mismatch: {len(dates)} dates vs {len(precip)} precipitation values.")

        today_str = self._get_kolkata_today()
        records: List[Dict[str, Any]] = []

        for d_str, p_val in zip(dates, precip):
            # Validate date string format
            try:
                datetime.strptime(d_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format '{d_str}' in response.")

            # Validate precipitation value
            val = 0.0 if p_val is None else float(p_val)
            if val < 0.0:
                raise ValueError(f"Negative precipitation value {val} on date {d_str}.")

            # Explicit classification
            if d_str < today_str:
                category = "observation_historical"
                label = "Retrieved Observation"
            elif d_str == today_str:
                category = "observation_current"
                label = "Current Observation (Accumulating)"
            else:
                category = "forecast"
                label = "Numerical Weather Forecast"

            records.append({
                "date": d_str,
                "precipitation_mm": round(val, 2),
                "category": category,
                "label": label,
                "unit": "mm"
            })

        return records

    def compute_rolling_features(self, series: List[Dict[str, Any]], target_date: Optional[str] = None) -> Dict[str, float]:
        """
        Computes the standard 8 precipitation model features from a series of daily records.
        If target_date is not specified, uses the latest observed date (date <= today).
        """
        if not series:
            return {}

        today_str = self._get_kolkata_today()
        # Find index of target date or latest observed date
        dates = [r["date"] for r in series]

        if target_date and target_date in dates:
            target_idx = dates.index(target_date)
        else:
            # Default to latest non-forecast date
            valid_indices = [i for i, r in enumerate(series) if r["date"] <= today_str]
            target_idx = valid_indices[-1] if valid_indices else len(series) - 1

        target_record = series[target_idx]
        val_at = lambda idx: series[idx]["precipitation_mm"] if 0 <= idx < len(series) else 0.0

        p1 = val_at(target_idx)
        p_lag1 = val_at(target_idx - 1)
        p_lag2 = val_at(target_idx - 2)
        p_lag3 = val_at(target_idx - 3)

        # 3-day sum (target + previous 2)
        p3 = sum(val_at(target_idx - i) for i in range(3))
        # 7-day sum (target + previous 6)
        p7 = sum(val_at(target_idx - i) for i in range(7))
        # 14-day sum (target + previous 13)
        p14 = sum(val_at(target_idx - i) for i in range(14))
        # 30-day sum (target + previous 29)
        p30 = sum(val_at(target_idx - i) for i in range(30))

        return {
            "reference_date": target_record["date"],
            "rain_1d_mm": round(p1, 2),
            "rain_3d_mm": round(p3, 2),
            "rain_7d_mm": round(p7, 2),
            "rain_14d_mm": round(p14, 2),
            "rain_30d_mm": round(p30, 2),
            "rain_lag1_mm": round(p_lag1, 2),
            "rain_lag2_mm": round(p_lag2, 2),
            "rain_lag3_mm": round(p_lag3, 2)
        }

    def get_live_rainfall(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Returns live rainfall context with provider metadata, series records,
        rolling feature metrics, and caching.
        """
        now = time.time()
        is_cache_valid = (
            not force_refresh
            and self._cache is not None
            and (now - self._cache_timestamp) < self.cfg.RAINFALL_CACHE_TTL_SECONDS
        )

        if is_cache_valid:
            cached_data = dict(self._cache)
            cached_data["cached"] = True
            cached_data["cache_age_seconds"] = round(now - self._cache_timestamp, 1)
            return cached_data

        provider_info = {
            "name": self.cfg.RAINFALL_PROVIDER_NAME,
            "api_endpoint": self.cfg.RAINFALL_API_URL,
            "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "spatial_resolution": "~0.1° (~11 km)",
            "temporal_resolution": "Daily aggregate (00:00 - 23:59 Asia/Kolkata)",
            "city_target": "Bengaluru, Karnataka, India",
            "coordinates": {
                "latitude": self.cfg.RAINFALL_CITY_LAT,
                "longitude": self.cfg.RAINFALL_CITY_LON
            },
            "comparison_notes": (
                "Open-Meteo uses ~11 km global reanalysis/NWP models. The N²M historical training "
                "baseline used CHIRPS ~5.3 km satellite-gauge data. Retrieved data serves as live "
                "meteorological research context and cannot replace CHIRPS without recalibration."
            )
        }

        url = self._build_request_url(past_days=14, forecast_days=3)

        try:
            raw_data = self._execute_http_fetch(url)
            records = self.validate_and_normalize(raw_data)
            features = self.compute_rolling_features(records)

            result = {
                "status": "success",
                "is_live": True,
                "cached": False,
                "fetch_timestamp": datetime.now(timezone.utc).isoformat(),
                "provider": provider_info,
                "summary": {
                    "total_days_retrieved": len(records),
                    "past_observation_days": len([r for r in records if "observation" in r["category"]]),
                    "forecast_days": len([r for r in records if r["category"] == "forecast"]),
                    "latest_daily_rain_mm": features.get("rain_1d_mm", 0.0),
                    "latest_7d_sum_mm": features.get("rain_7d_mm", 0.0)
                },
                "computed_features": features,
                "daily_series": records,
                "disclaimer": (
                    "RESEARCH CONTEXT ONLY. Live retrieved meteorological data is for observational "
                    "research and manual sensitivity demonstration. NOT an operational flood forecast."
                )
            }

            self._cache = result
            self._cache_timestamp = now
            return result

        except Exception as e:
            logger.warning(f"Live rainfall fetch failed: {e}")
            # If we have an existing stale cache, return it with warning
            if self._cache is not None:
                stale = dict(self._cache)
                stale["cached"] = True
                stale["is_stale"] = True
                stale["warning"] = f"Unable to refresh live data ({str(e)}). Serving cached telemetry."
                return stale

            # Return graceful offline diagnostic status without failing or making up numbers
            return {
                "status": "offline",
                "is_live": False,
                "cached": False,
                "fetch_timestamp": datetime.now(timezone.utc).isoformat(),
                "provider": provider_info,
                "error_details": {
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "diagnostic": "Backend is offline or remote API is unreachable. No synthetic data was generated."
                },
                "daily_series": [],
                "computed_features": None,
                "disclaimer": (
                    "OFFLINE DEMONSTRATION. External rainfall observation stream is currently unreachable. "
                    "The platform does not fabricate unverified weather data."
                )
            }


rainfall_service = RainfallIngestionService()
