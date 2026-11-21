import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from backend.data_loader import data_loader, DataLoader
from handover_member3.score_cells import score_day

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

class ReplayService:
    """
    Handles business logic for historical replay:
    validates date queries, performs model scoring using the original score_cells implementation,
    and computes summary statistics and rank-based classifications.
    """
    def __init__(self, loader: DataLoader = data_loader):
        self.loader = loader
        # Cache for already scored DataFrames by date_str
        self._scored_cache: Dict[str, pd.DataFrame] = {}

    def validate_date_format(self, date_str: str) -> None:
        """Validates that date string is in YYYY-MM-DD format and is a valid calendar date."""
        if not date_str or not DATE_REGEX.match(date_str):
            raise ValueError(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD.")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid calendar date '{date_str}': {str(e)}")

    def get_available_dates(self) -> Dict[str, Any]:
        """Returns sorted, deduplicated historical replay dates."""
        dates = self.loader.get_available_dates()
        return {
            "dates": dates,
            "total_dates": len(dates),
            "min_date": dates[0] if dates else "",
            "max_date": dates[-1] if dates else "",
            "mode": "historical_replay"
        }

    def score_date(self, date_str: str) -> pd.DataFrame:
        """
        Retrieves day data from replay dataset and runs score_day using the holdout model.
        Results are cached in memory for sub-millisecond retrieval on repeat requests.
        """
        self.validate_date_format(date_str)
        
        if date_str in self._scored_cache:
            return self._scored_cache[date_str]

        available_dates = self.loader.get_available_dates()
        if date_str not in available_dates:
            raise KeyError(
                f"Date '{date_str}' not found in historical replay dataset. "
                f"Available range is {available_dates[0]} to {available_dates[-1]}."
            )

        day_data = self.loader.get_replay_data_for_date(date_str)
        n_rows = len(day_data)
        if n_rows == 0:
            raise ValueError(f"No records available for date '{date_str}'.")

        # Reuse original score_day implementation from handover_member3.score_cells
        scored_df = score_day(
            df=day_data,
            model=self.loader.model,
            feats=self.loader.features,
            rule=self.loader.threshold_rules,
            n_ref=self.loader.cfg.N_REFERENCE_CELLS
        )

        # Attach date column (score_day keeps cell_id, ward, lat, lon)
        scored_df["date"] = date_str

        # Ensure correct column ordering and sorting
        scored_df = scored_df.sort_values("rank").reset_index(drop=True)
        self._scored_cache[date_str] = scored_df
        return scored_df

    def get_risk_records(
        self,
        date_str: str,
        level: Optional[str] = None,
        limit: Optional[int] = None,
        is_latest: bool = False
    ) -> Dict[str, Any]:
        """
        Returns structured susceptibility rankings for a date,
        with optional filtering by level (High, Moderate, None) and limit.
        """
        scored_df = self.score_date(date_str)
        filtered_df = scored_df

        if level:
            valid_levels = {"high": "High", "moderate": "Moderate", "none": "None"}
            norm_level = valid_levels.get(level.lower())
            if not norm_level:
                raise ValueError(f"Invalid level filter '{level}'. Allowed values: High, Moderate, None.")
            filtered_df = filtered_df[filtered_df["level"] == norm_level]

        if limit is not None and limit > 0:
            filtered_df = filtered_df.head(limit)

        counts = scored_df["level"].value_counts().to_dict()
        high_cnt = int(counts.get("High", 0))
        mod_cnt = int(counts.get("Moderate", 0))
        none_cnt = int(counts.get("None", 0))

        records = filtered_df.to_dict(orient="records")

        return {
            "date": date_str,
            "total_cells": len(scored_df),
            "high_count": high_cnt,
            "moderate_count": mod_cnt,
            "none_count": none_cnt,
            "mode": "historical_replay",
            "is_latest_replay": is_latest,
            "is_live": False,
            "disclaimer": "EXPERIMENTAL RANKING ONLY. Scores indicate relative susceptibility, NOT flood probabilities.",
            "cells": records
        }

    def get_latest_risk(
        self,
        level: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Returns risk records for the latest available date in historical replay."""
        dates = self.loader.get_available_dates()
        if not dates:
            raise ValueError("No historical replay dates available.")
        latest_date = dates[-1]
        return self.get_risk_records(date_str=latest_date, level=level, limit=limit, is_latest=True)

    def get_summary(self, date_str: str) -> Dict[str, Any]:
        """Returns statistical summary of risk rankings for a given replay date."""
        scored_df = self.score_date(date_str)

        counts = scored_df["level"].value_counts().to_dict()
        high_cnt = int(counts.get("High", 0))
        mod_cnt = int(counts.get("Moderate", 0))
        none_cnt = int(counts.get("None", 0))

        top_cell = scored_df.iloc[0].to_dict() if len(scored_df) > 0 else None
        top_cell_summary = None
        if top_cell:
            top_cell_summary = {
                "cell_id": int(top_cell["cell_id"]),
                "ward": int(top_cell["ward"]),
                "score": float(top_cell["score"]),
                "rank": int(top_cell["rank"]),
                "level": str(top_cell["level"]),
                "lat": float(top_cell["lat"]),
                "lon": float(top_cell["lon"]),
            }

        return {
            "date": date_str,
            "total_cells_scored": len(scored_df),
            "high_count": high_cnt,
            "moderate_count": mod_cnt,
            "none_count": none_cnt,
            "top_ranked_cell": top_cell_summary,
            "average_score": float(scored_df["score"].mean()),
            "min_score": float(scored_df["score"].min()),
            "max_score": float(scored_df["score"].max()),
            "data_mode": "historical_replay",
            "disclaimer": "Experimental relative susceptibility ranking. Scores are not flood probabilities."
        }

replay_service = ReplayService()
