"""tests/test_static.py
Test suite for static features in pipeline/02_static_features.py.
Verifies that:
1. pipeline/02_static_features.py NEVER imports or reads data/events.csv or data/interim/event_cells.csv.
2. data/interim/cells_static.csv exists, has exactly 3,026 rows, and zero null values.
3. Feature distributions fall within physically realistic hydrological and topographic bounds.
"""

import os
import re
import pandas as pd
import pytest

STATIC_CSV = "data/interim/cells_static.csv"
SCRIPT_PATH = "pipeline/02_static_features.py"

def test_static_pipeline_never_reads_events_data():
    """Confirms pipeline/02_static_features.py does not read events.csv or event_cells.csv."""
    assert os.path.exists(SCRIPT_PATH), f"Missing {SCRIPT_PATH}"
    with open(SCRIPT_PATH, "r") as f:
        code = f.read()

    # Must not contain references to events.csv or event_cells.csv
    assert "data/events.csv" not in code, "02_static_features.py must NEVER reference data/events.csv"
    assert "event_cells.csv" not in code, "02_static_features.py must NEVER reference event_cells.csv"
    assert "events_with_cells.csv" not in code, "02_static_features.py must NEVER reference events_with_cells.csv"

def test_static_features_completeness_and_no_nulls():
    """Checks that cells_static.csv has exactly 3,026 rows and 0 null values."""
    assert os.path.exists(STATIC_CSV), f"Missing {STATIC_CSV}. Run pipeline/02_static_features.py first."
    df = pd.read_csv(STATIC_CSV)

    assert len(df) == 3026, f"Expected 3,026 rows, got {len(df)}"
    assert df["cell_id"].nunique() == 3026, "Cell IDs must be unique"

    required_cols = [
        "cell_id", "elev_m", "slope_deg", "flow_acc", "twi", "hand_m",
        "dist_drain_m", "dist_road_m", "dist_lake_m", "lakes_within_1km",
        "impervious_fraction", "cell_area_km2", "is_edge_cell"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"

    null_count = df.isna().sum().sum()
    assert null_count == 0, f"Found {null_count} missing values in static features!"

def test_static_feature_ranges():
    """Verifies that computed features fall within realistic hydrological bounds for Bengaluru."""
    df = pd.read_csv(STATIC_CSV)

    # Elevation: Bengaluru plateau is ~700m to 1000m
    assert df["elev_m"].min() >= 700.0 and df["elev_m"].max() <= 1050.0

    # Slope: degrees >= 0
    assert df["slope_deg"].min() >= 0.0 and df["slope_deg"].max() <= 60.0

    # Impervious fraction between 0.0 and 1.0
    assert df["impervious_fraction"].min() >= 0.0 and df["impervious_fraction"].max() <= 1.0

    # Distances non-negative
    assert (df["dist_drain_m"] >= 0.0).all()
    assert (df["dist_road_m"] >= 0.0).all()
    assert (df["dist_lake_m"] >= 0.0).all()

    # HAND non-negative
    assert (df["hand_m"] >= 0.0).all()

def test_static_cell_ids_match_grid_exactly():
    """Confirms cell_ids in cells_static.csv match cells_grid.csv exactly in count and order."""
    static_df = pd.read_csv(STATIC_CSV)
    grid_df = pd.read_csv("data/interim/cells_grid.csv")

    assert len(static_df) == 3026
    assert (static_df["cell_id"].values == grid_df["cell_id"].values).all(), (
        "cells_static.csv cell_id order does not match cells_grid.csv!"
    )

def test_data_dictionary_covers_all_columns():
    """Confirms every column in cells_static.csv is documented in docs/DATA_DICTIONARY.md."""
    static_df = pd.read_csv(STATIC_CSV)
    dict_path = "docs/DATA_DICTIONARY.md"
    assert os.path.exists(dict_path), f"Missing {dict_path}"

    with open(dict_path, "r") as f:
        dict_text = f.read()

    for col in static_df.columns:
        assert f"`{col}`" in dict_text, f"Column {col} is missing from {dict_path}!"
