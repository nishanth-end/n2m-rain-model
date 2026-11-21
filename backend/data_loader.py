import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import xgboost as xgb

from backend.config import Settings, settings
from handover_member3.score_cells import load as load_model_assets

class DataLoader:
    """
    Manages loading, validation, and in-memory caching of ML assets,
    static cell data, and historical replay dataset.
    """
    def __init__(self, cfg: Settings = settings):
        self.cfg = cfg
        self.model: Optional[xgb.XGBClassifier] = None
        self.features: Optional[List[str]] = None
        self.threshold_rules: Optional[Dict[str, Any]] = None
        self.static_cells_df: Optional[pd.DataFrame] = None
        self.pixel_map_df: Optional[pd.DataFrame] = None
        self.replay_df: Optional[pd.DataFrame] = None
        self._available_dates: Optional[List[str]] = None
        self._is_initialized: bool = False

    def load_all(self) -> None:
        """Loads and verifies all required data assets into memory."""
        # 1. Verify existence of required files
        required_paths = [
            ("Holdout Model", self.cfg.HOLDOUT_MODEL_PATH),
            ("Features Config", self.cfg.FEATURES_PATH),
            ("Thresholds Config", self.cfg.THRESHOLDS_PATH),
            ("Replay Parquet", self.cfg.PARQUET_PATH),
            ("Static Cells CSV", self.cfg.STATIC_CELLS_PATH),
            ("Pixel Map CSV", self.cfg.PIXEL_MAP_PATH),
        ]
        
        for name, path in required_paths:
            if not Path(path).exists():
                raise FileNotFoundError(f"Required {name} file not found at: {path}")

        # 2. Load model, features, and threshold rules using supplied score_cells.load
        self.model, self.features, self.threshold_rules = load_model_assets(
            model_path=str(self.cfg.HOLDOUT_MODEL_PATH),
            features_path=str(self.cfg.FEATURES_PATH),
            rule_path=str(self.cfg.THRESHOLDS_PATH)
        )

        # 3. Load static cells and pixel map
        self.static_cells_df = pd.read_csv(self.cfg.STATIC_CELLS_PATH)
        self.pixel_map_df = pd.read_csv(self.cfg.PIXEL_MAP_PATH)

        # 4. Load replay parquet
        self.replay_df = pd.read_parquet(self.cfg.PARQUET_PATH)
        self.replay_df["date"] = self.replay_df["date"].astype(str)

        # Verify columns in replay dataset match required features
        missing_feats = [f for f in self.features if f not in self.replay_df.columns]
        if missing_feats:
            raise ValueError(f"Replay dataset is missing expected features: {missing_feats}")

        # Cache available sorted dates
        dates = sorted(self.replay_df["date"].unique().tolist())
        self._available_dates = dates
        self._is_initialized = True

    @property
    def is_initialized(self) -> bool:
        return self._is_initialized

    def get_available_dates(self) -> List[str]:
        if not self._is_initialized:
            self.load_all()
        return list(self._available_dates)

    def get_replay_data_for_date(self, date_str: str) -> pd.DataFrame:
        if not self._is_initialized:
            self.load_all()
        day_df = self.replay_df[self.replay_df["date"] == date_str]
        return day_df

# Global data loader singleton
data_loader = DataLoader()
