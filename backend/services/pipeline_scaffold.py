"""
Experimental Live Rainfall Pipeline Scaffolding
================================================
CRITICAL NOTICE:
This module is isolated research scaffolding and is DISABLED BY DEFAULT.
It is NOT connected to any operational alert mechanism or live warning system.

Data Integrity & Model Compatibility Rationale:
1. The XGBoost susceptibility model was trained specifically on CHIRPS ~5 km gridded daily rainfall.
2. The dynamic feature set requires 8 temporal aggregates per grid cell:
   - rain_1d_mm: rainfall on the target date
   - rain_3d_mm: sum of target date + previous 2 days
   - rain_7d_mm: sum of target date + previous 6 days
   - rain_14d_mm: sum of target date + previous 13 days
   - rain_30d_mm: sum of target date + previous 29 days
   - rain_lag1_mm: rainfall 1 day prior
   - rain_lag2_mm: rainfall 2 days prior
   - rain_lag3_mm: rainfall 3 days prior
3. Spatial mapping:
   - 3,026 Bengaluru cells are mapped to CHIRPS pixel centers via cell_pixel_map.csv.
4. Latency vs. Operational Warning mismatch:
   - CHIRPS is a climate product typically published with a lag of 1-3 days (preliminary) or weeks (final).
   - Real-time weather APIs (e.g. Open-Meteo, IMD, AccuWeather) use different observation methods,
     spatial resolutions, and point interpolations that exhibit systematic distributional shifts
     relative to CHIRPS.
   - Silently feeding uncalibrated real-time data into this model would invalidate its rank calibration.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd

from backend.config import Settings, settings

logger = logging.getLogger(__name__)

class LiveRainfallPipelineScaffold:
    """
    Isolated scaffolding for experimental live rainfall ingestion.
    Strictly isolated from historical replay and disabled by default.
    """
    def __init__(self, cfg: Settings = settings):
        self.cfg = cfg
        self.is_enabled = cfg.ENABLE_EXPERIMENTAL_LIVE_PIPELINE

    def get_pipeline_status(self) -> Dict[str, Any]:
        return {
            "status": "disabled" if not self.is_enabled else "experimental_offline",
            "is_operational": False,
            "connected_to_alerts": False,
            "required_source": "CHIRPS Gridded Daily Rainfall (~5km, UCSB/CHG)",
            "required_features": [
                "rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "rain_14d_mm", "rain_30d_mm",
                "rain_lag1_mm", "rain_lag2_mm", "rain_lag3_mm"
            ],
            "static_mapping_file": "cell_pixel_map.csv",
            "static_features_file": "cells_static.csv",
            "compatibility_warning": (
                "Do not substitute weather sources (e.g. Open-Meteo, IMD points) without "
                "re-evaluating feature distributions against the original training dataset."
            ),
            "safety_rule": "Under no circumstances should this pipeline trigger public alerts."
        }

    def ingest_and_build_features(self, date_str: str, raw_rain_data: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Placeholder execution stub.
        Refuses to run unless explicitly enabled in experimental research mode.
        """
        if not self.is_enabled:
            raise RuntimeError(
                "Live rainfall pipeline is DISABLED by default. "
                "Set ENABLE_EXPERIMENTAL_LIVE_PIPELINE=true in environment to activate experimental research scaffolding. "
                "Never use for operational flood warnings."
            )

        raise NotImplementedError(
            "Live ingestion scaffolding is a research prototype. "
            "Use historical replay mode for verified model evaluation."
        )

live_pipeline_scaffold = LiveRainfallPipelineScaffold()
